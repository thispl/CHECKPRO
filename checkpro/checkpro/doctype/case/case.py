# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, add_months, today, add_days, nowdate,formatdate,format_date,getdate
from frappe.model.document import Document
from datetime import datetime
# from teampro.custom import delete_documents

class Case(Document):
	def on_trash(self):
		frappe.errprint(self.billing_status)
		cp = frappe.get_doc("Check Package",self.check_package)
		cp_checks = cp.checks_list
		frappe.errprint(cp_checks)
		for c in cp_checks:
			checks = frappe.get_value(c.check_name,{"case_id":self.name},['name'])
			if checks:
				check = frappe.get_doc(c.check_name,{"name":checks})
				check.delete()

	def validate(self):
		cp = frappe.get_doc("Check Package",self.check_package)
		cp_checks = cp.checks_list
		for c in cp.checks_list:
			checks = frappe.get_all(c.check_name,{"case_id":self.name},['entry_status','name'])
			if not checks:
				for cp_check in cp_checks:
					for unit in range(int(cp_check.units)):
						check =frappe.get_value("Checks",cp_check.check_name,["ce_tat"])
						checks_ty =frappe.get_value("All Checks",cp_check.check_name,["check_name"])
						sh =frappe.get_value("Customer",self.customer,["short_code"])


						from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
						holiday_list_name = 'TEAMPRO 2023 - Checkpro'
						start_date = getdate(today())
						working_days = int(frappe.db.get_value("Check Package",{'name':self.check_package},['package_tat']))
						current_date = start_date
						holiday = []
						while working_days > 0:
							if not is_holiday(holiday_list_name, current_date):
								holiday.append(current_date)
								working_days -= 1
							current_date = add_days(current_date, 1)


							
						create_verify_check = frappe.new_doc(cp_check.check_name)
						create_verify_check.annexture_required=cp_check.annexure
						create_verify_check.ce_tatdays= check
						create_verify_check.check_type= checks_ty
						create_verify_check.customer=self.customer
						create_verify_check.customer_shortcode=sh
						create_verify_check.check_package=self.check_package

						
						create_verify_check.package_tat=frappe.db.get_value("Check Package",{'name':self.check_package},['package_tat'])
						create_verify_check.check_creation_date=getdate(today())
						# create_verify_check.check_completion_date=holiday[-1]
						# create_verify_check.actual_tat= (date_diff(holiday[-1],start_date) + 1)

						create_verify_check.batch=self.batch
						create_verify_check.case_id=self.name
						create_verify_check.name1=self.case_name
						create_verify_check.date_of_birth=self.date_of_birth
						create_verify_check.age=self.age
						create_verify_check.gender=self.case_gender
						create_verify_check.father_name=self.father_name
						create_verify_check.email_id=self.email_id
						create_verify_check.address=self.address
						create_verify_check.client_employee_code=self.client_employee_code
						create_verify_check.contact_number=self.contact
						create_verify_check.date_of_entry=self.date_of_initiating
						create_verify_check.epi_employee_name=self.case_name
						
						create_verify_check.epi_employeee_code=self.client_employee_code
						
						create_verify_check.flags.ignore_mandatory==True
						create_verify_check.save(ignore_permissions=True)
			else:
				for ch in checks:
					frappe.errprint(ch)
					checks = frappe.get_doc(c.check_name,{"name":ch.name})
					checks_ty =frappe.get_value("All Checks",c.check_name,["check_name"])
					checks.update({
						"annexture_required":c.annexure,
						"name1":self.case_name,
						"date_of_birth":self.date_of_birth,
						"gender":self.case_gender,
						"employee_name":self.case_name,
						"epi_employee_name":self.case_name,
						"employee_code":self.client_employee_code,
						"epi_employeee_code":self.client_employee_code,
						"age":self.age,
						"father_name":self.father_name,
						"contact_number":self.contact,
						"address":self.address,
						"entered_by":self.entered_by,
						"allocated_to":self.allocated_to,
						"entry_name" :self.entry_name,
						"employee_no":self.employee_no,
						"entry_designation" :self.entry_designation,
						"execution_by" :self.execution_by,
						"execution_code" :self.exe_designation,
						"execution_name" :self.exe_name,
						"execution_code" :self.employee_code_exe,
						"entered_by_qc":self.entered_by_qc,
						"qc_name":self.qc_name,
						"qc_employee_code":self.qc_employee_code,
						"designation_qc" :self.designation_qc,
						"package_tat":self.package_tat,
						# "execution_by":self.execution_by,
						# "execution_name":self.execution_name,
						# "execution_designation":self.execution_designation,
						# "execution_code":self.execution_code,
						"final_qc_by":self.final_qc_by,
						"final_qc_name":self.final_qc_name,
						"final_qc_designation":self.final_qc_designation,
						"final_qc_employee_code":self.final_qc_employee_code,
						"email_id":self.email_id,
						"verified_by":self.verified_by,
						"designation":self.designation,
						"verified_by_qc":self.verified_by_qc,
						"designation_ver":self.designation_ver,
						"client_employee_code":self.client_employee_code,
						"client" :self.customer,
						"date_of_entry" :self.date_of_initiating,
						"check_type":checks_ty
					
					})
					checks.save(ignore_permissions=True)
					frappe.db.commit()
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
				self.date_of_entry_qc_completed = frappe.utils.today()
				
		if self.execution_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.execution_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.exe_designation = emp[0]
				self.exe_name = emp[1]
				self.employee_code_exe = emp[2]
				self.date_of_execution_allocation=frappe.utils.today()
				
		if self.final_qc_by:
			emp=frappe.db.get_value("Employee",{"user_id":self.final_qc_by},['designation', 'employee_name', 'employee'])
			if emp:
				self.final_qc_designation = emp[0]
				self.final_qc_name = emp[1]
				self.final_qc_employee_code = emp[2]
				self.final_qc_completed_date = frappe.utils.today()
		if case_status == "Entry-QC":
			self.entry_completion_date=frappe.utils.today()
		if case_status == "Execution":
			self.date_of_entry_qc_completed=frappe.utils.today()
		if case_status == "Final-QC":
			self.date_of_execution_completed=frappe.utils.today()
		if case_status == "Generate Report":
			self.final_qc_completed_date=frappe.utils.today()
   
