from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from .models import Room, Booking, Hotel
from .forms import (
    CustomerRegistrationForm, HotelOwnerRegistrationForm, 
    HotelRegistrationForm, UserLoginForm, RoomForm, BookingForm,
    PaymentVerificationForm
)

# Helper functions for role checking
def is_admin(user):
    """Check if user is superuser or staff (Admin only)"""
    return user.is_superuser or user.is_staff

def is_hotel_owner(user):
    """Check if user is a hotel owner (has a hotel profile)"""
    return hasattr(user, 'hotel') and user.hotel is not None

def is_customer(user):
    """Check if user is a regular customer"""
    return user.is_authenticated and not is_admin(user) and not is_hotel_owner(user)

def index(request):
    # Only show featured rooms from approved hotels
    featured_rooms = Room.objects.filter(
        status='available',
        hotel__verification_status='approved'
    )[:6]
    return render(request, 'stay/index.html', {'featured_rooms': featured_rooms})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'❌ Username "{username}" is already taken.')
            return render(request, 'stay/customer_register.html', {'form': form})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f'❌ Email "{email}" is already registered.')
            return render(request, 'stay/customer_register.html', {'form': form})
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '✅ Registration successful! Welcome to InstaStay.')
            return redirect('dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'stay/customer_register.html', {'form': form})

def hotel_owner_register(request):
    if request.method == 'POST':
        form = HotelOwnerRegistrationForm(request.POST)
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'❌ Username "{username}" is already taken.')
            return render(request, 'stay/hotel_owner_register.html', {'form': form})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f'❌ Email "{email}" is already registered.')
            return render(request, 'stay/hotel_owner_register.html', {'form': form})
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '✅ Registration successful! Please register your hotel.')
            return redirect('register_hotel')
    else:
        form = HotelOwnerRegistrationForm()
    return render(request, 'stay/hotel_owner_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user_exists = User.objects.filter(username=username).exists()
            except:
                user_exists = False
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'✅ Welcome back, {username}!')
                
                # Redirect based on user type
                if user.is_superuser or user.is_staff:
                    return redirect('admin_dashboard')
                elif hasattr(user, 'hotel') and user.hotel:
                    return redirect('hotel_dashboard')
                else:
                    return redirect('dashboard')
            else:
                if user_exists:
                    messages.error(request, '❌ Incorrect password. Please try again.')
                else:
                    messages.error(request, '❌ Account not found. Please sign up.')
    else:
        form = UserLoginForm()
    return render(request, 'stay/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')

def rooms(request):
    """Display rooms from VERIFIED hotels only (approved by admin)"""
    # Only show rooms from approved hotels
    room_list = Room.objects.select_related('hotel').filter(
        hotel__verification_status='approved',
        status='available'
    )
    
    # Search parameters
    location = request.GET.get('location', '')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    guests = request.GET.get('guests')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Filter by location
    if location:
        room_list = room_list.filter(
            Q(hotel__city__icontains=location) |
            Q(hotel__country__icontains=location) |
            Q(hotel__address__icontains=location)
        )
    
    # Filter by dates - exclude booked rooms
    if check_in and check_out:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        booked_rooms = Booking.objects.filter(
            Q(check_in__lt=check_out_date) & Q(check_out__gt=check_in_date),
            booking_status__in=['payment_verified', 'confirmed']
        ).values_list('room_id', flat=True)
        room_list = room_list.exclude(id__in=booked_rooms)
    
    # Filter by guests
    if guests:
        room_list = room_list.filter(capacity__gte=int(guests))
    
    # Filter by room type
    if room_type:
        room_list = room_list.filter(room_type=room_type)
    
    # Filter by price
    if min_price:
        room_list = room_list.filter(price_per_night__gte=min_price)
    if max_price:
        room_list = room_list.filter(price_per_night__lte=max_price)
    
    # Get unique locations for dropdown
    locations = set()
    for room in room_list:
        if room.hotel and room.hotel.verification_status == 'approved':
            if room.hotel.city:
                locations.add(room.hotel.city)
            if room.hotel.country:
                locations.add(room.hotel.country)
    
    context = {
        'rooms': room_list,
        'locations': sorted(list(locations)),
        'search_params': {
            'location': location,
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'room_type': room_type,
            'min_price': min_price,
            'max_price': max_price,
        }
    }
    return render(request, 'stay/rooms.html', context)

