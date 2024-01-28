# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days,getdate
from frappe.utils import date_diff, add_months, today, add_days, nowdate,formatdate,format_date,getdate

class Batch(Document):
	# pass    
	def after_insert(self):
		project_create = frappe.new_doc('Project')        
		project_create.customer = self.customer
		project_create.service = "BCS"
		project_create.project_type = "BCS"
		project_create.expected_value = self.order_value
		project_create.department = "OPS - THIS"
		project_create.project_manager = self.delivery_manager_user
		project_create.customer = self.customer
		project_create.no_of_cases = self.no_of_cases
		project_create.project_name = self.name
		project_create.name = self.name
		project_create.spoc = self.delivery_manager_user
		project_create.expected_start_date = self.expected_start_date
		project_create.expected_end_date = self.expected_end_date
		project_create.pending = self.pending
		project_create.case = self.case
		project_create.comp = self.comp
		project_create.insuff = self.insuff
		project_create.save(ignore_permissions=True)
		# self.project_name = project_create.name
			# frappe.db.set_value('Batch','Project_name', project_name,project_create.name)
	
@frappe.whitelist()
def get_end_date(name,check_package,expected_start_date):
	check_package = frappe.get_value('Check Package', {'name': check_package},["package_tat"])
	if expected_start_date:
		end_date = add_days(expected_start_date,check_package)
		frappe.errprint(end_date)
		return end_date
	
@frappe.whitelist()
def get_check_list(check_package):
	check_list = {}
	checks = frappe.get_all('Checks List', {'parent': check_package}, ['check_name', 'units'])
	return checks

@frappe.whitelist()
def get_cases(batch, no_of_case,expected_start_date,check_package):
	nc = {}
	for unit in range(int(no_of_case)):
		if frappe.db.count("Case", {'batch': batch}) < int(no_of_case):
			nc = frappe.new_doc("Case")
			nc.batch = batch
			nc.no_of_cases = str((unit+1))+"/"+no_of_case
			nc.date_of_initiating = expected_start_date
			value=frappe.db.get_value("Check Package",{"name":check_package},["annexture_required"])
			nc.annexture_required = value

			
			from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
			from frappe.utils import date_diff, add_months, today, add_days, nowdate,formatdate,format_date,getdate
			holiday_list_name = 'TEAMPRO 2023 - Checkpro'
			start_date = getdate(today())
			working_days = frappe.db.get_value("Check Package",{'name':check_package},['package_tat'])
			current_date = start_date
			holiday = []
			if working_days:
				while int(working_days) > 0:
					if not is_holiday(holiday_list_name, current_date):
						holiday.append(current_date)
						working_days -= 1
					current_date = add_days(current_date, 1)


			nc.package_tat=frappe.db.get_value("Check Package",{'name':check_package},['package_tat'])
			# frappe.errprint("nc.package_tat")
			nc.batch_start_date =getdate(today())
			# print(nc.batch_start_date)
			if holiday:
				if len(holiday)>0:
					# nc.case_completion_date=holiday[-1]
					nc.end_date=holiday[-1]
			# nc.actual_tat= (date_diff(holiday[-1],start_date))
			# nc.end_date = expected_end_date
			nc.save(ignore_permissions=True)
			frappe.db.commit()
			frappe.errprint("HII")
			
	return nc 

	# 	if frappe.db.count("Case", {'batch': batch}) < int(no_of_case):
	# 		batch = batch
	# 		from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
	# 		from frappe.utils import date_diff, add_months, today, add_days, nowdate,formatdate,format_date,getdate
	# 		holiday_list_name = 'TEAMPRO 2023 - Checkpro'
	# 		start_date = getdate(today())
	# 		working_days = frappe.db.get_value("Check Package",{'name':check_package},['package_tat'])
	# 		current_date = start_date
	# 		holiday = []
	# 		if working_days:
	# 			while int(working_days) > 0:
	# 				if not is_holiday(holiday_list_name, current_date):
	# 					holiday.append(current_date)
	# 					working_days -= 1
	# 				current_date = add_days(current_date, 1)

	# 		pack_tat = frappe.db.get_value("Check Package",{'name':check_package},['package_tat'])
	# 		if not pack_tat:
	# 			pack_tat = 0
	# 		batch.package_tat = pack_tat
	# 		# frappe.errprint("nc.package_tat")
	# 		batch.batch_start_date =getdate(today())
	# 		# print(nc.batch_start_date)
	# 		if holiday:
	# 			if len(holiday)>0:
	# 				batch.case_completion_date=holiday[-1]
	# 		batch.actual_tat= (date_diff(holiday[-1],start_date))
	# 		# nc.end_date = expected_end_date
	# 		batch.save(ignore_permissions=True)
	# 		frappe.db.commit()
	# 		frappe.errprint("HII")
			
	# return batch 
	

@frappe.whitelist()
def get_checks(check_package):
	check_list = {}
	checks = frappe.get_all('Checks List', {'parent': check_package}, ['check_name', 'units'])
	return checks

