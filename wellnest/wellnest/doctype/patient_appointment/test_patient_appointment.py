# Copyright (c) 2026, www.careyogis.com and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from wellnest.wellnest.doctype.patient_appointment.patient_appointment import (
    _get_agora_uid,
    end_consultation,
    start_consultation,
)


class TestPatientAppointment(FrappeTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user_email = "test.teleconsult.lifecycle@example.com"

        if frappe.db.exists("User", cls.test_user_email):
            cls.user = frappe.get_doc("User", cls.test_user_email)
        else:
            cls.user = frappe.get_doc({
                "doctype": "User",
                "email": cls.test_user_email,
                "first_name": "Teleconsult",
                "last_name": "Test",
                "enabled": 1,
                "roles": [
                    {
                        "role": "System Manager",
                    }
                ],
            })
            cls.user.insert(ignore_permissions=True)

        if not any(
            role.role == "System Manager"
            for role in cls.user.roles
        ):
            cls.user.append(
                "roles",
                {
                    "role": "System Manager",
                },
            )
            cls.user.save(ignore_permissions=True)

        if frappe.db.exists(
            "Practitioner",
            {"user_id": cls.test_user_email},
        ):
            cls.practitioner = frappe.get_doc(
                "Practitioner",
                {"user_id": cls.test_user_email},
            )
        else:
            cls.practitioner = frappe.get_doc({
                "doctype": "Practitioner",
                "title": "Dr.",
                "first_name": "Teleconsult",
                "last_name": "Test",
                "mobile": "9999999998",
                "user_id": cls.test_user_email,
            })
            cls.practitioner.insert(ignore_permissions=True)

        if frappe.db.exists(
            "Patient",
            {"full_name": "Teleconsult Test Patient"},
        ):
            cls.patient = frappe.get_doc(
                "Patient",
                {"full_name": "Teleconsult Test Patient"},
            )
        else:
            cls.patient = frappe.get_doc({
                "doctype": "Patient",
                "full_name": "Teleconsult Test Patient",
            })
            cls.patient.insert(ignore_permissions=True)

        frappe.db.commit()

    def setUp(self):
        frappe.set_user(self.test_user_email)

        self.appointment = frappe.get_doc({
            "doctype": "Patient Appointment",
            "patient": self.patient.name,
            "practitioner": self.practitioner.name,
            "scheduled_time": frappe.utils.now_datetime(),
            "consultation_type": "Online",
            "status": "Scheduled",
        })
        self.appointment.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.set_user("Administrator")

        if getattr(self, "appointment", None):
            frappe.db.delete(
                "Patient Appointment",
                {"name": self.appointment.name},
            )

        frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        frappe.set_user("Administrator")

        if getattr(cls, "patient", None):
            frappe.db.delete(
                "Patient",
                {"name": cls.patient.name},
            )

        if getattr(cls, "practitioner", None):
            frappe.db.delete(
                "Practitioner",
                {"name": cls.practitioner.name},
            )

        if getattr(cls, "user", None):
            frappe.db.delete(
                "User",
                {"name": cls.user.name},
            )

        frappe.db.commit()
        super().tearDownClass()

    def test_agora_uid_is_stable(self):
        uid_first = _get_agora_uid(self.test_user_email)
        uid_second = _get_agora_uid(self.test_user_email)

        self.assertEqual(uid_first, uid_second)
        self.assertIsInstance(uid_first, int)
        self.assertGreater(uid_first, 0)

    def test_agora_uid_is_unique_for_different_users(self):
        first_uid = _get_agora_uid(
            "test.teleconsult.lifecycle@example.com"
        )
        second_uid = _get_agora_uid(
            "test.other.practitioner@example.com"
        )

        self.assertNotEqual(first_uid, second_uid)
        self.assertGreaterEqual(first_uid, 1)
        self.assertLessEqual(first_uid, 99999)
        self.assertGreaterEqual(second_uid, 1)
        self.assertLessEqual(second_uid, 99999)

    def test_agora_uid_is_different_for_different_users(self):
        first_uid = _get_agora_uid("doctor.one@example.com")
        second_uid = _get_agora_uid("doctor.two@example.com")

        self.assertNotEqual(first_uid, second_uid)

    def test_start_consultation(self):
        result = start_consultation(self.appointment.name)

        appointment = frappe.get_doc(
            "Patient Appointment",
            self.appointment.name,
        )

        self.assertEqual(
            appointment.status,
            "In-Progress",
        )
        self.assertEqual(
            appointment.video_room_id,
            appointment.name,
        )

        self.assertEqual(
            result["appointment"],
            appointment.name,
        )
        self.assertEqual(
            result["video_room_id"],
            appointment.video_room_id,
        )
        self.assertEqual(
            result["channel_name"],
            appointment.video_room_id,
        )
        self.assertEqual(
            result["uid"],
            _get_agora_uid(self.test_user_email),
        )
        self.assertIn("rtcToken", result)
        self.assertEqual(
            result["status"],
            "In-Progress",
        )

    def test_end_consultation(self):
        start_consultation(self.appointment.name)

        result = end_consultation(self.appointment.name)

        appointment = frappe.get_doc(
            "Patient Appointment",
            self.appointment.name,
        )

        self.assertEqual(
            appointment.status,
            "Completed",
        )
        self.assertEqual(
            result["appointment"],
            appointment.name,
        )
        self.assertEqual(
            result["status"],
            "Completed",
        )

    def test_cannot_start_non_online_appointment(self):
        self.appointment.db_set("consultation_type", "In Clinic")

        with self.assertRaises(frappe.ValidationError):
            start_consultation(self.appointment.name)

    def test_cannot_start_completed_consultation(self):
        self.appointment.db_set(
            "status",
            "Completed",
        )

        with self.assertRaises(frappe.ValidationError):
            start_consultation(self.appointment.name)

    def test_cannot_end_scheduled_consultation(self):
         with self.assertRaises(frappe.ValidationError):
            end_consultation(self.appointment.name)

    def test_practitioner_cannot_start_another_practitioners_appointment(self):
        other_email = "test.other.practitioner@example.com"

        if frappe.db.exists("User", other_email):
            other_user = frappe.get_doc("User", other_email)
        else:
            other_user = frappe.get_doc({
                "doctype": "User",
                "email": other_email,
                "first_name": "Other",
                "last_name": "Practitioner",
                "enabled": 1,
                "roles": [
                    {
                        "role": "System Manager",
                    }
                ],
            })
            other_user.insert(ignore_permissions=True)

        if frappe.db.exists(
            "Practitioner",
            {"user_id": other_email},
        ):
            other_practitioner = frappe.get_doc(
                "Practitioner",
                {"user_id": other_email},
            )
        else:
            other_practitioner = frappe.get_doc({
                "doctype": "Practitioner",
                "title": "Dr.",
                "first_name": "Other",
                "last_name": "Practitioner",
                "mobile": "9999999997",
                "user_id": other_email,
            })
            other_practitioner.insert(ignore_permissions=True)

        try:
            frappe.set_user(other_email)

            with self.assertRaises(frappe.ValidationError):
                start_consultation(self.appointment.name)

        finally:
            frappe.set_user(self.test_user_email)

            frappe.db.delete(
                "Practitioner",
                {"name": other_practitioner.name},
            )
            frappe.db.delete(
                "User",
                {"name": other_user.name},
            )
            frappe.db.commit()
