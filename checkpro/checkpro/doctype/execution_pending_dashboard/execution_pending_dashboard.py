# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ExecutionPendingDashboard(Document):
	pass
@frappe.whitelist()
def completed_count():
	empcount = frappe.db.count("Verify Employment Check",{"status":"Pending"})
	edcount = frappe.db.count("Verify Education Check",{"status":"Pending"})
	addcount = frappe.db.count("Verify Address Check",{"status":"Pending"})
	idcount = frappe.db.count("Verify ID Check",{"status":"Pending"})
	cmcount = frappe.db.count("Verify Criminal Record Check",{"status":"Pending"})
	fincount = frappe.db.count("Verify Financial History Check",{"status":"Pending"})
	fmcount = frappe.db.count("Verify Family History Check",{"status":"Pending"})
	refcount = frappe.db.count("Verify Reference Check",{"status":"Pending"})
	courtcount = frappe.db.count("Verify Court Record Check",{"status":"Pending"})
	gapcount = frappe.db.count("Verify Gap Check",{"status":"Pending"})
	matricount = frappe.db.count("Verify Matrimonial Check",{"status":"Pending"})
	smcount = frappe.db.count("Verify Social Media Check",{"status":"Pending"})
	medcount = frappe.db.count("Verify Medical Test",{"status":"Pending"})
	intcount = frappe.db.count("Verify Integrity Check",{"status":"Pending"})
	vscount = frappe.db.count("Verify Vendor Screening Check",{"status":"Pending"})
	vrcount = frappe.db.count("Verify Vendor Registration",{"status":"Pending"})
	dbcount = frappe.db.count("Verify Database Check",{"status":"Pending"})
	exitcount = frappe.db.count("Verify Exit Interview Check",{"status":"Pending"})



	return empcount,edcount,addcount,idcount,cmcount,fincount,fmcount,refcount,courtcount,gapcount,matricount,smcount,medcount,intcount,vscount,vrcount,dbcount,exitcount