@frappe.whitelist()
def get_checks(check_package):
	check_list = {}
	checks = frappe.get_all('Checks List',{'parent':check_package},['check_name'])
	return checks

@frappe.whitelist()
def get_verify_status(check_package):
	check_list = {}
	checks = frappe.get_all('Checks List',{'parent':check_package},['checks'])
	return checks

@frappe.whitelist()
def check_status(name,check_package):
	check_package = frappe.get_doc('Check Package',{'name' : check_package })
	ch =[]
	for c in check_package.checks_list:
		
		checks = frappe.get_all(c.check_name,{"case_id":name},['entry_status','report_status','verification_status','name'])
		# ch=frappe.get_doc("Case",name)
		# frappe.errprint(checks)
		
		for cs in checks:
			cj=cs["name"]
			sep=cj.split("-")
			if sep[0] == "Employment":
				if cs ["entry_status"] == "Not Applicable":
					ch.append({
						"checks":sep[0],
						"check_id":cs["name"],
						"check_status":cs["entry_status"],
						"verification_status": "Not Applicable",
						"report_status": "Not Applicable",
						"units":"1"
					})
				else:
					ch.append({
						"checks":sep[0],
						"check_id":cs["name"],
						"check_status":cs["entry_status"],
						"verification_status":cs["verification_status"],
						"report_status":cs["report_status"],
						"units":"1"
					})
			else:
				ch.append({
					"checks":sep[0],
					"check_id":cs["name"],
					"check_status":cs["entry_status"],
					"verification_status":cs["verification_status"],
					"report_status":cs["report_status"],
					"units":"1"
				})
			# frappe.errprint(ch)
			# ch.save(ignore_permissions=True)
			# frappe.db.commit()
	return ch
				 
				# dict = {"name":cstatus.name,"status":cstatus.status}
				# frappe.errprint(dict.status)
				
			
				# if all(c == 'Green' for c in cstatus.status):
				#     frappe.errprint("Positive")
				# else:
				#     frappe.errprint("Negative")
			# if all(c == 'Green' for c in check_status):
			#     frappe.errprint("Positive")
			#     result = frappe._dict({
			#         'check':'Verify'+ ' ' +c.checks,
			#         'status':'Green'
			#     })
			# if any(c == 'Red' for c in check_status):
			#     result = frappe._dict({
			#         'check':'Verify'+ ' ' +c.checks,
			#         'status':'Red'
			#     })

			
			

		# check_status = frappe.get_all('Verify '+checks['name'],{'case_id':name},['status'])
		#     if any(c == 'Red' for c in check_status):
		#         result = frappe._dict({
		#         'check': 'Verify'+checks['name'],
		#         'status': 'Red',
		#         })

	# result = {
	#     {'check': 'Verify Employment Check','status':'Red'},
	#         {'check':'Verify Education Check':'Red'}
	#         }
	# }