@frappe.whitelist()
def check_status(name, check_package):
	check_package = frappe.get_doc('Check Package', {'name': check_package})
	ch = []

	for c in check_package.checks_list:
		checks = frappe.get_all(c.check_name, {"batch": name}, ['entry_status', 'report_status', 'verification_status', 'name'])
		# ch = frappe.get_doc("Case", name)
		# frappe.errprint(checks)

		for cs in checks:
			cj = cs["name"]
			sep = cj.split("-")

			ch.append({
				"checks": sep[0],
				"check_id": cs["name"],
				"check_status": cs["entry_status"],
				"verification_status": cs["verification_status"],
				"report_status": cs["report_status"],
				"units":"1"
			})
			# ch.save(ignore_permissions=True)
		# ch.submit()
		# frappe.db.commit()

	return ch
	ch.save(ignore_permissions=True)


import frappe

@frappe.whitelist()
def case_status(name, check_package):
	check_package_doc = frappe.get_doc('Check Package', {'name': check_package})
	ch = []

	for c in check_package_doc.checks_list:
		checks = frappe.get_all(c.check_name, filters={"batch": name}, fields=['case_id'])
		# frappe.errprint(checks)
		for cs in checks:
			tat=frappe.db.get_value("Case",{'name':cs.case_id},['case_status'])
			cj = cs["case_id"]
			sep = cj.split("-")

			ch.append({				
				"case_id": cs["case_id"],
				"case_status": tat,
			})

		return ch

# @frappe.whitelist()
# def update case():
#     bat = frappe.db.get_all('Batch',{'case':0},['*'])
#     frappe.errprint(bat)


# from frappe.utils import nowdate

# def validate(self):
#     if self.batch_status == "Open" and self.expected_end_date:
#         if self.expected_end_date < datetime.now().date():
#             self.db_set("batch_status", "Overdue", update_modified=False)

from frappe.utils import nowdate
from datetime import datetime

def validate(self):
	if self.batch_status == "Open" and self.expected_end_date:
		if self.expected_end_date < datetime.now().date():
			self.db_set("batch_status", "Overdue", update_modified=False)

@frappe.whitelist()
def tat_monitor():
	doc=frappe.db.get_list("Batch",["name","case_completion_date","batch_status","posting_date","expected_end_date","case_completion_date","batch_start_date","check_package"])
	for i in doc:
		# print(i.check_package)
		# start_date = getdate(today()) 
		frappe.db.set_value("Batch",i.name,"batch_start_date",i.posting_date)
		frappe.db.set_value("Batch",i.name,"case_completion_date",i.expected_end_date)
		date=(date_diff(i.case_completion_date,i.batch_start_date))
		frappe.db.set_value("Batch",i.name,"actual_tat",date)
		package_tat=frappe.db.get_value("Check Package",{'name':i.check_package},['package_tat'])
		if package_tat:
			frappe.db.set_value("Batch",i.name,"package_tat",package_tat)

@frappe.whitelist()
def calculate_end_date(check_package,posting_date):
	from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
	holiday_list_name = 'TEAMPRO 2023 - Checkpro'
	start_date = posting_date
	working_days = int(frappe.db.get_value("Check Package",{'name':check_package},['package_tat']))
	current_date = start_date
	holiday = []
	while working_days > 0:
		if not is_holiday(holiday_list_name, current_date):
			holiday.append(current_date)
			working_days -= 1
		current_date = add_days(current_date, 1)
	return holiday[-1]
		
@frappe.whitelist()
def onload(self):
	doc=frappe.db.get_list("Case",{"batch":self.name}["name","case_status"])
	for i in doc:
		completed = 0
		insuff = 0
		pending = 0
		if i.case_status=="Case Report Completed":
			completed +=1
			frappe.db.set_value("Batch",self.name,"comp",completed)
		if i.case_status=="Draft with Insuff" or i.case_status=="Entry-QC with Insuff" or i.case_status=="Execution with Insuff" or i.case_status=="Final-QC with Insuff" or i.case_status=="Completed with Insuff" or i.case_status=="Generate Report with Insuff":
			insuff +=1
			frappe.db.set_value("Batch",self.name,"insuff",insuff)
		else:
			pending +=1
			frappe.db.set_value("Batch",self.name,"pending",pending)

@frappe.whitelist()
def case_summary(batch_name):
	completed = 0
	insuff = 0
	pending = 0
	cases = frappe.get_all("Case", filters={"batch": batch_name}, fields=["*"])
	for i in cases:
		frappe.errprint(i.case_status)
		if i.case_status == "Case Report Completed":
			frappe.errprint("hi")
			completed += 1
		elif i.case_status in ["Draft with Insuff", "Entry-QC with Insuff", "Execution with Insuff", "Final-QC with Insuff", "Completed with Insuff", "Generate Report with Insuff"]:
			insuff += 1
		else:
			pending += 1
	frappe.errprint(batch_name)
	frappe.errprint(completed)
	frappe.errprint(insuff)
	frappe.errprint(pending)
	return completed,insuff,pending