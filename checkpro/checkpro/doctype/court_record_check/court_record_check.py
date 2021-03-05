# -*- coding: utf-8 -*-
# Copyright (c) 2020, saru and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CourtRecordCheck(Document):
	pass

@frappe.whitelist()
def set_epi(name,case_id):
	frappe.errprint("called")
	vpd = frappe.get_doc("Verify Court Record Check",{"case_id":case_id})
	epi = frappe.get_doc("Court Record Check",{"name":name})
	vpd.update({
		"entry_social_behaviour": epi.social_behaviour
	})
	vpd.save(ignore_permissions=True)
	frappe.db.commit()



