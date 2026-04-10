from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Hotel(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hotel')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, help_text="State/Province")
    zip_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_rooms = models.IntegerField(default=0)
    amenities = models.TextField(blank=True, help_text="Pool, Gym, Restaurant, Parking, etc.")
    image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)
    
    # ========== VERIFICATION FIELDS (NEW) ==========
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    tin_number = models.CharField(max_length=50, blank=True, help_text="Tax Identification Number")
    business_permit = models.FileField(upload_to='business_permits/', blank=True, null=True, help_text="Upload Business Permit")
    business_permit_number = models.CharField(max_length=100, blank=True, help_text="Business Permit Number")
    dti_registration = models.FileField(upload_to='dti_registrations/', blank=True, null=True, help_text="DTI/SEC Registration")
    mayors_permit = models.FileField(upload_to='mayors_permits/', blank=True, null=True, help_text="Mayor's Permit")
    
    # Bank Account for Payouts
    bank_account_name = models.CharField(max_length=200, blank=True, help_text="Bank Account Name")
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    
    # Admin Verification Notes
    verification_notes = models.TextField(blank=True, help_text="Admin notes about verification")
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_hotels')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.country} ({self.get_verification_status_display()})"
    
    @property
    def full_address(self):
        parts = [self.address, self.city, self.state, self.country, self.zip_code]
        return ", ".join([p for p in parts if p])
    
    @property
    def is_verified(self):
        return self.verification_status == 'approved'

class Room(models.Model):
    ROOM_TYPES = [
        ('SINGLE', 'Single Room'),
        ('DOUBLE', 'Double Room'),
        ('TWIN', 'Twin Room'),
        ('QUEEN', 'Queen Room'),
        ('KING', 'King Room'),
        ('MASTER', 'Master Bedroom Suite'),
        ('FAMILY', 'Family Room'),
        ('DELUXE', 'Deluxe Suite'),
        ('PRESIDENTIAL', 'Presidential Suite'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.TextField(help_text="WiFi, AC, TV, Mini Bar, etc.")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True, help_text="Upload room image")
    image_url = models.URLField(blank=True, help_text="Or provide image URL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"
    
    @property
    def get_image(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        else:
            return 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=400'
    
    def save(self, *args, **kwargs):
        room_defaults = {
            'SINGLE': {'capacity': 1, 'price': 80},
            'DOUBLE': {'capacity': 2, 'price': 120},
            'TWIN': {'capacity': 2, 'price': 130},
            'QUEEN': {'capacity': 2, 'price': 160},
            'KING': {'capacity': 2, 'price': 200},
            'MASTER': {'capacity': 4, 'price': 350},
            'FAMILY': {'capacity': 6, 'price': 280},
            'DELUXE': {'capacity': 2, 'price': 300},
            'PRESIDENTIAL': {'capacity': 4, 'price': 800},
        }
        if self.room_type in room_defaults:
            if not self.capacity:
                self.capacity = room_defaults[self.room_type]['capacity']
            if not self.price_per_night:
                self.price_per_night = room_defaults[self.room_type]['price']
        super().save(*args, **kwargs)

class Booking(models.Model):
    # Payment Methods (E-wallet options)
    PAYMENT_METHODS = [
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('grabpay', 'GrabPay'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('verified', 'Payment Verified'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    BOOKING_STATUS = [
        ('pending_payment', 'Awaiting Payment'),
        ('payment_uploaded', 'Payment Uploaded - Pending Verification'),
        ('payment_verified', 'Payment Verified'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='gcash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True, help_text="GCash/Reference Number")
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)
    payment_verified_at = models.DateTimeField(null=True, blank=True)
    payment_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending_payment')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.room.room_number}"
    
    def calculate_total_price(self):
        nights = (self.check_out - self.check_in).days
        return nights * self.room.price_per_night
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)