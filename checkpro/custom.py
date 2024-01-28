import frappe
from frappe.utils.csvutils import read_csv_content
from frappe.utils import get_first_day, get_last_day, format_datetime, get_url_to_form
from frappe.utils import cint
from frappe.utils.data import date_diff, now_datetime, nowdate, today, add_days
import datetime
from frappe import _
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from frappe import throw, msgprint
import frappe
from datetime import date
from frappe import throw, _
from frappe.utils import getdate, today
today = date.today()
from frappe.model.document import Document
import datetime 
import frappe,erpnext
from frappe.utils import cint
import json
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
import datetime
from datetime import date,datetime,timedelta
import openpyxl
from openpyxl import Workbook
import openpyxl
import xlrd
import re
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
import pandas as pd
from frappe.utils import formatdate
from frappe.utils import now
from erpnext.setup.utils import get_exchange_rate
from datetime import date
from six import BytesIO, string_types
from frappe.utils import time_diff

@frappe.whitelist()
def create_so_case(case_id):
	doc_name = json.loads(case_id)
	for i in doc_name:
		case=frappe.get_doc("Case",i)
		if case.case_status =="Case Report Completed":
			batch = frappe.db.get_value("Batch",case.batch,['customers_purchase_order'])
			item = frappe.new_doc("Item")
			item.item_code = i
			item.item_name= case.case_name
			item.item_group = "BCS Cases"
			item.item_group_code= "BCS"
			item.stock_uom = "Nos"
			item.qty = "1"
			item.gst_hsn_code = '998521'
			item.is_stock_item = "0"
			item.include_item_in_manufacturing = "0"
			dict_list = []
			dict_list.append(frappe._dict({"item_tax_template":"GST 18% - THIS","tax_category":"Tamil Nadu","valid_from": today()}))
			dict_list.append(frappe._dict({"item_tax_template":"I - GST @ 18% - THIS","tax_category":"Inter State","valid_from": today()}))
			for j in dict_list:
				item.append("taxes", {
					"item_tax_template":j.item_tax_template,
					"tax_category":j.tax_category,
					"valid_from": j.valid_from
					})
			item.append("item_defaults", {
						"company": "TeamPRO HR & IT Services Pvt. Ltd.",
						"buying_cost_center":"Main - THIS",
						"selling_cost_center":"Main - THIS",
						"income_account":"Sales - THIS",
						"expense_account":"Cost of Goods Sold - THIS"
					})
			item.insert()
			item.save(ignore_permissions=True)

			so = frappe.new_doc("Sales Order")
			so.company = "TEAMPRO HR & IT Services Pvt. Ltd."
			so.customer = case.customer
			so.service = "BCS"
			so.order_type = "Sales"
			so.delivery_date = today()  
			so.transaction_date = today() 
			so.po_no = batch
			# so.delivery_manager = batch.delivery_manager
			so.posa_notes:case.case_report
			so.tc_name="Account Details - THIS"
			rate = frappe.db.get_value("Check Package", {"name":case.check_package},["total_sp"])
			
			so.append('items', {
				'item_code': i,
				'item_name':case.case_name,
				'case_batch':case.batch,
				'qty':1,
				'posa_notes':case.case_report,
				'rate':rate,
				})
			case_status=case.case_status
			billing_status = case.billing_status
			
			so.insert()
			so.save(ignore_permissions=True)
			frappe.msgprint("Sales Order Created"+" "+"-<b> "+so.name+"</b>")
			frappe.set_value("Case",i,"billing_status","Billed")
			frappe.set_value("Case",i,"case_status","Case Completed")
			
		else:
			frappe.msgprint("Case Status is not Case Report Completed for this Case-"+" "+i)


@frappe.whitelist()
def delete():
	delete = frappe.db.sql("""delete from `tabAddress Check` where name = "Address Check-10361" """,as_dict = True)

@frappe.whitelist()
def update_query():
	frappe.db.sql("""update `tabFamily` set workflow_state = 'Drop' where workflow_state = 'Dropped'""")
	# frappe.db.sql("""update `tabReference Check` set workflow_state = 'Report Completed' where name = 'Reference Check-032'""")
# 	frappe.db.sql("""update `tabReference Check` set workflow_state = 'Report Completed' where name = 'Reference Check-031'""")

