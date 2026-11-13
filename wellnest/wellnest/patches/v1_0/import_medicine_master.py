
import csv
from collections import Counter
from pathlib import Path

import frappe


def execute():
    csv_path = Path(__file__).parent / "data" / "medicine_master.csv"

    if not csv_path.is_file():
        frappe.throw(f"Medicine catalogue CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        expected_columns = {
            "generic_name",
            "unit_size",
            "group_name",
        }

        if set(reader.fieldnames or []) != expected_columns:
            frappe.throw(
                f"Unexpected CSV columns: {reader.fieldnames}"
            )

        records = []
        for line_number, row in enumerate(reader, start=2):
            generic_name = (row.get("generic_name") or "").strip()
            unit_size = (row.get("unit_size") or "").strip()
            group_name = (row.get("group_name") or "").strip()

            if not generic_name:
                frappe.throw(
                    f"Missing Generic Name at CSV row {line_number}"
                )

            records.append({
                "generic_name": generic_name,
                "unit_size": unit_size,
                "group_name": group_name,
            })

    if len(records) != 2439:
        frappe.throw(
            f"Expected 2439 medicine records, found {len(records)}"
        )

    def record_key(record):
        return (
            record["generic_name"],
            record["unit_size"],
            record["group_name"],
        )

    source_records = Counter(record_key(row) for row in records)

    existing = frappe.get_all(
        "Medicine Master",
        fields=["generic_name", "unit_size", "group_name"],
        limit_page_length=0,
    )

    existing_records = Counter(
        record_key(row) for row in existing
    )

    if existing_records == source_records:
        frappe.logger("wellnest").info(
            "Medicine Master already matches the 2439-record catalogue. Skipping import."
        )
        print("Medicine Master already matches source catalogue. Import skipped.")
        return

    if existing:
        frappe.throw(
            "Medicine Master contains existing records that do not exactly "
            "match the deployment catalogue. Import stopped without changes."
        )

    for record in records:
        doc = frappe.get_doc({
            "doctype": "Medicine Master",
            **record,
        })
        doc.insert(ignore_permissions=True)

    imported = frappe.get_all(
        "Medicine Master",
        fields=["generic_name", "unit_size", "group_name"],
        limit_page_length=0,
    )

    if Counter(record_key(row) for row in imported) != source_records:
        frappe.throw(
            "Medicine Master verification failed after import."
        )

    print("Medicine Master import successful: 2439 records verified.")
