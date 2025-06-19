# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
class EntryDashboard(Document):
	pass
@frappe.whitelist()
def case_count(entry_list):
	# batch = frappe.get_all("Batch")
	# for b in batch:
	# 	b1 = frappe.get_doc("Batch",b)
	# return b1.name,b1.check_package,b1.customer
	case_draft = frappe.db.count('Case', {'batch':entry_list,'entry_status': 'Draft'})
	case_pending = frappe.db.count('Case', {'batch':entry_list,'entry_status': 'Pending'})
	case_insuff = frappe.db.count('Case', {'batch':entry_list,'entry_status': 'Insufficient'})
	return case_draft,case_pending,case_insuff

	

    