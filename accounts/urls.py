from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),  # Current user's profile
    path('profile/<str:username>/', views.view_profile, name='view_profile'),  # View other user's profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),
    path('follow/<int:user_id>/', views.follow_toggle, name='follow_toggle'),  # Follow/unfollow toggle
] 