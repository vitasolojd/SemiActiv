print("=" * 50)
print("✅✅✅ stay/urls.py is LOADING! ✅✅✅")
print("=" * 50)

from django.urls import path
from . import views

# ... rest of your urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ==================== PUBLIC URLs ====================
    path('', views.index, name='index'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/hotel-owner/', views.hotel_owner_register, name='hotel_owner_register'),
    path('register-hotel/', views.register_hotel, name='register_hotel'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('rooms/', views.rooms, name='rooms'),
    path('room/<int:room_id>/', views.room_details, name='room_details'),
    path('check-username/', views.check_username, name='check_username'),
    
    # ==================== CUSTOMER URLs ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('booking/<int:room_id>/', views.booking, name='booking'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('upload-payment/<int:booking_id>/', views.upload_payment, name='upload_payment'),
    
    # ==================== ADMIN URLs (only accessible by admins) ====================
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin Room Management
    path('manage-rooms/', views.manage_rooms, name='manage_rooms'),
    path('add-room/', views.add_room, name='add_room'),
    path('edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('approve-booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    
 # Admin Hotel Verification
    path('verify-hotels/', views.admin_verify_hotels, name='admin_verify_hotels'),
    path('verify-hotel/<int:hotel_id>/', views.admin_verify_hotel_detail, name='admin_verify_hotel_detail'),

# Admin Payment Verification
   path('verify-payments/', views.admin_verify_payments, name='admin_verify_payments'),
   path('verify-payment/<int:booking_id>/', views.admin_verify_payment_detail, name='admin_verify_payment_detail'),
    # ==================== HOTEL OWNER URLs (only accessible by hotel owners) ====================
    # Hotel Owner Dashboard
    path('hotel-dashboard/', views.hotel_dashboard, name='hotel_dashboard'),
    
    # Hotel Owner Room Management
    path('hotel/add-room/', views.add_hotel_room, name='add_hotel_room'),
    path('hotel/manage-rooms/', views.hotel_manage_rooms, name='hotel_manage_rooms'),
    path('hotel/edit-room/<int:room_id>/', views.hotel_edit_room, name='hotel_edit_room'),
    path('hotel/delete-room/<int:room_id>/', views.hotel_delete_room, name='hotel_delete_room'),
]