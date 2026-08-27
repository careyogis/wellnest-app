# Copyright (c) 2026, www.careyogis.com and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from wellnest.wellnest.doctype.teleconsultation_clinical_record.teleconsultation_clinical_record import (
    get_clinical_record,
    save_clinical_record,
)
from wellnest.wellnest.doctype.vitals.vitals import (
    get_consultation_vitals,
    save_consultation_vitals,
)


class TestTeleconsultationClinicalRecord(FrappeTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user_email = "test.clinical.record@example.com"

        if frappe.db.exists("User", cls.test_user_email):
            cls.user = frappe.get_doc("User", cls.test_user_email)
        else:
            cls.user = frappe.get_doc({
                "doctype": "User",
                "email": cls.test_user_email,
                "first_name": "Clinical",
                "last_name": "Test",
                "enabled": 1,
                "roles": [
                    {
                        "role": "System Manager",
                    }
                ],
            })
            cls.user.insert(ignore_permissions=True)

        # Make sure the test user has System Manager permissions
        # even if the user already existed.
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
                "first_name": "Clinical",
                "last_name": "Test",
                "mobile": "9999999999",
                "user_id": cls.test_user_email,
            })
            cls.practitioner.insert(ignore_permissions=True)

        if frappe.db.exists(
            "Patient",
            {"full_name": "Clinical Test Patient"},
        ):
            cls.patient = frappe.get_doc(
                "Patient",
                {"full_name": "Clinical Test Patient"},
            )
        else:
            cls.patient = frappe.get_doc({
                "doctype": "Patient",
                "full_name": "Clinical Test Patient",
            })
            cls.patient.insert(ignore_permissions=True)

        # Patient Appointment is the actual appointment DocType.
        cls.appointment = frappe.get_doc({
            "doctype": "Patient Appointment",
            "patient": cls.patient.name,
            "practitioner": cls.practitioner.name,
            "scheduled_time": frappe.utils.now_datetime(),
            "consultation_type": "Online",
        })
        cls.appointment.insert(ignore_permissions=True)

        frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        frappe.set_user("Administrator")

        if getattr(cls, "appointment", None):
            record_name = frappe.db.get_value(
                "Teleconsultation Clinical Record",
                {
                    "teleconsultation_appointment": cls.appointment.name,
                },
                "name",
            )

            if record_name:
                frappe.db.delete(
                    "Teleconsultation Clinical Record",
                    {"name": record_name},
                )

            vital_name = frappe.db.get_value(
                "Vitals",
                {
                    "teleconsultation_appointment": cls.appointment.name,
                },
                "name",
            )

            if vital_name:
                frappe.db.delete(
                    "Vitals",
                    {"name": vital_name},
                )

            frappe.db.delete(
                "Patient Appointment",
                {"name": cls.appointment.name},
            )

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

    def setUp(self):
        frappe.set_user(self.test_user_email)

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_clinical_record_create_fetch_update(self):
        data = {
            "consultation_date": frappe.utils.now_datetime(),
            "chief_complaints": [
                {
                    "complaint": "Headache",
                    "duration": "2 days",
                },
                {
                    "complaint": "Fatigue",
                    "duration": "1 week",
                },
            ],
            "history": "Patient reports intermittent headache.",
            "examination": "Patient appears stable.",
            "provisional_diagnosis": "Tension headache",
            "investigations": [
                {
                    "investigation": "CBC",
                },
                {
                    "investigation": "Thyroid Profile",
                },
            ],
            "follow_up_advice": "Follow up after investigations.",
            "diet_advice": "Maintain a balanced diet.",
            "exercise_advice": "Continue regular exercise.",
        }

        result = save_clinical_record(
            appointment=self.appointment.name,
            data=frappe.as_json(data),
        )

        self.assertTrue(result["name"])

        self.assertEqual(
            result["teleconsultation_appointment"],
            self.appointment.name,
        )

        self.assertEqual(
            result["patient"],
            self.patient.name,
        )

        self.assertEqual(
            result["practitioner"],
            self.practitioner.name,
        )

        self.assertEqual(
            len(result["chief_complaints"]),
            2,
        )

        self.assertEqual(
            result["chief_complaints"][0]["complaint"],
            "Headache",
        )

        self.assertEqual(
            result["chief_complaints"][0]["duration"],
            "2 days",
        )

        self.assertEqual(
            len(result["investigations"]),
            2,
        )

        self.assertEqual(
            result["investigations"][0]["investigation"],
            "CBC",
        )

        fetched = get_clinical_record(
            appointment=self.appointment.name,
        )

        self.assertEqual(
            fetched["name"],
            result["name"],
        )

        self.assertEqual(
            fetched["history"],
            "Patient reports intermittent headache.",
        )

        self.assertEqual(
            len(fetched["chief_complaints"]),
            2,
        )

        self.assertEqual(
            len(fetched["investigations"]),
            2,
        )

        update_data = {
            "history": "Updated patient history.",
            "examination": "Updated examination findings.",
            "provisional_diagnosis": "Updated diagnosis",
            "chief_complaints": [
                {
                    "complaint": "Headache",
                    "duration": "5 days",
                },
            ],
            "investigations": [
                {
                    "investigation": "MRI Brain",
                },
            ],
            "follow_up_advice": "Follow up in one week.",
            "diet_advice": "Continue balanced diet.",
            "exercise_advice": "Walk for 30 minutes daily.",
        }

        updated = save_clinical_record(
            appointment=self.appointment.name,
            data=frappe.as_json(update_data),
        )

        self.assertEqual(
            updated["name"],
            result["name"],
        )

        self.assertEqual(
            updated["history"],
            "Updated patient history.",
        )

        self.assertEqual(
            updated["provisional_diagnosis"],
            "Updated diagnosis",
        )

        self.assertEqual(
            len(updated["chief_complaints"]),
            1,
        )

        self.assertEqual(
            updated["chief_complaints"][0]["complaint"],
            "Headache",
        )

        self.assertEqual(
            updated["chief_complaints"][0]["duration"],
            "5 days",
        )

        self.assertEqual(
            len(updated["investigations"]),
            1,
        )

        self.assertEqual(
            updated["investigations"][0]["investigation"],
            "MRI Brain",
        )

    def test_vitals_create_update(self):
        readings = [
            {
                "vital_type": "Weight",
                "unit": "kg",
                "value": "70",
            },
            {
                "vital_type": "Heart Rate",
                "unit": "bpm",
                "value": "72",
            },
        ]

        result = save_consultation_vitals(
            appointment=self.appointment.name,
            readings=frappe.as_json(readings),
        )

        self.assertTrue(result["name"])

        self.assertEqual(
            result["patient"],
            self.patient.name,
        )

        self.assertEqual(
            result["practitioner"],
            self.practitioner.name,
        )

        self.assertEqual(
            result["teleconsultation_appointment"],
            self.appointment.name,
        )

        self.assertEqual(
            len(result["vital_reading"]),
            2,
        )

        self.assertEqual(
            result["vital_reading"][0]["vital_type"],
            "Weight",
        )

        vital = frappe.get_doc(
            "Vitals",
            result["name"],
        )

        self.assertEqual(
            vital.recorded_by,
            self.test_user_email,
        )

        updated_readings = [
            {
                "vital_type": "Weight",
                "unit": "kg",
                "value": "75",
            },
            {
                "vital_type": "BP",
                "unit": "mmHg",
                "value": "120/80",
            },
        ]

        updated = save_consultation_vitals(
            appointment=self.appointment.name,
            readings=frappe.as_json(updated_readings),
        )

        self.assertEqual(
            updated["name"],
            result["name"],
        )

        self.assertEqual(
            len(updated["vital_reading"]),
            2,
        )

        self.assertEqual(
            updated["vital_reading"][0]["value"],
            "75",
        )

        self.assertEqual(
            updated["vital_reading"][1]["vital_type"],
            "BP",
        )

        fetched = get_consultation_vitals(
            appointment=self.appointment.name,
        )

        self.assertEqual(
            fetched["name"],
            result["name"],
        )

        self.assertEqual(
            len(fetched["vital_reading"]),
            2,
        )

        self.assertEqual(
            fetched["vital_reading"][0]["value"],
            "75",
        )