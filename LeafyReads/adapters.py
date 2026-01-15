from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # 1. Let Allauth do its normal default thing 
        user = super().populate_user(request, sociallogin, data)
        
        User = get_user_model()
        username_base = user.username
        final_username = username_base
        
        counter = 1
        while User.objects.filter(username=final_username).exists():
            counter += 1
            final_username = f"{username_base}{counter}"
            
        user.username = final_username
        return user