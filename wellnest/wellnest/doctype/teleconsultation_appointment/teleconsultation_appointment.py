# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe
import requests

from frappe.model.document import Document


class TeleconsultationAppointment(Document):

    def after_insert(self):
        """Queue Google Meet creation for scheduled teleconsultation appointments."""

        if self.consultation_status != "Scheduled":
            return

        frappe.enqueue_doc(
            self.doctype,
            self.name,
            "create_video_room",
            queue="short",
            enqueue_after_commit=True,
        )

    def create_video_room(self):
        """Create a Google Meet space and store its details."""

        # Prevent duplicate meeting creation
        if self.video_room_id or self.video_room_url:
            return

        client_id = frappe.conf.get("google_meet_client_id")
        client_secret = frappe.conf.get("google_meet_client_secret")
        refresh_token = frappe.conf.get("google_meet_refresh_token")

        if not client_id or not client_secret or not refresh_token:
            frappe.throw("Google Meet credentials are not configured.")

        # Exchange refresh token for a short-lived access token
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=30,
        )

        if token_response.status_code != 200:
            frappe.log_error(
                token_response.text,
                "Google Meet OAuth Token Error",
            )
            frappe.throw("Unable to authenticate with Google Meet.")

        access_token = token_response.json().get("access_token")

        if not access_token:
            frappe.throw("Google did not return an access token.")

        # Create a standalone Google Meet space
        response = requests.post(
            "https://meet.googleapis.com/v2/spaces",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={},
            timeout=30,
        )

        if response.status_code not in (200, 201):
            frappe.log_error(
                response.text,
                "Google Meet Creation Error",
            )
            frappe.throw("Unable to create Google Meet.")

        meeting = response.json()

        meeting_id = meeting.get("name")
        meeting_url = meeting.get("meetingUri")

        if not meeting_id or not meeting_url:
            frappe.throw(
                "Google Meet was created but meeting details were not returned."
            )

        self.db_set(
            {
                "video_room_id": meeting_id,
                "video_room_url": meeting_url,
            },
            update_modified=True,
        )

        return {
            "video_room_id": meeting_id,
            "video_room_url": meeting_url,
        }