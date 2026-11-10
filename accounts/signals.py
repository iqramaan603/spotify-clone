from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from .models import CustomUser, UserPreferences, Follower

@receiver(post_save, sender=CustomUser)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create UserPreferences when a new user is created."""
    if created:
        UserPreferences.objects.create(user=instance)

@receiver(post_save, sender=Follower)
def notify_follow(sender, instance, created, **kwargs):
    """Send notification when someone follows a user."""
    if created and instance.follows.preferences.email_notifications:
        context = {
            'follower': instance.user,
            'user': instance.follows
        }
        
        # Render email templates
        email_html = render_to_string('account/email/new_follower_email.html', context)
        email_text = render_to_string('account/email/new_follower_email.txt', context)
        
        # Send email notification
        send_mail(
            f'{instance.user.get_display_name()} started following you',
            email_text,
            settings.DEFAULT_FROM_EMAIL,
            [instance.follows.email],
            html_message=email_html,
            fail_silently=True
        )

@receiver(post_save, sender=CustomUser)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Only send email when user is created
        try:
            context = {
                'user': instance,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            }
            
            # Render email templates
            email_html = render_to_string('account/email/welcome_email.html', context)
            email_text = "Welcome to Spotify Clone!"  # Simple text version
            
            # Send email
            send_mail(
                'Welcome to Spotify Clone!',
                email_text,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                html_message=email_html,
                fail_silently=True,  # Set to True to prevent registration issues if email fails
            )
        except Exception as e:
            print(f"Failed to send welcome email: {e}")  # Log the error but don't prevent user creation 