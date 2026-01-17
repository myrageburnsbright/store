import stripe
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from typing import Dict, Optional, Tuple
import logging

from .models import Payment, WebhookEvent
from apps.payment.models import Payment, OrderStatusHistory

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()

class StripeService:
    """Сервис для работы с Stripe"""
    
    @staticmethod
    def create_customer(user) -> Optional[str]:
        """Создает клиента в Stripe"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
                metadata={
                    'user_id': user.id,
                    'username': user.username
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return None

    @staticmethod
    def create_checkout_session(user, order, success_url: str, cancel_url: str, coupon_code: Optional[str] = None) -> Optional[Dict]:
        """create Stripe Checkout session"""
        try:

            if not user.stripe_customer_id:
                customer_id = StripeService.create_customer(user)
                if customer_id:
                    user.stripe_customer_id = customer_id
                    user.save()

            line_items = []
            # Use order.items.all() to access OrderItem instances
            for item in order.items.all():
                # Get product name (from variant or product)
                product_name = item.product_name
                if item.variant_name:
                    product_name = f"{item.product_name} - {item.variant_name}"

                # Use total_price which includes all product-level discounts
                # Divide by quantity to get the discounted unit price
                discounted_unit_price = item.total_price / item.quantity
                unit_amount = int(discounted_unit_price * 100)

                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": unit_amount,
                        "product_data": {
                            "name": product_name,
                            "metadata": {
                                "product_id": item.product.id,
                                "variant_id": item.variant.id if item.variant else None,
                            },
                        },
                    },
                    "quantity": item.quantity,
                })

            # Add shipping cost as a line item
            if order.shipping_cost > 0:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(order.shipping_cost * 100),
                        "product_data": {
                            "name": "Shipping Cost",
                        },
                    },
                    "quantity": 1,
                })

            # Session metadata
            session_params = {
                "customer": user.stripe_customer_id,
                "payment_method_types": ['card'],
                "line_items": line_items,
                "mode": 'payment',
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'user_id': user.id,
                }
            }

            # Apply coupon discount if provided
            if coupon_code:
                from .models import Coupon
                try:
                    coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                    if coupon.is_valid:
                        # Calculate discount amount on order total (after product discounts)
                        order_amount = order.subtotal - order.discount_amount
                        discount = coupon.calculate_discount(order_amount)

                        # Create a Stripe coupon for this order
                        stripe_coupon = stripe.Coupon.create(
                            amount_off=int(discount * 100),  # Convert to cents
                            currency='usd',
                            duration='once',
                            name=f"Order {order.order_number} - {coupon_code}"
                        )
                        session_params['discounts'] = [{
                            'coupon': stripe_coupon.id
                        }]
                        # Add coupon info to metadata for webhook processing
                        session_params['metadata']['coupon_code'] = coupon_code
                        session_params['metadata']['coupon_discount'] = str(discount)
                except Coupon.DoesNotExist:
                    pass

            session = stripe.checkout.Session.create(**session_params)

            return {
                'checkout_url': session.url,
                'session_id': session.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}")
            return None

    @staticmethod
    def refund_payment(payment: Payment, amount: Optional[Decimal] = None, reason: str = "") -> bool:
        """Refund through Stripe"""
        try:
            if not payment.stripe_payment_intent_id:
                return False

            refund_data = {
                'payment_intent': payment.stripe_payment_intent_id,
                'metadata': {
                    'payment_id': payment.id,
                    'reason': reason
                }
            }

            if amount:
                refund_data['amount'] = int(amount * 100)

            refund = stripe.Refund.create(**refund_data)
            
            return refund.status == 'succeeded'

        except stripe.error.StripeError as e:
            logger.error(f"Error processing refund: {e}")
            return False

    @staticmethod
    def retrieve_session(session_id: str) -> Optional[Dict]:
        """Get info about session"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'status': session.payment_status,
                'payment_intent': session.payment_intent,
                'customer': session.customer,
                'metadata': session.metadata
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving session: {e}")
            return None