def room_details(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if hotel is approved
    if room.hotel and room.hotel.verification_status != 'approved':
        messages.warning(request, 'This hotel is currently pending verification and not available for booking.')
        return redirect('rooms')
    
    # Get all booked dates for this room (for calendar)
    booked_bookings = Booking.objects.filter(
        room=room,
        booking_status__in=['payment_verified', 'confirmed']
    ).values('check_in', 'check_out')
    
    # Create list of unavailable dates
    unavailable_dates = []
    for booking in booked_bookings:
        start_date = booking['check_in']
        end_date = booking['check_out']
        current_date = start_date
        while current_date <= end_date:
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
    
    unavailable_dates = sorted(list(set(unavailable_dates)))
    
    similar_rooms = Room.objects.filter(
        room_type=room.room_type,
        status='available',
        hotel__verification_status='approved'
    ).exclude(id=room.id)[:4]
    
    context = {
        'room': room,
        'similar_rooms': similar_rooms,
        'unavailable_dates': json.dumps(unavailable_dates),
    }
    return render(request, 'stay/room_details.html', context)

@login_required
def dashboard(request):
    """Customer dashboard - only accessible by regular customers"""
    if is_admin(request.user):
        messages.info(request, 'You are an admin. Please use the admin dashboard.')
        return redirect('admin_dashboard')
    
    if hasattr(request.user, 'hotel') and request.user.hotel:
        messages.info(request, 'You are a hotel owner. Please use the hotel dashboard.')
        return redirect('hotel_dashboard')
    
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    upcoming_bookings = user_bookings.filter(check_in__gte=timezone.now().date(), booking_status__in=['payment_verified', 'confirmed'])
    past_bookings = user_bookings.filter(check_out__lt=timezone.now().date())
    pending_payments = user_bookings.filter(booking_status='pending_payment')
    
    context = {
        'user_bookings': user_bookings,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'pending_payments': pending_payments,
        'total_bookings': user_bookings.count(),
        'total_spent': user_bookings.filter(payment_status='paid').aggregate(total=Sum('total_price'))['total'] or 0,
    }
    return render(request, 'stay/dashboard.html', context)

@login_required
def booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if room.hotel and room.hotel.verification_status != 'approved':
        messages.error(request, 'This hotel is not yet verified. Bookings are not available.')
        return redirect('rooms')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.total_price = booking.calculate_total_price()
            booking.booking_status = 'pending_payment'
            booking.payment_status = 'pending'
            
            # Check availability
            existing_bookings = Booking.objects.filter(
                room=room,
                check_in__lt=booking.check_out,
                check_out__gt=booking.check_in,
                booking_status__in=['payment_verified', 'confirmed']
            )
            if existing_bookings.exists():
                messages.error(request, 'Room is not available for selected dates.')
                return redirect('rooms')
            
            booking.save()
            booking.nights = (booking.check_out - booking.check_in).days
            
            messages.info(request, f'Please complete payment to confirm your booking for Room {room.room_number}.')
            return redirect('upload_payment', booking_id=booking.id)
    else:
        form = BookingForm(initial={
            'check_in': request.GET.get('check_in', ''),
            'check_out': request.GET.get('check_out', ''),
            'guests': request.GET.get('guests', 1),
        })
    
    return render(request, 'stay/booking.html', {'room': room, 'form': form})

@login_required
def upload_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.booking_status != 'pending_payment':
        messages.error(request, 'Payment has already been processed for this booking.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PaymentVerificationForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            booking.booking_status = 'payment_uploaded'
            form.save()
            messages.success(request, '✅ Payment proof uploaded! Please wait for admin verification.')
            return redirect('dashboard')
    else:
        form = PaymentVerificationForm(instance=booking)
    
    payment_methods_info = {
        'gcash': {
            'name': 'GCash',
            'number': '0917-123-4567',
            'name_on_account': 'InstaStay Payments',
            'instructions': '1. Open GCash app\n2. Click "Send Money"\n3. Enter number: 0917-123-4567\n4. Enter amount and reference: BOOKING-' + str(booking.id) + '\n5. Screenshot the receipt and upload below'
        },
        'paymaya': {
            'name': 'PayMaya',
            'number': '0918-765-4321',
            'name_on_account': 'InstaStay Payments',
            'instructions': '1. Open PayMaya app\n2. Click "Send Money"\n3. Enter number: 0918-765-4321\n4. Enter amount and reference: BOOKING-' + str(booking.id) + '\n5. Screenshot the receipt and upload below'
        },
        'bank_transfer': {
            'name': 'Bank Transfer',
            'bank': 'BPI',
            'account_name': 'InstaStay Hotel Booking System',
            'account_number': '1234-5678-9012',
            'branch': 'Main Office',
            'instructions': '1. Log in to your bank account\n2. Transfer to the account details above\n3. Use reference: BOOKING-' + str(booking.id) + '\n4. Save the transaction receipt and upload below'
        }
    }
    
    payment_info = payment_methods_info.get(booking.payment_method, payment_methods_info['gcash'])
    
    context = {
        'booking': booking,
        'form': form,
        'payment_info': payment_info,
    }
    return render(request, 'stay/upload_payment.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.booking_status in ['pending_payment', 'payment_uploaded', 'payment_verified', 'confirmed']:
        booking.booking_status = 'cancelled'
        booking.payment_status = 'refunded' if booking.payment_status == 'paid' else 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_rooms = Room.objects.count()
    total_bookings = Booking.objects.count()
    total_users = User.objects.count()
    total_customers = User.objects.exclude(is_superuser=True).exclude(hotel__isnull=False).count()
    total_hotel_owners = Hotel.objects.count()
    pending_hotels = Hotel.objects.filter(verification_status='pending').count()
    pending_hotels_list = Hotel.objects.filter(verification_status='pending').order_by('-created_at')[:10]
    pending_payments = Booking.objects.filter(booking_status='payment_uploaded').count()
    total_revenue = Booking.objects.filter(payment_status='paid', booking_status__in=['payment_verified', 'confirmed']).aggregate(total=Sum('total_price'))['total'] or 0
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'total_users': total_users,
        'total_customers': total_customers,
        'total_hotel_owners': total_hotel_owners,
        'pending_hotels': pending_hotels,
        'pending_hotels_list': pending_hotels_list,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'stay/admin_dashboard.html', context)

# ========== ADMIN VERIFICATION VIEWS ==========

@login_required
@user_passes_test(is_admin)
def admin_verify_hotels(request):
    pending_hotels = Hotel.objects.filter(verification_status='pending').order_by('-created_at')
    verified_hotels = Hotel.objects.filter(verification_status='approved').order_by('-created_at')
    rejected_hotels = Hotel.objects.filter(verification_status='rejected').order_by('-created_at')
    
    context = {
        'pending_hotels': pending_hotels,
        'verified_hotels': verified_hotels,
        'rejected_hotels': rejected_hotels,
        'pending_count': pending_hotels.count(),
        'verified_count': verified_hotels.count(),
        'rejected_count': rejected_hotels.count(),
    }
    return render(request, 'stay/admin_verify_hotels.html', context)

@login_required
@user_passes_test(is_admin)
def admin_verify_hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            hotel.verification_status = 'approved'
            hotel.verified_at = timezone.now()
            hotel.verified_by = request.user
            hotel.verification_notes = notes
            hotel.save()
            messages.success(request, f'✅ {hotel.name} has been approved! The hotel can now accept bookings.')
            
        elif action == 'reject':
            hotel.verification_status = 'rejected'
            hotel.verification_notes = notes
            hotel.save()
            messages.warning(request, f'❌ {hotel.name} has been rejected.')
        
        return redirect('admin_verify_hotels')
    
    return render(request, 'stay/admin_verify_hotel_detail.html', {'hotel': hotel})

@login_required
@user_passes_test(is_admin)
def admin_verify_payments(request):
    pending_payments = Booking.objects.filter(booking_status='payment_uploaded').order_by('-created_at')
    verified_payments = Booking.objects.filter(booking_status='payment_verified').order_by('-payment_verified_at')
    
    context = {
        'pending_payments': pending_payments,
        'verified_payments': verified_payments,
        'pending_count': pending_payments.count(),
        'verified_count': verified_payments.count(),
    }
    return render(request, 'stay/admin_verify_payments.html', context)

@login_required
@user_passes_test(is_admin)
def admin_verify_payment_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verify':
            booking.payment_status = 'paid'
            booking.booking_status = 'payment_verified'
            booking.payment_verified_at = timezone.now()
            booking.payment_verified_by = request.user
            booking.save()
            messages.success(request, f'✅ Payment for Booking #{booking.id} has been verified! The booking is now confirmed.')
            
        elif action == 'reject':
            booking.payment_status = 'pending'
            booking.booking_status = 'pending_payment'
            booking.save()
            messages.warning(request, f'❌ Payment for Booking #{booking.id} has been rejected. User needs to resubmit.')
        
        return redirect('admin_verify_payments')
    
    return render(request, 'stay/admin_verify_payment_detail.html', {'booking': booking})

# ========== ADMIN ROOM MANAGEMENT VIEWS ==========

@login_required
@user_passes_test(is_admin)
def manage_rooms(request):
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'stay/manage_rooms.html', {'rooms': rooms})

@login_required
@user_passes_test(is_admin)
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room added successfully.')
            return redirect('manage_rooms')
    else:
        form = RoomForm()
    return render(request, 'stay/add_room.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully.')
            return redirect('manage_rooms')
    else:
        form = RoomForm(instance=room)
    return render(request, 'stay/edit_room.html', {'form': form, 'room': room})

@login_required
@user_passes_test(is_admin)
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted successfully.')
        return redirect('manage_rooms')
    return render(request, 'stay/delete_room.html', {'room': room})

@login_required
@user_passes_test(is_admin)
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.booking_status == 'pending':
        booking.booking_status = 'confirmed'
        booking.save()
        messages.success(request, f'Booking #{booking.id} approved.')
    return redirect('admin_dashboard')

# ========== HOTEL OWNER VIEWS ==========

@login_required
def hotel_dashboard(request):
    if is_admin(request.user):
        messages.info(request, 'You are an admin. Please use the admin dashboard.')
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'hotel') or request.user.hotel is None:
        messages.warning(request, 'Please register your hotel first.')
        return redirect('register_hotel')
    
    hotel = request.user.hotel
    rooms = hotel.rooms.all()
    bookings = Booking.objects.filter(room__hotel=hotel).order_by('-created_at')
    
    if hotel.verification_status != 'approved':
        messages.warning(request, f'Your hotel is {hotel.get_verification_status_display()}. Rooms will not be visible to customers until approved.')
    
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'total_rooms': rooms.count(),
        'total_bookings': bookings.count(),
        'recent_bookings': bookings[:10],
        'available_rooms': rooms.filter(status='available').count(),
        'booked_rooms': rooms.filter(status='booked').count(),
    }
    return render(request, 'stay/hotel_dashboard.html', context)

