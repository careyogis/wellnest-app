import frappe
from frappe.utils import getdate, get_time, get_datetime
from datetime import datetime, timedelta

@frappe.whitelist(allow_guest=True)
def get_available_slots(practitioner, date, consult_type):
    if consult_type not in ['Online', 'In Clinic', 'Emergency']:
        frappe.throw("Invalid consultation type. Must be 'Online', 'In Clinic', or 'Emergency'.")
        
    date_obj = getdate(date)
    day_name = date_obj.strftime("%A")
    
    # 1. Determine Base Availability
    practitioner_doc = frappe.get_doc("Practitioner", practitioner)
    
    start_time = None
    end_time = None
    
    for slot in practitioner_doc.get("availability_days", []):
        if slot.day == day_name:
            if consult_type == 'Online':
                start_time = slot.online_from
                end_time = slot.online_to
            elif consult_type == 'In Clinic':
                start_time = slot.clinic_from
                end_time = slot.clinic_to
            elif consult_type == 'Emergency':
                start_time = slot.emergency_from
                end_time = slot.emergency_to
            break
            
    if not start_time or not end_time:
        return []
        
    # Generate 15 min slots
    slots = []
    
    # Convert to datetime objects for easy math
    current_dt = datetime.combine(date_obj, get_time(start_time))
    end_dt = datetime.combine(date_obj, get_time(end_time))
    
    now_dt = frappe.utils.now_datetime()
    while current_dt < end_dt:
        slot_end_dt = current_dt + timedelta(minutes=15)
        if slot_end_dt > end_dt:
            break
        
        if current_dt >= now_dt:
            slots.append({
                "from_time": current_dt.time().strftime("%H:%M:%S"),
                "to_time": slot_end_dt.time().strftime("%H:%M:%S")
            })
        current_dt = slot_end_dt

    # 3. Filter Unavailability
    timeaways = frappe.get_all("Practitioner TimeAway", filters={
        "practitioner": practitioner,
        "status": "Approved",
        "from_date": ("<=", date),
        "to_date": (">=", date)
    }, fields=["from_time", "to_time", "from_date", "to_date"])
    
    valid_slots = []
    
    for slot in slots:
        slot_start_dt = datetime.combine(date_obj, get_time(slot["from_time"]))
        slot_end_dt = datetime.combine(date_obj, get_time(slot["to_time"]))
        is_away = False
        
        for away in timeaways:
            away_start_time = get_time(away.from_time) if away.from_date == date_obj else get_time("00:00:00")
            away_end_time = get_time(away.to_time) if away.to_date == date_obj else get_time("23:59:59")
            
            away_start_dt = datetime.combine(date_obj, away_start_time)
            away_end_dt = datetime.combine(date_obj, away_end_time)
            
            # Check overlap
            if not (slot_end_dt <= away_start_dt or slot_start_dt >= away_end_dt):
                is_away = True
                break
                
        if not is_away:
            valid_slots.append(slot)
            
    # 4. Filter Bookings
    bookings = frappe.get_all("Patient Appointment", filters={
        "practitioner": practitioner,
        "scheduled_time": ("between", [f"{date} 00:00:00", f"{date} 23:59:59"]),
        "status": ("not in", ["Cancelled", "No Show"])
    }, fields=["scheduled_time"])
    
    final_slots = []
    
    for slot in valid_slots:
        slot_start_dt = datetime.combine(date_obj, get_time(slot["from_time"]))
        slot_end_dt = datetime.combine(date_obj, get_time(slot["to_time"]))
        is_booked = False
        
        for booking in bookings:
            booking_dt = get_datetime(booking.scheduled_time)
            booking_end_dt = booking_dt + timedelta(minutes=15)
            
            # Check overlap
            if not (slot_end_dt <= booking_dt or slot_start_dt >= booking_end_dt):
                is_booked = True
                break
                
        if not is_booked:
            final_slots.append(slot["from_time"])
            
    return final_slots
