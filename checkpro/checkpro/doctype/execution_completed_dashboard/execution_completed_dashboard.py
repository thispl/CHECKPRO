# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ExecutionCompletedDashboard(Document):
	pass
@frappe.whitelist()
def completed_count():
	empcount = frappe.db.count("Verify Employment Check",{"execution_status":"Completed"})
	edcount = frappe.db.count("Verify Education Check",{"execution_status":"Completed"})
	addcount = frappe.db.count("Verify Address Check",{"execution_status":"Completed"})
	idcount = frappe.db.count("Verify ID Check",{"execution_status":"Completed"})
	cmcount = frappe.db.count("Verify Criminal Record Check",{"execution_status":"Completed"})
	fincount = frappe.db.count("Verify Financial History Check",{"execution_status":"Completed"})
	fmcount = frappe.db.count("Verify Family History Check",{"execution_status":"Completed"})
	refcount = frappe.db.count("Verify Reference Check",{"execution_status":"Completed"})
	courtcount = frappe.db.count("Verify Court Record Check",{"execution_status":"Completed"})
	gapcount = frappe.db.count("Verify Gap Check",{"execution_status":"Completed"})
	matricount = frappe.db.count("Verify Matrimonial Check",{"execution_status":"Completed"})
	smcount = frappe.db.count("Verify Social Media Check",{"execution_status":"Completed"})
	medcount = frappe.db.count("Verify Medical Test",{"execution_status":"Completed"})
	intcount = frappe.db.count("Verify Integrity Check",{"execution_status":"Completed"})
	vscount = frappe.db.count("Verify Vendor Screening Check",{"execution_status":"Completed"})
	vrcount = frappe.db.count("Verify Vendor Registration",{"execution_status":"Completed"})
	dbcount = frappe.db.count("Verify Database Check",{"execution_status":"Completed"})
	exitcount = frappe.db.count("Verify Exit Interview Check",{"execution_status":"Completed"})



	return empcount,edcount,addcount,idcount,cmcount,fincount,fmcount,refcount,courtcount,gapcount,matricount,smcount,medcount,intcount,vscount,vrcount,dbcount,exitcount


