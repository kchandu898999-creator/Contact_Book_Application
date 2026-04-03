"""
Django Admin Configuration for the contacts app.
Provides a customized admin interface for managing contacts.
"""

from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for Contact model.
    Provides comprehensive management capabilities for contacts.
    """
    
    # Fields to display in the contact list
    list_display = [
        'name',
        'phone',
        'email',
        'user',
        'category',
        'is_favorite',
        'created_at',
        'updated_at'
    ]
    
    # Filters available in the right sidebar
    list_filter = [
        'category',
        'is_favorite',
        'created_at',
        'updated_at'
    ]
    
    # Fields that can be searched
    search_fields = [
        'name',
        'phone',
        'email',
        'user__username',
        'user__email'
    ]
    
    # Fields that can be edited directly in the list view
    list_editable = ['is_favorite']
    
    # Prepopulate certain fields (not applicable here, but shown for reference)
    # prepopulated_fields = {'slug': ('name',)}
    
    # Ordering of contacts in the list
    ordering = ['-created_at']
    
    # Date hierarchy for navigation
    date_hierarchy = 'created_at'
    
    # Number of items per page
    list_per_page = 25
    
    # Fields to display when viewing a single contact
    fieldsets = (
        ('Contact Information', {
            'fields': ('user', 'name', 'phone', 'email', 'category')
        }),
        ('Options', {
            'fields': ('is_favorite',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Read-only fields (cannot be edited in admin)
    readonly_fields = ['created_at', 'updated_at']
    
    # Actions available for bulk operations
    actions = ['mark_as_favorite', 'remove_from_favorites']
    
    def mark_as_favorite(self, request, queryset):
        """Bulk action to mark selected contacts as favorites."""
        updated = queryset.update(is_favorite=True)
        self.message_user(
            request,
            f'{updated} contact(s) marked as favorite.',
        )
    mark_as_favorite.short_description = 'Mark selected contacts as favorite'
    
    def remove_from_favorites(self, request, queryset):
        """Bulk action to remove selected contacts from favorites."""
        updated = queryset.update(is_favorite=False)
        self.message_user(
            request,
            f'{updated} contact(s) removed from favorites.',
        )
    remove_from_favorites.short_description = 'Remove selected contacts from favorites'
