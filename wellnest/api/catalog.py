import frappe


@frappe.whitelist()
def get_recommended_packages(parent_group: str = "Packages"):
	"""
	Single endpoint replacing 3 sequential calls:
	  1. Item Group  — sub-groups under `parent_group`
	  2. Item        — items belonging to those groups
	  3. Item Price  — standard rate for each item

	Returns a list of dicts ready for the Flutter PackageRepository:
	  [{ plan_name, item_name, item_code, rate, description }, ...]
	"""

	# 1. Sub-groups under the parent group
	groups = frappe.get_all(
		"Item Group",
		filters={"parent_item_group": parent_group},
		fields=["name"],
		ignore_permissions=True,
	)

	if not groups:
		return []

	group_names = [g["name"] for g in groups]

	# 2. Items in those groups
	items = frappe.get_all(
		"Item",
		filters=[["item_group", "in", group_names]],
		fields=["name", "item_name", "description", "item_group"],
		ignore_permissions=True,
	)

	if not items:
		return []

	item_codes = [i["name"] for i in items]

	# 3. Prices for those items (standard price list, fall back to 0)
	prices = frappe.get_all(
		"Item Price",
		filters=[["item_code", "in", item_codes]],
		fields=["item_code", "price_list_rate"],
		ignore_permissions=True,
	)

	price_map = {p["item_code"]: float(p["price_list_rate"] or 0) for p in prices}

	# Assemble
	return [
		{
			"plan_name": item["item_group"],
			"item_name": item["item_name"],
			"item_code": item["name"],
			"rate": price_map.get(item["name"], 0.0),
			"description": item["description"] or "",
		}
		for item in items
	]
