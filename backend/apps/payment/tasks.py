from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Payment, WebhookEvent, Order

@shared_task
def cancel_old_pending_orders():
    """Canceling old pending payments"""
    cutoff_date = timezone.now() - timedelta(days=7)
    
    
    old_orders = Order.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['pending']
    )
    
    for order in old_orders:
        order.status = 'cancelled'
    
    return {'cancelled_orders': old_orders}

@shared_task
def cleanup_old_payments():
    """Deleting old payment records"""
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_payments = Payment.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['failed', 'cancelled']
    )
    
    deleted_payments, _ = old_payments.delete()
    
    return {'deleted_payments': deleted_payments}

@shared_task
def cleanup_old_webhook_events():
    """Deleting old webhook events"""
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_events = WebhookEvent.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['processed', 'ignored']
    )
    
    deleted_events, _ = old_events.delete()
    
    return {'deleted_webhook_events': deleted_events}

@shared_task
def retry_failed_webhook_events():
    """Повторная обработка неудачных webhook событий"""
    from .services import WebhookService
    
    # Находим события, которые не удалось обработать в последние 24 часа
    retry_cutoff = timezone.now() - timedelta(hours=24)
    
    failed_events = WebhookEvent.objects.filter(
        status='failed',
        created_at__gte=retry_cutoff
    )[:50]  # Ограничиваем количество для повторной обработки
    
    processed_count = 0
    
    for event in failed_events:
        success = WebhookService.process_stripe_webhook(event.data)
        if success:
            event.mark_as_processed()
            processed_count += 1
    
    return {'reprocessed_events': processed_count}