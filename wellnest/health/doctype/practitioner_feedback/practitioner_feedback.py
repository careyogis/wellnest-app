# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PractitionerFeedback(Document):
	def before_save(self):
		if self.ratings:
			total = sum(float(r.rating) for r in self.ratings if r.rating)
			self.average_rating = total / len(self.ratings)
		else:
			self.average_rating = 0.0

	def on_update(self):
		self.update_practitioner_rating()

	def on_trash(self):
		self.update_practitioner_rating()

	def update_practitioner_rating(self):
		if not self.practitioner:
			return

		feedbacks = frappe.get_all(
			"Practitioner Feedback",
			filters={"practitioner": self.practitioner},
			fields=["average_rating"]
		)
		
		total_reviews = len(feedbacks)
		if total_reviews > 0:
			avg_rating = sum(f.average_rating for f in feedbacks) / total_reviews
		else:
			avg_rating = 0.0

		frappe.db.set_value("Practitioner", self.practitioner, {
			"average_rating": avg_rating,
			"total_reviews": total_reviews
		})
