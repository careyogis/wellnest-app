
import frappe
from frappe.tests.utils import FrappeTestCase


class TestEventLog(FrappeTestCase):
    """Basic sanity tests for the Event Log DocType."""

    def _make_log(self, **kwargs):
        defaults = {
            "doctype": "Event Log",
            "event_category": "Custom",
            "event_name": "Test Event",
        }
        defaults.update(kwargs)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

    def test_insert_creates_record(self):
        doc = self._make_log()
        self.assertTrue(frappe.db.exists("Event Log", doc.name))

    def test_clear_old_logs_removes_stale_records(self):
        from frappe.utils import add_days

        doc = self._make_log(event_name="Stale Event")
        # Backdating via direct SQL to simulate an old record.
        frappe.db.set_value(
            "Event Log",
            doc.name,
            "creation",
            add_days(frappe.utils.now_datetime(), -60),
            update_modified=False,
        )
        frappe.db.commit()

        from wellnest.wellnest.doctype.event_log.event_log import EventLog

        EventLog.clear_old_logs(days=30)

        self.assertFalse(frappe.db.exists("Event Log", doc.name))