class PaymentService:
    """Main service for payment processing"""

    @staticmethod
    def process_successful_payment(payment: Payment, session_metadata: dict = None) -> bool:
        """Handle successful payment"""
        try:
            payment.mark_as_succeeded()

            # Update order status
            order = payment.order
            if not order.is_paid:
                from django.utils import timezone
                order.is_paid = True
                order.paid_at = timezone.now()
                order.status = 'paid'

                # Apply coupon to order if it was in the session metadata
                if session_metadata and 'coupon_code' in session_metadata and 'coupon_discount' in session_metadata:
                    from .models import Coupon, CouponUsage
                    try:
                        coupon = Coupon.objects.get(code=session_metadata['coupon_code'], is_active=True)
                        if coupon.is_valid:
                            order.coupon = coupon
                            order.coupon_code = coupon.code
                            order.coupon_discount = Decimal(session_metadata['coupon_discount'])

                            # Recalculate total with coupon
                            order_amount = order.subtotal - order.discount_amount
                            order.total = order_amount + order.shipping_cost + order.tax_amount - order.coupon_discount

                            # Increment coupon usage count
                            coupon.used_count += 1
                            coupon.save()

                            # Create coupon usage record
                            CouponUsage.objects.create(
                                coupon=coupon,
                                user=order.user,
                                order=order,
                                discount_amount=order.coupon_discount
                            )
                    except Coupon.DoesNotExist:
                        logger.warning(f"Coupon {session_metadata.get('coupon_code')} not found during payment processing")

                order.save()

                # Add to order status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='paid',
                    notes='Payment completed successfully',
                    changed_by=order.user
                )

            logger.info(f"Payment {payment.id} processed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing successful payment {payment.id}: {e}")
            return False

    @staticmethod
    def process_failed_payment(payment: Payment, reason: str = "") -> bool:
        """Handle failed payment"""
        try:
            payment.mark_as_failed(reason)

            # Update order status to reflect payment failure
            order = payment.order
            if order.status == 'pending':
                order.status = 'cancelled'
                order.save()

                # Add to order status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='cancelled',
                    notes=f'Payment failed: {reason}',
                    changed_by=order.user
                )

            logger.info(f"Payment {payment.id} marked as failed")
            return True

        except Exception as e:
            logger.error(f"Error processing failed payment {payment.id}: {e}")
            return False


class WebhookService:
    """Service for webhook events"""

    @staticmethod
    def process_stripe_webhook(event_data: Dict) -> bool:
        """Handle Stripe webhook"""
        try:
            event_id = event_data.get('id')
            event_type = event_data.get('type')

            # If this event already handled
            if WebhookEvent.objects.filter(event_id=event_id).exists():
                return True

            webhook_event = WebhookEvent.objects.create(
                provider='stripe',
                event_id=event_id,
                event_type=event_type,
                data=event_data
            )

            success = False
            
            if event_type == 'checkout.session.completed':
                success = WebhookService._handle_checkout_completed(event_data)                
            elif event_type == 'charge.dispute.created':
                success = WebhookService._handle_dispute_created(event_data)
            else:
                webhook_event.status = 'ignored'
                webhook_event.save()
                return True

            if success:
                webhook_event.mark_as_processed()
            else:
                webhook_event.mark_as_failed("Processing failed")

            return success

        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}")
            return False

    @staticmethod
    def _handle_checkout_completed(event_data: Dict) -> bool:
        """Handle completed checkout session event"""
        try:
            session = event_data['data']['object']
            session_id = session.get('id')

            if not session_id:
                logger.warning("No session_id in checkout session")
                return False

            # Find payment by stripe_session_id
            try:
                payment = Payment.objects.get(stripe_session_id=session_id)
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for session {session_id}")
                return False

            # Update payment with payment intent ID
            payment.stripe_payment_intent_id = session.get("payment_intent")
            payment.save()

            # Get session metadata (contains coupon info if applied)
            session_metadata = session.get('metadata', {})

            # Process payment based on status
            if session.get('mode') == 'payment' and session.get('payment_status') == 'paid':
                return PaymentService.process_successful_payment(payment, session_metadata)
            else:
                reason = f"Payment status: {session.get('payment_status')}"
                return PaymentService.process_failed_payment(payment, reason)

        except Exception as e:
            logger.error(f"Error handling checkout completed: {e}")
            return False

    @staticmethod
    def _handle_dispute_created(event_data: Dict) -> bool:
        """Handle dipute creation event"""
        try:
            dispute = event_data['data']['object']
            charge_id = dispute.get('charge')

            pass
            
            logger.info(f"Dispute created for charge {charge_id}")
            return True

        except Exception as e:
            logger.error(f"Error handling dispute created: {e}")
            return False