# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from wellnest import config_override

class SystemSettingsExtended(Document):
	def on_update(self):
		# TODO: this is not refreshing in-memory cache
		config_override.refresh_cache_on_save(self)
