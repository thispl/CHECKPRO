# Copyright (c) 2023, saru and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.utils import flt
import erpnext
from datetime import datetime
from datetime import datetime, date
from frappe.utils import getdate





def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Batch Number") + ":Link/Batch:200",
		_("Client Name") + ":Link/Customer:200",
		_("TAT Date") + ":Date:200",
		_("Age") + ":Int:200",
		_("Checks") + ":Select/:100",
		_("Cases") + ":Int/:100",
		_("Insuff") + ":Int/:100",
		_("Entry By") + ":Int/:100",
		_("Entry QC") + ":Int/:100",

		_("Education Checks") + ":Int/:100" ,
		_("Employement Checks") + ":Int/:100",
		_("Address Checks") + ":Select/:100",
		_("Court Checks") + ":Int/:100" ,
		_("Reference Checks") + ":Int/:100",
		_("Identity Checks") + ":Int/:100",
		_("Family Checks") + ":Int/:100",
		_("Social Checks") + ":Int/:100",
		_("Final QC") + ":Int/:100",
		_("Completed") + ":Int/:100",

	]
	return columns

def get_data(filters):
	data = []
	batches = frappe.get_all('Batch', filters={
        'batch_status': ['in', ['Open', 'Overdue', 'Insufficient']]
    }, fields=['*'])
	for batch in batches:
		check_package_name = batch.get('check_package')
		
    

		if check_package_name:
			check_package = frappe.get_doc('Check Package', check_package_name)
			package_tat = check_package.get('package_tat')
	insuff = frappe.get_all('Batch', fields=['insuff'])
	
	checks = frappe.get_all('Batch', filters={
        'batch_status': ['in', ['Open', 'Overdue', 'Insufficient']]
    }, fields=['*'])
	for i in checks:
		sa = frappe.db.count("Case", filters={"batch": i.name, "entry_status": "Pending"})
		sb = frappe.db.count("Case", filters={"batch": i.name, "entry_status": "Completed"})
		sc = frappe.db.count("Case", filters={"batch": i.name, "entry_status": "Insufficient"})
		expected_end_date = getdate(i.expected_end_date)
		today = date.today()
		tat_day = (expected_end_date - today).days
		
		cases = frappe.get_all('Case', filters={"batch": i.name}, fields=["entered_by", "entered_by_qc"])
		sg = sum(1 for case in cases if case.entered_by)
		sh = sum(1 for case in cases if case.entered_by_qc)
		new = frappe.get_doc("Batch",i.name)
		
		count = 0
		for j in new.check_list:
			count = j.idx
		
		
		
		row = [i.name, i.customer,i.expected_end_date,tat_day,count,i.no_of_cases,i.insuff,sg,sh]
		query = frappe.db.sql(""" select `tabCheckwise Report`.checks,`tabCheckwise Report`.verification_status,count(`tabCheckwise Report`.verification_status) as count from `tabCheckwise Report` where parent = '%s' group by `tabCheckwise Report`.checks  """%(i.name),as_dict=1)
		education = 0
		employment = 0
		address = 0
		court = 0
		reference = 0
		identity = 0
		family = 0
		social = 0
		for k in query:
			if k.checks == "Education Checks" and k.verification_status == "YTS":
				education = k.count
			if k.checks == "Employment" and k.verification_status == "YTS":
				employment = k.count
			if k.checks == "Address Check" and k.verification_status == "YTS":
				address = k.count
			if k.checks == "Court" and k.verification_status == "YTS":
				court = k.count
			if k.checks == "Reference Check" and k.verification_status == "YTS":
				reference = k.count
			if k.checks == "Identity Aadhar" and k.verification_status == "YTS":
				identity = k.count
			if k.checks == "Family" and k.verification_status == "YTS":
				family = k.count
			if k.checks == "Social Media" and k.verification_status == "YTS":
				social = k.count
		
		row += [education,employment,address,court,reference,identity,family,social]
		education_checks_pending_count = frappe.db.count("Education Checks",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		employment_checks_pending_count = frappe.db.count("Employment",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		
		Address_checks_pending_count = frappe.db.count("Address Check",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		court_pending_count = frappe.db.count("Court",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		
		refer_pending_count = frappe.db.count("Reference Check",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		
		identity_pending_count = frappe.db.count("Identity Aadhar",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		
		family_pending_count = frappe.db.count("Family",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		

		social_pending_count = frappe.db.count("Social Media",
														 filters={"batch": i.name, "workflow_state": "Pending for Verification"})
		
		
		
		var = (education_checks_pending_count + employment_checks_pending_count + Address_checks_pending_count + court_pending_count + refer_pending_count + identity_pending_count + family_pending_count + social_pending_count)
		
		row += [var]

		education_checks_com = frappe.db.count("Education Checks",
														 filters={"batch": i.name, "verification_status": "completed"})
		employment_checks_com = frappe.db.count("Employment",
														 filters={"batch": i.name, "verification_status": "completed"})
		
		Address_checks_com = frappe.db.count("Address Check",
														 filters={"batch": i.name, "verification_status": "completed"})
		court_com = frappe.db.count("Court",
														 filters={"batch": i.name, "verification_status": "completed"})
		
		refer_com = frappe.db.count("Reference Check",
														 filters={"batch": i.name, "verification_status": "completed"})
		
		identity_com = frappe.db.count("Identity Aadhar",
														 filters={"batch": i.name, "verification_status": "completed"})
		
		family_com = frappe.db.count("Family",
														 filters={"batch": i.name, "verification_status": "completed"})
		

		social_com = frappe.db.count("Social Media",
														 filters={"batch": i.name, "verification_status": "completed"})
		
		com = (education_checks_com + employment_checks_com + Address_checks_com + court_com + refer_com + identity_com + family_com + social_com)
		
		row += [com]

		# batches = frappe.get_all('Batch', fields=['name'])
		# for batch in batches:
		# completed_count = frappe.db.count("Education Checks", filters={"parent": batch.name, "verification_status": "Completed"})
		# row += [completed_count]
		data.append(row)

	return data