@frappe.whitelist()
def create_so(case_id):
	case=frappe.get_doc("Case",case_id)
	batch = frappe.db.get_value("Batch",case.batch,['customers_purchase_order'])
	item = frappe.new_doc("Item")
	item.item_code = case_id
	item.item_name= case.case_name
	item.item_group = "BCS Cases"
	item.item_group_code= "BCS"
	item.stock_uom = "Nos"
	item.qty = "1"
	item.gst_hsn_code = '998521'
	item.is_stock_item = "0"
	item.include_item_in_manufacturing = "0"
	dict_list = []
	dict_list.append(frappe._dict({"item_tax_template":"GST 18% - THIS","tax_category":"Tamil Nadu","valid_from": today()}))
	dict_list.append(frappe._dict({"item_tax_template":"I - GST @ 18% - THIS","tax_category":"Inter State","valid_from": today()}))
	for j in dict_list:
		item.append("taxes", {
			"item_tax_template":j.item_tax_template,
			"tax_category":j.tax_category,
			"valid_from": j.valid_from
			})
	item.append("item_defaults", {
				"company": "TeamPRO HR & IT Services Pvt. Ltd.",
				"buying_cost_center":"Main - THIS",
				"selling_cost_center":"Main - THIS",
				"income_account":"Sales - THIS",
				"expense_account":"Cost of Goods Sold - THIS"
			})
	item.insert()
	item.save(ignore_permissions=True)

	so = frappe.new_doc("Sales Order")
	so.company = "TEAMPRO HR & IT Services Pvt. Ltd."
	so.customer = case.customer
	so.service = "BCS"
	so.order_type = "Sales"
	so.delivery_date = today()  
	so.transaction_date = today() 
	so.po_no = batch
	# so.delivery_manager = batch.delivery_manager
	so.posa_notes:case.case_report
	so.tc_name="Account Details - THIS"
	rate = frappe.db.get_value("Check Package", {"name":case.check_package},["total_sp"])
	
	so.append('items', {
		'item_code': case_id,
		'item_name':case.case_name,
		'case_batch':case.batch,
		'qty':1,
		'posa_notes':case.case_report,
		'rate':rate,
		})
	case_status=case.case_status
	billing_status = case.billing_status
	
	so.insert()
	so.save(ignore_permissions=True)
	frappe.msgprint("Sales Order Created"+" "+"-<b> "+so.name+"</b>")
	frappe.set_value("Case",case_id,"billing_status","Billed")
	frappe.set_value("Case",case_id,"case_status","Case Completed")
	

@frappe.whitelist()
def update_case_status():
	case = frappe.get_all("Case",{"batch":"BT-AMFL-2023-10-13-4655"},["name","case_status"])
	for c in case:
		if c.case_status=="Generate Report":
			list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
			for i in list:
				doc=frappe.get_all(i,{"case_id":c.name},["name","workflow_state"])
				for j in doc:
					if j.workflow_state != "Report Completed":
						frappe.db.set_value(i,j.name,"workflow_state","Report Completed")
			frappe.db.set_value("Case",c.name,"case_status","Case Report Completed")
			frappe.db.set_value("Case",c.name,"case_completion_date","2023-11-06")
			frappe.db.set_value("Case",c.name,"billing_Status","Billed")

@frappe.whitelist()
def update_case_billing_status():
	case = frappe.get_all("Case",{"batch":"BT-AMFL-2023-10-13-4655"},["name","case_status"])
	for c in case:
		if c.case_status=="Case Report Completed":
			frappe.db.set_value("Case",c.name,"billing_Status","Billed")


