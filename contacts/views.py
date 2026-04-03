from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Contact
from .forms import ContactForm, CustomUserCreationForm, ProfileUpdateForm


# =============================================================================
# Authentication Views
# =============================================================================

def register_view(request):
    """
    Handle user registration.
    If the request is POST and form is valid, create a new user and log them in.
    """
    if request.user.is_authenticated:
        return redirect('contact_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to your Contact Book.')
            return redirect('contact_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Handle user login using Django's built-in AuthenticationForm.
    """
    if request.user.is_authenticated:
        return redirect('contact_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('contact_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


# =============================================================================
# Contact Views - Class-Based Views
# =============================================================================

class HomeView(TemplateView):
    """
    Home page view - displays welcome message and features.
    Accessible to both authenticated and anonymous users.
    """
    template_name = 'home.html'


class ProfileUpdateView(LoginRequiredMixin, View):
    """Allow users to update their own profile details."""

    template_name = "registration/profile.html"

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get("new_password1")
            if new_password:
                user.set_password(new_password)
            user.save()
            if new_password:
                update_session_auth_hash(request, user)
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")

        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form})


class ContactListView(LoginRequiredMixin, ListView):
    """
    Display list of contacts for the logged-in user.
    Features:
    - Pagination (10 contacts per page)
    - Search by name, phone, or email
    - Filter by category
    - Filter favorites only
    """
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Filter contacts by current user and apply search/filter parameters.
        """
        # Get all contacts for the current user
        queryset = Contact.objects.filter(user=self.request.user)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # Favorites filter
        favorites_only = self.request.GET.get('favorites_only', '')
        if favorites_only == 'on':
            queryset = queryset.filter(is_favorite=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['favorites_only'] = self.request.GET.get('favorites_only', '')
        context['categories'] = Contact.CATEGORY_CHOICES
        return context


class ContactDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed view of a single contact.
    """
    model = Contact
    template_name = 'contacts/contact_detail.html'
    context_object_name = 'contact'
    
    def get_queryset(self):
        """
        Ensure users can only view their own contacts.
        """
        return Contact.objects.filter(user=self.request.user)


class ContactCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new contact.
    Automatically associates the contact with the current user.
    """
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contact_list')
    
    def form_valid(self, form):
        """
        Set the user before saving the contact.
        """
        form.instance.user = self.request.user
        messages.success(self.request, f'Contact "{form.instance.name}" added successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Handle invalid form submission.
        """
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing contact.
    Only allows updating contacts owned by the current user.
    """
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contact_list')
    
    def get_queryset(self):
        """
        Ensure users can only update their own contacts.
        """
        return Contact.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        """
        Show success message after update.
        """
        messages.success(self.request, f'Contact "{form.instance.name}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Handle invalid form submission.
        """
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a contact with confirmation.
    Only allows deleting contacts owned by the current user.
    """
    model = Contact
    template_name = 'contacts/contact_confirm_delete.html'
    success_url = reverse_lazy('contact_list')
    
    def get_queryset(self):
        """
        Ensure users can only delete their own contacts.
        """
        return Contact.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Override delete to add custom success message.
        """
        contact = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Contact "{contact.name}" deleted successfully!')
        return response


@require_POST
@login_required
def toggle_favorite(request, pk):
    """
    Toggle the favorite status of a contact.
    Can be used with regular form submission or AJAX.
    """
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    contact.is_favorite = not contact.is_favorite
    contact.save()
    
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'is_favorite': contact.is_favorite
        })
    
    # Regular redirect
    messages.success(
        request,
        f'"{contact.name}" {"added to" if contact.is_favorite else "removed from"} favorites!'
    )
    return redirect('contact_list')

# =============================================================================
# Informational Views
# =============================================================================

def about_view(request):
    """
    Render the About Smart Contact Book page.
    """
    return render(request, 'contacts/about.html')


def developer_view(request):
    """
    Render the Developer Details page.
    """
    return render(request, 'contacts/developer.html')
