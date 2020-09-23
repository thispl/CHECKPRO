# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document

class VerifyVendorScreeningCheck(Document):
    pass
@frappe.whitelist()
def edu_check(names,exe,doctype):
    names = json.loads(names)
    for name in names:
        emp = frappe.new_doc("User Permission")
        emp.update({
            "user":exe,
            'allow':doctype,
            "for_value":name
        })
        emp.save(ignore_permissions=True)
        frappe.db.commit()
        check_exec=frappe.get_doc("Verify Vendor Screening Check",name)
        check_exec.update({
            "check_executive":exe
        })
        check_exec.save(ignore_permissions=True)
        frappe.db.commit()