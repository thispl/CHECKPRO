# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Batch(Document):
	pass
	# def validate(self):
	# 	self.entry_count = self.no_of_cases
	
@frappe.whitelist()
def get_checks(check_package):
	check_list = {}
	checks = frappe.get_all('Checks List',{'parent':check_package},['checks'])
	return checks
