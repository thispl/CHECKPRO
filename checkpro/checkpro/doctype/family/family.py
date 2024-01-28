# Copyright (c) 2023, saru and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from teampro.custom import update_case_status

class Family(Document):
	def validate(self):
		case_id = self.case_id
		update_case_status(case_id)
		if self.workflow_state:
			self.check_status=self.workflow_state
		if self.entered_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.entered_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.entry_designation = emp[0]
				self.entry_name = emp[1]
				self.employee_no = emp[2]
				self.entry_allocation_date = frappe.utils.today()
				
		if self.entered_by_qc:
			emp=frappe.db.get_value("Employee",{"user_id":self.entered_by_qc},['designation', 'employee_name', 'employee'])
			if emp:
				self.designation_qc = emp[0]
				self.qc_name = emp[1]
				self.qc_employee_code = emp[2]
				
		if self.execution_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.execution_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.execution_designation = emp[0]
				self.execution_name = emp[1]
				self.execution_code = emp[2]
				
		if self.final_qc_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.final_qc_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.final_qc_designation = emp[0]
				self.final_qc_name = emp[1]
				self.final_qc_employee_code = emp[2]
	
