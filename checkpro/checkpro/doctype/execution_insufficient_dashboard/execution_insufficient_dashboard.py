# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ExecutionInsufficientDashboard(Document):
	pass
@frappe.whitelist()
def completed_count():
	empcount = frappe.db.count("Verify Employment Check",{"status":"Insufficient"})
	edcount = frappe.db.count("Verify Education Check",{"status":"Insufficient"})
	addcount = frappe.db.count("Verify Address Check",{"status":"Insufficient"})
	idcount = frappe.db.count("Verify ID Check",{"status":"Insufficient"})
	cmcount = frappe.db.count("Verify Criminal Record Check",{"status":"Insufficient"})
	fincount = frappe.db.count("Verify Financial History Check",{"status":"Insufficient"})
	fmcount = frappe.db.count("Verify Family History Check",{"status":"Insufficient"})
	refcount = frappe.db.count("Verify Reference Check",{"status":"Insufficient"})
	courtcount = frappe.db.count("Verify Court Record Check",{"status":"Insufficient"})
	gapcount = frappe.db.count("Verify Gap Check",{"status":"Insufficient"})
	matricount = frappe.db.count("Verify Matrimonial Check",{"status":"Insufficient"})
	smcount = frappe.db.count("Verify Social Media Check",{"status":"Insufficient"})
	medcount = frappe.db.count("Verify Medical Test",{"status":"Insufficient"})
	intcount = frappe.db.count("Verify Integrity Check",{"status":"Insufficient"})
	vscount = frappe.db.count("Verify Vendor Screening Check",{"status":"Insufficient"})
	vrcount = frappe.db.count("Verify Vendor Registration",{"status":"Insufficient"})
	dbcount = frappe.db.count("Verify Database Check",{"status":"Insufficient"})
	exitcount = frappe.db.count("Verify Exit Interview Check",{"status":"Insufficient"})



	return empcount,edcount,addcount,idcount,cmcount,fincount,fmcount,refcount,courtcount,gapcount,matricount,smcount,medcount,intcount,vscount,vrcount,dbcount,exitcount