@frappe.whitelist()
def update_next_action_sm(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Social Media",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Social Media",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Social Media",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_fam(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Family",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Family",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Family",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_edu(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Education Checks",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Education Checks",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Education Checks",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_emp(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Employment",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Employment",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Employment",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_addrs(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Address Check",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Address Check",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Address Check",j,"workflow_state",next_indx)
		
	
@frappe.whitelist()
def update_next_action_court(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Court",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Court",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Court",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_criminal(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Criminal",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Criminal",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Criminal",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_ref(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Reference Check",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Reference Check",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Reference Check",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_next_action_id(check_id,allocated_to):
	doc_name = json.loads(check_id)
	for j in doc_name:
		frappe.set_value("Identity Aadhar",j,"allocated_to",allocated_to)
		doc = frappe.get_doc("Identity Aadhar",j)
		check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Pending','Execution Completed','Final QC Pending']
		if doc.workflow_state in check_status:
			indx=check_status.index(doc.workflow_state)
			next_indx=check_status[indx+1]
			frappe.set_value("Identity Aadhar",j,"workflow_state",next_indx)
	
@frappe.whitelist()
def update_case():
	# addrs = frappe.db.get_all("Address Check",{"check_status":"Draft"},['*'])
# 	for i in addrs:
# 		if i.workflow_state:
# 			frappe.db.set_value("Address Check",i.name,"check_status",i.workflow_state)
	# frappe.db.sql("""update `tabCase` set case_status = 'Case Completed' where case_status = 'Completed'""")
	# frappe.db.sql("""update `tabCase` set case_completion_date = '2024-01-22' where name = 'CS-006492'""")
	frappe.db.sql("""update `tabSocial Media` set workflow_state = 'Final QC Completed' where name = 'Social Media-132'""")
	frappe.db.sql("""update `tabSocial Media` set check_status = 'Final QC Completed' where name = 'Social Media-132'""")

			
# @frappe.whitelist()
# def update_case_status():
# 	cases=frappe.db.get_all("Case",{"case_status":"Generate Report","date_of_initiating":("<",'2023-08-01')},["name",'case_status'])
# 	i=1
# 	for c in cases:
# 		frappe.db.set_value("Case",c.name,"case_status","Report Completed")
# 		print(c.name)
# 		i+=1
# 	print(i)
	

@frappe.whitelist()
def update_batch():
	batch = frappe.get_all("Batch",{'batch_status':"Completed"},['*'])
	ind=1
	for b in batch:
		ind+=1
		case = frappe.get_all("Case",{"batch":b.name},["name","case_status","end_date"])
		for c in case:
			if c.end_date:
				# list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
				# for i in list:
				# 	doc=frappe.get_all(i,{"case_id":c.name},["name","workflow_state"])
				# 	for j in doc:
				# 		if j.workflow_state != "Report Completed":
				# 			frappe.db.set_value(i,j.name,"workflow_state","Report Completed")
				# frappe.db.set_value("Case",c.name,"case_status","Case Completed")
				# frappe.db.set_value("Case",c.name,"case_completion_date",c.end_date)
				pass
			else:
				print(c.name)
				list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
				for i in list:
					doc=frappe.get_all(i,{"case_id":c.name},["name","workflow_state"])
					for j in doc:
						if j.workflow_state != "Report Completed":
							frappe.db.set_value(i,j.name,"workflow_state","Report Completed")
				frappe.db.set_value("Case",c.name,"case_status","Case Completed")
				print(ind)
	print(ind)
	
# @frappe.whitelist()
# def update_batch_proposed_so():
# 	batch = frappe.get_all("Batch",{'batch_status':"Proposed SO"},['*'])
# 	ind=1
# 	for b in batch:
# 		ind+=1
# 		case = frappe.get_all("Case",{"batch":b.name},["name","case_status","end_date"])
# 		for c in case:
# 			if c.end_date:
# 				# list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
# 				# for i in list:
# 				# 	doc=frappe.get_all(i,{"case_id":c.name},["name","workflow_state"])
# 				# 	for j in doc:
# 				# 		if j.workflow_state != "Report Completed":
# 				# 			frappe.db.set_value(i,j.name,"workflow_state","Report Completed")
# 				# frappe.db.set_value("Case",c.name,"case_status","Case Completed")
# 				# frappe.db.set_value("Case",c.name,"case_completion_date",c.end_date)
# 				pass
# 			else:
# 				print(c.name)
# 				# list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
# 				# for i in list:
# 				# 	doc=frappe.get_all(i,{"case_id":c.name},["name","workflow_state"])
# 				# 	for j in doc:
# 				# 		if j.workflow_state != "Report Completed":
# 				# 			frappe.db.set_value(i,j.name,"workflow_state","Report Completed")
# 				# frappe.db.set_value("Case",c.name,"case_status","Case Completed")
# 				# print(ind)
# 	print(ind)

@frappe.whitelist()
def update_status_case():
    frappe.enqueue(
        update_case_status_report, # python function or a module path as string
        queue="long", # one of short, default, long
        timeout=36000, # pass timeout manually
        is_async=True, # if this is True, method is run in worker
        now=False, # if this is True, method is run directly (not in a worker) 
        job_name='Update Case Status', # specify a job name
        enqueue_after_commit=False, # enqueue the job after the database commit is done at the end of the request

    ) 
@frappe.whitelist()
def update_case_status_report():
	i=0
	case=frappe.db.get_all("Case",{"case_report":["in", ['Positive', 'Negative', 'Dilemma']],"case_status":"Generate Report"},['*'])
	for c in case:
		i+=1
		frappe.db.set_value("Case",c.name,"case_status","Case Report Completed")
		frappe.db.set_value("Case",c.name,"case_completion_date",c.end_date)
	print(i)