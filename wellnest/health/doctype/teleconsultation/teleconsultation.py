# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
import requests

from frappe.model.document import Document


class Teleconsultation(Document):

    def after_insert(self):
        """Create a Google Meet automatically for scheduled teleconsultations."""

        if self.consultation_status != "Scheduled":
            return

        try:
            self.create_meeting()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                "Teleconsultation Google Meet Creation Failed",
            )

    def create_meeting(self):
        """Create a standalone Google Meet space and store its details."""

        # Prevent duplicate meeting creation
        if self.meeting_id or self.meeting_url:
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

        # Create a standalone Google Meet space.
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

        meeting_name = meeting.get("name")
        meeting_uri = meeting.get("meetingUri")

        if not meeting_name or not meeting_uri:
            frappe.throw(
                "Google Meet was created but meeting details were not returned."
            )

        self.meeting_provider = "Google Meet"
        self.meeting_id = meeting_name
        self.meeting_url = meeting_uri

        self.save(ignore_permissions=True)

        return {
            "meeting_id": self.meeting_id,
            "meeting_url": self.meeting_url,
        }