from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.validators import validate_email
from .models import CustomUser, UserPreferences

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser.Role.choices)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Using email as username
        if commit:
            user.save()  # preferences are created automatically by the signal
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'profile_picture', 'bio', 'date_of_birth', 'country')

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ('language', 'theme', 'autoplay', 'private_profile', 'email_notifications', 'push_notifications')
        widgets = {
            'language': forms.Select(choices=[('en', 'English'), ('es', 'Spanish')]),
            'theme': forms.Select(choices=[('dark', 'Dark'), ('light', 'Light')]),
        }

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('No user found with this email address.')
        return email

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        min_length=8,
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match.')
            
            # Password strength validation
            if len(password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
            if not any(char.isdigit() for char in password1):
                raise forms.ValidationError('Password must contain at least one number.')
            if not any(char.isupper() for char in password1):
                raise forms.ValidationError('Password must contain at least one uppercase letter.')
            if not any(char.islower() for char in password1):
                raise forms.ValidationError('Password must contain at least one lowercase letter.')

        return cleaned_data

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError('Password must contain at least one number.')
        if not any(char.isupper() for char in password):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')
        return password 