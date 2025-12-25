from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(recipient=request.user)
        # Count only unread ones for the red badge
        unread_count = notifs.filter(is_read=False).count()
        
        return {
            'notifications': notifs[:10],
            'unread_notification_count': unread_count
        }
    # Return empty if user is not logged in
    return {
        'notifications': [], 
        'unread_notification_count': 0
    }