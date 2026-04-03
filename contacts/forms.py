import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Contact


class CustomUserCreationForm(UserCreationForm):
    """Registration form with required unique email."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ContactForm(forms.ModelForm):
    """
    ModelForm for creating and updating contacts.
    Includes custom validation for phone numbers and email uniqueness.
    """
    
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number (e.g., +1234567890)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def clean_name(self):
        """
        Validate and clean the name field.
        Ensures name is not empty and has proper format.
        """
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        if len(name) > 100:
            raise forms.ValidationError("Name cannot exceed 100 characters.")
        return name
    
    def clean_phone(self):
        """
        Validate phone number format.
        Accepts various phone formats with optional +, -, (), spaces.
        """
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Remove common separators for validation
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if phone contains only digits and optional + at the start
        if not re.match(r'^\+?\d{7,15}$', cleaned_phone):
            raise forms.ValidationError(
                "Invalid phone number format. Please enter a valid phone number (7-15 digits)."
            )
        
        return phone
    
    def clean_email(self):
        """
        Validate email format and ensure uniqueness per user.
        """
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        
        # Get current user if editing an existing contact
        user = None
        if hasattr(self, 'instance') and self.instance.pk:
            user = self.instance.user
        elif 'user' in self.cleaned_data:
            user = self.cleaned_data['user']
        
        # Check for duplicate email for the same user
        if user:
            contacts = Contact.objects.filter(user=user, email=email)
            if self.instance.pk:
                # Exclude current contact when editing
                contacts = contacts.exclude(pk=self.instance.pk)
            if contacts.exists():
                raise forms.ValidationError(
                    "A contact with this email already exists in your contacts."
                )
        
        return email


class ProfileUpdateForm(forms.ModelForm):
    """Allow logged-in users to update their own profile details."""

    new_password1 = forms.CharField(
        required=False,
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Leave blank to keep current password",
                "autocomplete": "new-password",
            }
        ),
        min_length=8,
    )
    new_password2 = forms.CharField(
        required=False,
        label="Confirm new password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter username",
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email address",
                    "autocomplete": "email",
                }
            ),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 or password2:
            if not password1 or not password2:
                raise forms.ValidationError("Please fill both password fields to update password.")
            if password1 != password2:
                raise forms.ValidationError("The two password fields did not match.")
        return cleaned_data
