# Copyright (c) 2023, saru and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import flt
import erpnext



def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Batch ID") + ":Link/Batch:200",
		_("Customer") + ":Link/Customer:200",
		_("Expected Start Date") + ":Date:200",
		_("Expected End Date") + ":Date:200",
		_("Batch Status") + ":Select/:100",
		_("No Of Cases") + ":Int/:100",
		_("#Pending") + ":Int/:100",
		_("#Comp") + ":Int/:100" ,
		_("#Insuff") + ":Int/:100",
		_("#Billing Status") + ":Select/:100"

	]
	return columns



def get_data(filters):
	data = []
	checks = frappe.get_all('Batch', fields=['*'])
	for i in checks:
		sa = frappe.db.count("Case", filters={"batch": i.name, "entry_status": "Pending"})
		sb = frappe.db.count("Case", filters={"batch": i.name, "entry_status": "Completed"})
		sc = frappe.db.count("Case", filters={"batch": i.name, "entry_status": "Insufficient"})

		row = [i.name,i.customer,i.expected_start_date,i.expected_end_date,i.batch_status,i.no_of_cases,sa,sb,sc,i.billing_status]
		data.append(row)
	return data
