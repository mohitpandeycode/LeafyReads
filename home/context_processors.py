from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(recipient=request.user).select_related('actor').prefetch_related('content_object')
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        
        return {
            'notifications': notifs[:10],
            'unread_notification_count': unread_count
        }

    return {
        'notifications': [], 
        'unread_notification_count': 0
    }