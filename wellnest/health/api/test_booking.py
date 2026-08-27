import frappe
from wellnest.health.api.booking import get_available_slots
from frappe.utils import today, add_days

def run_tests():
    # Create a mock practitioner
    practitioner = frappe.get_doc({
        "doctype": "Practitioner",
        "title": "Dr",
        "first_name": "Test",
        "last_name": "Doctor",
        "gender": "Male",
        "mobile": "9999999999",
        "is_active": 1,
        "availability_days": [
            {
                "day": "Monday",
                "online_from": "09:00:00",
                "online_to": "11:00:00"
            }
        ]
    })
    try:
        practitioner.insert()
    except Exception:
        practitioner = frappe.get_last_doc("Practitioner", filters={"mobile": "9999999999"})
        
    # Find next monday
    test_date = add_days(today(), 1)
    while frappe.utils.getdate(test_date).strftime("%A") != "Monday":
        test_date = add_days(test_date, 1)

    # Book a time away
    timeaway = frappe.get_doc({
        "doctype": "Practitioner TimeAway",
        "practitioner": practitioner.name,
        "from_date": test_date,
        "to_date": test_date,
        "from_time": "09:30:00",
        "to_time": "10:00:00",
        "status": "Approved"
    })
    timeaway.insert()
    
    # Test available slots without booking
    slots = get_available_slots(practitioner.name, test_date, "Online")
    
    # Expected: 09:00-09:15, 09:15-09:30, (09:30-10:00 blocked), 10:00-10:15, 10:15-10:30, 10:30-10:45, 10:45-11:00
    expected = ["09:00:00", "09:15:00", "10:00:00", "10:15:00", "10:30:00", "10:45:00"]
    assert slots == expected, f"Slots mismatch! Expected {expected}, got {slots}"
    
    print("Test passed! Slots:", slots)
    
    # Cleanup
    timeaway.delete()
    practitioner.delete()
