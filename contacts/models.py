from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    """
    Contact model representing a contact entry in the contact book.
    Each contact is linked to a user via ForeignKey for data isolation.
    """
    
    # Category choices for contact grouping
    CATEGORY_CHOICES = [
        ('Family', 'Family'),
        ('Friends', 'Friends'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    ]
    
    # Foreign key relationship with User model
    # on_delete=models.CASCADE ensures contacts are deleted when user is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    
    # Contact information fields
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    
    # Category/group for organizing contacts
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Other'
    )
    
    # Favorite flag for marking important contacts
    is_favorite = models.BooleanField(default=False)
    
    # Timestamps for tracking creation and updates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for the Contact model."""
        # Default ordering of contacts by name
        ordering = ['name']
        
        # Ensure unique contacts per user (same name and phone combination)
        unique_together = ['user', 'name', 'phone']
        
        # Human-readable singular and plural names
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __str__(self):
        """Return string representation of the contact."""
        return self.name
    
    def get_absolute_url(self):
        """Return the URL for viewing this contact's details."""
        from django.urls import reverse
        return reverse('contact_detail', kwargs={'pk': self.pk})
