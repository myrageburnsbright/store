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
    def create_checkout_session(user, order, success_url: str, cancel_url: str) -> Optional[Dict]:
        """create Stripe Checkout session"""
        try:
            
            if not user.stripe_customer_id:
                customer_id = StripeService.create_customer(user)
                if customer_id:
                    user.stripe_customer_id = customer_id
                    user.save()
            line_items = []
            for item in order.products:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": item.price,
                        "product_data": {
                            "name": item.name,
                            "metadata": {"product_id": item.id},
                        },
                    },
                    "quantity": item.quantity,
                })
    
            session = stripe.checkout.Session.create(
                customer= user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'order_id': order.id,
                    'user_id': user.id,
                }
            )

            return {
                'checkout_url': session.url,
                'session_id': session.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}"),
        
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
    """Основной сервис для работы с платежами"""

    @staticmethod
    def process_successful_payment(payment: Payment) -> bool:
        """Handle successful payment"""
        try:
            payment.mark_as_succeeded()

            # Активируем подписку
            if payment.subscription:
                payment.subscription.activate()
                
                # Записываем в историю
                SubscriptionHistory.objects.create(
                    subscription=payment.subscription,
                    action='activated',
                    description='Subscription activated after successful payment',
                    metadata={'payment_id': payment.id}
                )

            logger.info(f"Payment {payment.id} processed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing successful payment {payment.id}: {e}")
            return False

    @staticmethod
    def process_failed_payment(payment: Payment, reason: str = "") -> bool:
        """Обрабатывает неудачный платеж"""
        try:
            payment.mark_as_failed(reason)

            # Отменяем подписку
            if payment.subscription:
                payment.subscription.cancel()
                
                # Записываем в историю
                SubscriptionHistory.objects.create(
                    subscription=payment.subscription,
                    action='payment_failed',
                    description=f'Payment failed: {reason}',
                    metadata={'payment_id': payment.id}
                )

            logger.info(f"Payment {payment.id} marked as failed")
            return True

        except Exception as e:
            logger.error(f"Error processing failed payment {payment.id}: {e}")
            return False


class WebhookService:
    """Сервис для обработки webhook событий"""

    @staticmethod
    def process_stripe_webhook(event_data: Dict) -> bool:
        """Обрабатывает Stripe webhook"""
        try:
            event_id = event_data.get('id')
            event_type = event_data.get('type')

            # Проверяем, не обрабатывали ли мы уже это событие
            if WebhookEvent.objects.filter(event_id=event_id).exists():
                return True

            # Создаем запись о событии
            webhook_event = WebhookEvent.objects.create(
                provider='stripe',
                event_id=event_id,
                event_type=event_type,
                data=event_data
            )

            # Обрабатываем различные типы событий
            success = False
            
            if event_type == 'checkout.session.completed':
                success = WebhookService._handle_checkout_completed(event_data)                
            elif event_type == 'charge.dispute.created':
                success = WebhookService._handle_dispute_created(event_data)
            else:
                # Неизвестный тип события - помечаем как игнорируемый
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
        """Обрабатывает завершение checkout сессии"""
        try:
            session = event_data['data']['object']
            metadata = session.get('metadata', {})
            payment_id = metadata.get('payment_id')

            if not payment_id:
                logger.warning("No payment_id in checkout session metadata")
                return False

            payment = Payment.objects.get(id=payment_id)
            payment.stripe_payment_intent_id = session.get("payment_intent")
            payment.save()
            if session.mode == 'payment' and session.payment_status == 'paid':
                
                return PaymentService.process_successful_payment(payment)
            else:
                return PaymentService.process_failed_payment(payment)
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for checkout session")
            return False
        except Exception as e:
            logger.error(f"Error handling checkout completed: {e}")
            return False

    @staticmethod
    def _handle_dispute_created(event_data: Dict) -> bool:
        """Обрабатывает создание диспута"""
        try:
            dispute = event_data['data']['object']
            charge_id = dispute.get('charge')

            # Здесь можно добавить логику для обработки диспутов
            # Например, отправка уведомлений администраторам
            
            logger.info(f"Dispute created for charge {charge_id}")
            return True

        except Exception as e:
            logger.error(f"Error handling dispute created: {e}")
            return False