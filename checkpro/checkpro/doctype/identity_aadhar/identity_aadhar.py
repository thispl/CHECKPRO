# Copyright (c) 2023, saru and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from teampro.custom import update_case_status


class IdentityAadhar(Document):
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
		
		if self.custom_execution_initiated_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.custom_execution_initiated_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.custom_designation_exec = emp[0]
				self.custom_name_exe = emp[1]
				self.custom_employee_code_exe  = emp[2]

		if self.final_qc_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.final_qc_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.final_qc_designation = emp[0]
				self.final_qc_name = emp[1]
				self.final_qc_employee_code = emp[2]
	# def validate(self):
	# 	if self.workflow_state == "Entry Pending" and not self.entered_by:
	# 		frappe.throw("Entry Pending - Not Allocated")
	# 	if self.workflow_state == "Entry QC Pending" and not self.entered_by_qc:
	# 		frappe.throw("Entry QC Pending - Not Allocated")
	# 	if self.workflow_state == "Execution Pending" and not self.execution_by:
	# 		frappe.throw("Execution Pending - Not Allocated")
	# 	if self.workflow_state == "Final QC Pending" and not self.final_qc_by:
	# 		frappe.throw("Final QC Pending - Not Allocated")
	# 	if self.workflow_state == "Final QC Pending" and self.report_status =="YTS":
	# 		frappe.throw("Check Report should be either Positive, Negative or Dilemma")
	# 	if self.workflow_state == "Final QC Pending" and self.report_status =="Pending":
	# 		frappe.throw("Check Report should be either Positive, Negative or Dilemma")

@frappe.whitelist()
def aadhar_check_mail(id):
	mail_doc = frappe.get_doc("Identity Aadhar",id)
	attendee = mail_doc.allocated_to
	# for i in mail_doc:
	frappe.sendmail(
	recipients=[attendee],
	subject=( 'Insuff clearance' ),
	message="""
		<p> Insufficient Data is cleared for the check : <b>%s</b> of the case :  <b>%s</b> </p> <br>
		Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
		""" %(mail_doc.name,mail_doc.case_id)
	)