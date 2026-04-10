from django.contrib import admin
from .models import Hotel, Room, Booking

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'city', 'country', 'total_rooms']
    search_fields = ['name', 'city', 'country']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'hotel', 'capacity', 'price_per_night', 'status', 'get_image_preview']
    list_filter = ['room_type', 'status']
    search_fields = ['room_number']
    
    def get_image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />'
        return 'No Image'
    get_image_preview.allow_tags = True
    get_image_preview.short_description = 'Image Preview'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room', 'check_in', 'check_out', 'total_price', 'booking_status']
    list_filter = ['booking_status', 'payment_status']
    search_fields = ['user__username', 'room__room_number']