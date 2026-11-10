from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', _('User')
        ARTIST = 'ARTIST', _('Artist')

    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_premium = models.BooleanField(default=False)
    subscription_date = models.DateTimeField(blank=True, null=True)
    plan = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    notification_preferences = models.JSONField(default=dict)

    # Add email to required fields
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def is_artist(self):
        return self.role == self.Role.ARTIST

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_display_name(self):
        return self.get_full_name() or self.email.split('@')[0]

class UserPreferences(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(max_length=20, default='dark')
    autoplay = models.BooleanField(default=True)
    private_profile = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email}'s preferences"

class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='devices')
    device_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255, unique=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    push_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"{self.device_name} ({self.user.email})"

class PasswordReset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()

class Follower(models.Model):
    user = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    follows = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follows')

    def __str__(self):
        return f"{self.user.email} follows {self.follows.email}"
