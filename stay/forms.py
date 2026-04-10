from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Booking, Hotel

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your address'}), required=False)
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class HotelOwnerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Business email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number'}))
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class HotelRegistrationForm(forms.ModelForm):
    """Form for hotel owners to register their hotel with verification documents"""
    class Meta:
        model = Hotel
        fields = [
            'name', 'address', 'city', 'state', 'country', 'zip_code', 
            'phone', 'email', 'website', 'description', 'amenities', 'image',
            'tin_number', 'business_permit', 'business_permit_number',
            'dti_registration', 'mayors_permit',
            'bank_account_name', 'bank_name', 'bank_account_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hotel Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hotel Phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Hotel Email'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website URL'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your hotel'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Pool, Gym, Restaurant, Parking, Spa, WiFi'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            # Verification Fields
            'tin_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TIN Number (Tax Identification Number)'}),
            'business_permit': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
            'business_permit_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Permit Number'}),
            'dti_registration': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
            'mayors_permit': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
            # Bank Account Fields
            'bank_account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Name'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'capacity', 'price_per_night', 'amenities', 'description', 'image', 'image_url', 'status']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 101, 202, 305'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Number of guests'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Price in USD'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'WiFi, AC, TV, Mini Bar, Room Service'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the room features'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/room-image.jpg'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class BookingForm(forms.ModelForm):
    """Form for creating a booking with payment method selection"""
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'special_requests', 'payment_method']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Number of guests'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError('Check-out date must be after check-in date.')
        return cleaned_data

class PaymentVerificationForm(forms.ModelForm):
    """Form for users to upload payment proof"""
    class Meta:
        model = Booking
        fields = ['payment_reference', 'payment_screenshot']
        widgets = {
            'payment_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GCash/Reference Number'}),
            'payment_screenshot': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }