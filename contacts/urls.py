"""
URL Configuration for the contacts app.
Defines all URL patterns for authentication and contact CRUD operations.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Authentication URLs
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    
    # Contact CRUD URLs
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', views.ContactCreateView.as_view(), name='contact_add'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/edit/', views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    
    # Favorite toggle
    path('contacts/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Informational pages
    path('about/', views.about_view, name='about'),
    path('developer/', views.developer_view, name='developer'),
]
