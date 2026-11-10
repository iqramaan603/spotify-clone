from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from datetime import timedelta

from .models import CustomUser, UserPreferences, PasswordReset, Follower
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    UserPreferencesForm,
    PasswordResetRequestForm,
    SetNewPasswordForm,
    CustomPasswordChangeForm
)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'account/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
        preferences_form = UserPreferencesForm(instance=request.user.preferences)
    
    return render(request, 'account/profile.html', {
        'form': form,
        'preferences_form': preferences_form
    })

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            # Generate token and create reset record
            token = get_random_string(64)
            expires_at = timezone.now() + timedelta(hours=24)
            reset_record = PasswordReset.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # Send email
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[token])
            )
            context = {
                'user': user,
                'reset_url': reset_url,
                'expires_at': expires_at
            }
            email_html = render_to_string('account/email/password_reset_email.html', context)
            email_text = render_to_string('account/email/password_reset_email.txt', context)
            
            send_mail(
                'Password Reset Request',
                email_text,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=email_html,
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'account/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    reset_record = get_object_or_404(
        PasswordReset,
        token=token,
        is_used=False,
        expires_at__gt=timezone.now()
    )
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = reset_record.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Mark token as used
            reset_record.is_used = True
            reset_record.save()
            
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'account/password_reset_confirm.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'account/change_password.html', {'form': form})

@login_required
def update_preferences(request):
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=request.user.preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully!')
    return redirect('accounts:profile')

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {
        'user': request.user
    })

@login_required
def follow_toggle(request, user_id):
    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    
    if request.user == user_to_follow:
        messages.error(request, "You can't follow yourself.")
        return redirect('accounts:view_profile', username=user_to_follow.username)
    
    follower, created = Follower.objects.get_or_create(
        user=request.user,
        follows=user_to_follow
    )
    
    if not created:
        follower.delete()
        messages.success(request, f'You have unfollowed {user_to_follow.get_display_name()}.')
    else:
        messages.success(request, f'You are now following {user_to_follow.get_display_name()}.')
    
    return redirect('accounts:view_profile', username=user_to_follow.username)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'account/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def view_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    is_following = request.user.is_authenticated and Follower.objects.filter(
        user=request.user,
        follows=user
    ).exists()
    
    context = {
        'profile_user': user,
        'is_following': is_following,
        'songs': user.songs.all()[:5] if hasattr(user, 'songs') else None,
        'playlists': user.playlists.filter(is_public=True)[:5] if hasattr(user, 'playlists') else None,
        'followers_count': Follower.objects.filter(follows=user).count(),
        'following_count': Follower.objects.filter(user=user).count()
    }
    
    return render(request, 'account/view_profile.html', context)
