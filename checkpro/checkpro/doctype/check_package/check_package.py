# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CheckPackage(Document):
    pass
    # def validate(self):
    #     check_package = frappe.get_all("Check Package",{"name":self.chec})
    #     frappe.errprint(check_package)

    # def validate(self):
    #     check_package = frappe.get_all("Check Package",{"name":self.check_package})
    #     for ch in check_package:
    #         check = frappe.get_doc("Check Package",ch)
    #         check_list=check.checks_list
    #         for checks in check_list:
    #             un = int(checks.units)
    #             for unit in range(un):
    #                 create_check = frappe.new_doc(checks.checks)
    #                 # check_id = frappe.get_doc("Checks",{"check_name":checks.checks})
    #                 create_check.insert()
    #                 create_check.save(ignore_permissions=True)
    #                 create_check = frappe.new_doc('Verify' + ' ' + checks.checks)
    #                 create_check.insert()
    #                 create_check.save(ignore_permissions=True)

    
