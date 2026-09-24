
import frappe
from frappe.model.document import Document


class EventLog(Document):
    """
    Append-only event log DocType for platform-wide observability.

    Registered with Frappe's "Log Settings" mechanism via the
    `clear_old_logs` static method so that site administrators can
    configure automatic purging from:

        Settings → Log Settings → Event Log
    """

    # ------------------------------------------------------------------
    # Frappe Log Settings integration
    # ------------------------------------------------------------------

    @staticmethod
    def clear_old_logs(days: int = 30) -> None:
        """
        Delete Event Log records older than *days* days.

        Frappe's Log Settings scheduler calls this method automatically
        when the DocType is registered in Log Settings. The signature
        ``clear_old_logs(days=30)`` is the expected contract — Frappe
        passes the configured retention window as the ``days`` keyword
        argument.

        Implementation uses a direct SQL DELETE (not ``frappe.delete_doc``)
        to avoid triggering ``on_trash`` hooks and to run efficiently
        against large tables without loading documents into memory.

        Args:
            days: Number of days worth of logs to retain.
                  Records with ``creation`` older than this threshold
                  will be permanently deleted. Defaults to 30.
        """
        from frappe.utils import add_days, now_datetime

        cutoff = add_days(now_datetime(), -days)

        # Batch-delete to avoid a single enormous transaction on busy tables.
        # 10 000 rows per batch keeps the DELETE statement fast and avoids
        # long table-lock windows on MyISAM / Aria deployments.
        BATCH_SIZE = 10_000

        while True:
            deleted = frappe.db.sql(
                """
                DELETE FROM `tabEvent Log`
                WHERE `creation` < %(cutoff)s
                LIMIT %(batch)s
                """,
                {"cutoff": cutoff, "batch": BATCH_SIZE},
            )
            frappe.db.commit()

            # frappe.db.sql returns affected-row count only when the driver
            # exposes it; fall back to assuming we're done when the query
            # completes without error on an empty result.
            rows_deleted = frappe.db.affected_rows() if hasattr(frappe.db, "affected_rows") else 0
            if not rows_deleted:
                break
