import frappe


@frappe.whitelist()
def log_call_event(event, appointment_id, **kwargs):
    """
    Log a teleconsultation call event emitted by the Flutter Customer app.

    Called in fire-and-forget convention from the client. Always returns success so
    network errors on the client side are never surfaced to the user.

    Supported events (non-exhaustive):
      - patient_entered_waiting_room
      - doctor_initiated_call
      - patient_joined_rtc_channel
      - doctor_joined_rtc_channel
      - call_ended            (includes duration_seconds, doctor_joined)
      - network_quality_degraded (includes quality level)
      - patient_reported_noshow
      - patient_exiting_call

    Events are persisted to the `Event Log` DocType via a low-level
    frappe.db.insert() that bypasses InnoDB transactional overhead and ORM
    hooks. A file-based fallback ensures the call is never disrupted by a
    transient DB failure.

    Field mapping to `Event Log` DocType
    ─────────────────────────────────────
      event             → event_name        (Data, required)
      "Teleconsultation" → event_category   (Select, required)
      appointment_id    → reference_name    (Data)
      "Patient Appt."   → reference_doctype (Link → DocType)
      all other kwargs  → data              (Code/JSON blob)
    """
    import json
    # Strip private kwargs (keys prefixed with "_") then collect all
    # teleconsult-specific metadata into the `data` JSON blob.
    # The Event Log DocType has no individual columns for these fields
    # (duration_seconds, doctor_joined, quality_level, channel, remote_uid …);
    # they all live in the freeform `data` (Code/JSON) field.
    metadata = {k: v for k, v in kwargs.items() if not k.startswith("_")}

    # Row dict aligned 1-to-1 with tabEvent Log columns.
    # `name` is intentionally omitted — the autoname expression
    # "EVLOG-{YYYY}{MM}{DD}-{######}" generates it inside the DB layer.
    row = {
        # ── Event Log DocType fields ──────────────────────────────────────
        "event_category": "Teleconsultation",
        "event_name": event,                         # e.g. "patient_entered_waiting_room"
        "reference_doctype": "Patient Appointment",
        "reference_name": appointment_id,            # appointment ID for traceability
        # All call-specific parameters are serialised into the JSON blob.
        "data": json.dumps(metadata, default=str) if metadata else None,
    }

    try:
        # Low-level insert: no ORM hooks, no validate(), no before_insert(),
        # no InnoDB gap locks from a full document save cycle.
        doc = frappe.get_doc({"doctype": "Event Log", **row})
        doc.set_new_name()
        doc.db_insert()
        # Explicit commit so the row is visible immediately even if the outer
        # request does not commit (e.g., a GET whitelisted endpoint).
        frappe.db.commit()

    except Exception as db_err:  # noqa: BLE001
        # ---------------------------------------------------------------------------
        # Graceful fallback — write to the rotating file log so the event is
        # never silently lost, but the teleconsultation call is never crashed.
        # ---------------------------------------------------------------------------
        _fallback_log(row, db_err)

    return {"status": "ok"}


def _fallback_log(payload: dict, exc: Exception) -> None:
    """
    Write the event payload to the call_events rotating file log.

    This is called only when the primary DB insert fails (e.g., DB overload,
    migration in progress, schema mismatch). It logs both the original event
    and the DB error for post-mortem analysis.
    """
    import json

    logger = frappe.logger("event_log", allow_site=True, max_size=5, file_count=20)
    logger.setLevel(20)  # INFO

    logger.warning(
        json.dumps(
            {
                "fallback": True,
                "db_error": str(exc),
                "payload": payload,
            },
            default=str,
        )
    )