@login_required
def register_hotel(request):
    if is_admin(request.user):
        messages.warning(request, 'Admins cannot register hotels. Please use the admin panel.')
        return redirect('admin_dashboard')
    
    if hasattr(request.user, 'hotel') and request.user.hotel:
        messages.info(request, 'You already have a registered hotel.')
        return redirect('hotel_dashboard')
    
    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.user = request.user
            hotel.verification_status = 'pending'
            hotel.save()
            messages.success(request, f'{hotel.name} has been registered successfully!')
            messages.info(request, 'Your hotel is pending verification. You will be notified once approved.')
            return redirect('hotel_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = HotelRegistrationForm()
    
    return render(request, 'stay/register_hotel.html', {'form': form})

@login_required
def add_hotel_room(request):
    if is_admin(request.user):
        messages.warning(request, 'Admins cannot add rooms to hotels. Please use the admin panel.')
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'hotel') or request.user.hotel is None:
        messages.warning(request, 'Please register your hotel first.')
        return redirect('register_hotel')
    
    if request.user.hotel.verification_status != 'approved':
        messages.warning(request, 'Your hotel is pending verification. You cannot add rooms until approved.')
        return redirect('hotel_dashboard')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = request.user.hotel
            room.save()
            messages.success(request, f'Room {room.room_number} added successfully!')
            return redirect('hotel_manage_rooms')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RoomForm()
    
    return render(request, 'stay/add_hotel_room.html', {'form': form, 'hotel': request.user.hotel})

