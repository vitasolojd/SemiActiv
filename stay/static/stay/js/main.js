// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Calculate total price for booking
function calculateTotal() {
    const checkIn = document.getElementById('id_check_in');
    const checkOut = document.getElementById('id_check_out');
    const pricePerNight = document.getElementById('price_per_night');
    const totalDisplay = document.getElementById('total_price');
    
    if (checkIn && checkOut && pricePerNight && totalDisplay) {
        const start = new Date(checkIn.value);
        const end = new Date(checkOut.value);
        
        if (start && end && end > start) {
            const nights = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
            const total = nights * parseFloat(pricePerNight.value);
            totalDisplay.textContent = '$' + total.toFixed(2);
            document.getElementById('total_amount').value = total.toFixed(2);
        }
    }
}

// Validate booking form
function validateBooking() {
    const checkIn = document.getElementById('id_check_in').value;
    const checkOut = document.getElementById('id_check_out').value;
    const guests = document.getElementById('id_guests').value;
    const today = new Date().toISOString().split('T')[0];
    
    if (!checkIn || !checkOut) {
        alert('Please select check-in and check-out dates');
        return false;
    }
    
    if (checkIn < today) {
        alert('Check-in date cannot be in the past');
        return false;
    }
    
    if (checkOut <= checkIn) {
        alert('Check-out date must be after check-in date');
        return false;
    }
    
    if (guests < 1) {
        alert('Please enter number of guests');
        return false;
    }
    
    return true;
}

// Confirm deletion
function confirmDelete(roomId, roomNumber) {
    if (confirm(`Are you sure you want to delete Room ${roomNumber}?\n\nThis action cannot be undone!`)) {
        document.getElementById(`delete-form-${roomId}`).submit();
    }
}

// Filter rooms by type
function filterRooms() {
    const filter = document.getElementById('room_type_filter').value;
    const rooms = document.querySelectorAll('.room-card');
    
    rooms.forEach(room => {
        if (filter === 'all' || room.dataset.type === filter) {
            room.style.display = 'block';
        } else {
            room.style.display = 'none';
        }
    });
}