import frappe

@frappe.whitelist()
def case_status(name, check_package):
	check_package_doc = frappe.get_doc('Check Package', {'name': check_package})
	ch = []

	for c in check_package_doc.checks_list:
		checks = frappe.get_all(c.check_name, filters={"case_id": name}, fields=['check_status', 'name','report_status'])
		for cs in checks:
			cj = cs["name"]
			sep = cj.split("-")

			ch.append({
				"checks": sep[0],
				"check_id": cs["name"],
				"checks_status": cs["check_status"],
				"check_report": cs["report_status"]
			})

	return ch

# @frappe.whitelist()
# def tat_variation():
# 	list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]

# 	for i in list:
# 		doc=frappe.db.get_list(i,["name","check_completion_date","workflow_state","check_creation_date"])
# 		for j in doc:
# 			if j.check_completion_date and j.workflow_state!="Report Completed":
# 				start_date = getdate(today())
# 				date=(date_diff(start_date,j.check_creation_date))
# 				frappe.db.set_value(i,j.name,"tat_variation",date)
# 				if date > 0:
# 					frappe.db.set_value(i,j.name,"tat_monitor","In TAT")
# 				else:
# 					frappe.db.set_value(i,j.name,"tat_monitor","Out TAT")

@frappe.whitelist()
def tat_monitor():
	doc=frappe.db.get_list("Batch",["name","case_completion_date","batch_status"])
	for i in doc:
		# print(i.batch_status)
		if i.case_completion_date and i.batch_status!="Completed":
			start_date = getdate(today())
			print(start_date)
			date=(date_diff(start_date,i.case_completion_date))
			frappe.db.set_value("Batch",i.name,"tat_variation",date)
			if date < 0:
			# 	print(i.tat_monitor)
				frappe.db.set_value("Batch",i.name,"tat__monitor","In TAT")
			else:
				frappe.db.set_value("Batch",i.name,"tat__monitor","Out TAT")

@frappe.whitelist()
def insuff_tat(case_name):
	list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
	mini=[]
	maxi=[]
	for i in list:
		doc=frappe.get_all(i,{"case_id":case_name},["name","insufficiency_date","workflow_state","insuff_closed"])
		for j in doc:
			frappe.errprint(j.name)
			if j.insufficiency_date:
				mini.append(j.insufficiency_date)
			if j.insuff_closed and j.workflow_state!="Insufficient Data":
				maxi.append(j.insuff_closed)
	first_date= min(mini) if mini else None
	frappe.errprint(first_date)
	last_time = max(maxi) if maxi else None
	frappe.errprint(last_time)
	return first_date,last_time
			

