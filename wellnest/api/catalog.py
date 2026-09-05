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

	# 3. Fetch all active prices for these items (Removed limit_page_length)
	prices = frappe.get_all(
		"Item Price",
		filters=[["item_code", "in", item_codes]],
		fields=["item_code", "price_list_rate", "uom", "packing_unit"],
		ignore_permissions=True,
	)

	# 4. Group and find the absolute lowest per-unit price per item
	price_map = {}
	for p in prices:
		item_code = p["item_code"]
		packing_unit = float(p.get("packing_unit") or 1.0)
		price_list_rate = float(p.get("price_list_rate") or 0.0)
		
		# Calculate actual price per single unit
		unit_price = price_list_rate / packing_unit if packing_unit > 0 else price_list_rate

		# If the item isn't tracked yet, or this unit_price is lower than what we have, update it
		if item_code not in price_map or unit_price < price_map[item_code]["price"]:
			price_map[item_code] = {
				"price": int(unit_price),
				"uom": p.get("uom")
			}

	# Assemble response
	return [
		{
			"plan_name": item["item_group"],
			"item_name": item["item_name"],
			"item_code": item["name"],
			"rate": price_map.get(item["name"], {}).get("price", 0),
			"uom": price_map.get(item["name"], {}).get("uom", ""),
			"description": item["description"] or "",
		}
		for item in items
	]