@login_required
def hotel_manage_rooms(request):
    if is_admin(request.user):
        messages.info(request, 'You are an admin. Please use the admin dashboard.')
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'hotel') or request.user.hotel is None:
        messages.warning(request, 'Please register your hotel first.')
        return redirect('register_hotel')
    
    rooms = request.user.hotel.rooms.all().order_by('room_number')
    
    context = {
        'rooms': rooms,
        'hotel': request.user.hotel,
    }
    return render(request, 'stay/hotel_manage_rooms.html', context)

@login_required
def hotel_edit_room(request, room_id):
    if is_admin(request.user):
        messages.info(request, 'You are an admin. Please use the admin dashboard.')
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'hotel') or request.user.hotel is None:
        messages.warning(request, 'Please register your hotel first.')
        return redirect('register_hotel')
    
    room = get_object_or_404(Room, id=room_id, hotel=request.user.hotel)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f'Room {room.room_number} updated successfully!')
            return redirect('hotel_manage_rooms')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'stay/hotel_edit_room.html', {'form': form, 'room': room, 'hotel': request.user.hotel})

@login_required
def hotel_delete_room(request, room_id):
    if is_admin(request.user):
        messages.info(request, 'You are an admin. Please use the admin dashboard.')
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'hotel') or request.user.hotel is None:
        messages.warning(request, 'Please register your hotel first.')
        return redirect('register_hotel')
    
    room = get_object_or_404(Room, id=room_id, hotel=request.user.hotel)
    
    if request.method == 'POST':
        room.delete()
        messages.success(request, f'Room {room.room_number} deleted successfully!')
        return redirect('hotel_manage_rooms')
    
    return render(request, 'stay/hotel_delete_room.html', {'room': room, 'hotel': request.user.hotel})

def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})