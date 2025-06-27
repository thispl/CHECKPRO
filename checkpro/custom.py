import frappe
import frappe.utils
from frappe.utils.csvutils import read_csv_content
from frappe.utils import get_first_day, get_last_day, format_datetime, get_url_to_form
from frappe.utils import cint
from frappe.utils.data import date_diff, now_datetime, nowdate, today, add_days
import datetime
from io import BytesIO
import openpyxl
from frappe import _
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from frappe import throw, msgprint
import frappe
from frappe.utils import flt, fmt_money
from datetime import timedelta
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
    customer = []
    check_package = []
    for c in doc_name:
        case=frappe.get_doc("Case",c)
        customer.append(case.customer)
        check_package.append(case.check_package)
    if all(cust == customer[0] for cust in customer) and all(check_pac == check_package[0] for check_pac in check_package):
        so = frappe.new_doc("Sales Order")
        so.company = "TEAMPRO HR & IT Services Pvt. Ltd."
        so.customer = case.customer
        so.service = "BCS"
        so.order_type = "Sales"
        so.delivery_date = today()  
        so.transaction_date = today()
        batch_delivery_manager = frappe.db.get_value("Batch",case.batch,['batch_manager']) 
        so.delivery_manager = batch_delivery_manager
        so.posa_notes=case.case_report
        so.tc_name="Account Details - THIS"
        for i in doc_name:
            case=frappe.get_doc("Case",i)
            if case.case_status =="To be Billed":
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

                
                # rate = frappe.db.get_value("Check Package", {"name":case.check_package},["total_sp"])
                package_price=frappe.db.get_value("Check Package",{"name":case.check_package},["pricing_model"])
                if package_price=="Lumpsum":
                    rate = frappe.db.get_value("Check Package", {"name":case.check_package},["total_sp"])
                elif package_price=="Check Based":
                    frappe.log_error(message='i',title='errors')
                    check_doc=frappe.get_doc("Check Package",{"name":case.check_package})
                    list=[]
                    rate = 0
                    for k in case.checkwise_status:
                        if k.checks_status=="Report Completed" and k.check_report !="Not Applicable":
                            check_type=k.checks
                            list.append(check_type)
                    for p in check_doc.checks_list:
                        if p.check_name in list:
                            rate+=p.check_sp
                    # for k in check_doc.checks_list:
                    #     if k.check_name in list:
                    #         rate+=k.check_sp
                so.append('items', {
                    'item_code': i,
                    'item_name':case.case_name,
                    'case_batch':case.batch,
                    'qty':1,
                    'posa_notes':case.case_report,
                    'rate':rate
                    })
                case_status=case.case_status
                billing_status = case.billing_status

                frappe.db.set_value("Case",i,"case_status","SO Created")
            
            else:
                frappe.msgprint("Case Status is not To be Billed for this Case-"+" "+i)
        so.insert()
        so.save(ignore_permissions=True)
        frappe.msgprint("Sales Order Created"+" "+"-<b> "+so.name+"</b>")
        # frappe.set_value("Case",i,"billing_status","Billed")
        
    else:
        frappe.msgprint("All Cases are not belong to same Customer and same Check Package")

@frappe.whitelist()
def case_report_submitted(case_id,mode_of_submission,proof_of_submission):
    doc_name = json.loads(case_id)
    for i in doc_name:
        case=frappe.get_doc("Case",i)
        if case.case_status =="Case Completed":
            frappe.set_value("Case",i,"mode_of_submission",mode_of_submission)
            frappe.set_value("Case",i,"proof_of_submission",proof_of_submission)
            frappe.set_value("Case",i,"case_status","To be Billed")
            
        else:
            frappe.msgprint("Case Status is not Case Completed for this Case-"+" "+i)


@frappe.whitelist()
def delete():
    frappe.db.sql("""delete from `tabScheduled Job Type` where name = "custom.statement_of_account" """,as_dict = True)
    # frappe.db.sql("""delete from `tabEducation Checks` where name = "Education Checks-2187" """,as_dict = True)


# @frappe.whitelist()
# def update_query():
            
    # frappe.db.sql("""update `tabCase` set case_status = 'Case Completed' where name = 'Case-205'""")
    # frappe.db.sql("""update `tabCase` set end_date = '2024-05-16' where name = 'CS-013495'""")
    
    # frappe.db.sql("""update `tabEducation Checks` set report_status = 'Not Applicable' where name = 'Education Checks-17161'""")
    # frappe.db.sql("""update `tabAddress Check` set workflow_state = 'Report Completed' where name = 'Address Check-9724'""")
    # frappe.db.sql("""update `tabAddress Check` set check_status = 'Report Completed' where name = 'Address Check-9724'""")
    
    # frappe.db.sql("""update `tabEmployment` set check_status = 'Draft',report_status='Pending' where name = 'Employment-3137 '""")
    # frappe.db.sql("""update `tabEmployment` set check_status = 'Execution Pending' where name = 'Employment-2493 '""")
    
    # frappe.db.sql("""update `tabSocial Media` set workflow_state = 'Draft' where name = 'Social Media-214'""")
    # frappe.db.sql("""update `tabSocial Media` set check_status = 'Draft' where name = 'Social Media-214'""")

    # frappe.db.sql("""update `tabEducation Checks` set tat_monitor = 'In TAT' where name = 'Education Checks-9270'""")

    # frappe.db.sql("""UPDATE `tabCase` SET case_status = 'Entry-Insuff' WHERE name ='CS-010548'""")

    # frappe.db.sql("""update `tabEducation Checks` set check_status = 'Report Completed ' where name = 'Education Checks-18031'""")

    # frappe.db.sql("""update `tabCandidate` set pending_for = 'Linedup' where name = 'CD19529'""")


    
    

@frappe.whitelist()
def create_so(case_id):
    frappe.log_error('Check error','error')
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
    frappe.log_error('check error','error')

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
    frappe.set_value("Case",case_id,"custom_case_update_status","Case Completed")
    

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
            frappe.db.set_value("Case",c.name,"custom_case_update_status","Case Report Completed")
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
        if doc.workflow_state in check_status:
            indx=check_status.index(doc.workflow_state)
            next_indx=check_status[indx+1]
            frappe.set_value("Employment",j,"workflow_state",next_indx)
    
@frappe.whitelist()
def update_next_action_addrs(check_id,allocated_to,allocate_to_supplier,supplier=None):
    doc_name = json.loads(check_id)
    for j in doc_name:
        frappe.set_value("Address Check",j,"allocated_to",allocated_to)
        doc = frappe.get_doc("Address Check",j)
        if supplier is not None:
            check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Supplier Pending','Execution Pending','Execution Completed','Final QC Pending']
            if doc.workflow_state in check_status:
                frappe.set_value("Address Check",j,"supplier",supplier)
                frappe.set_value("Address Check",j,"custom_supplier_allocation_date",frappe.utils.nowdate())
                indx=check_status.index(doc.workflow_state)
                next_indx=check_status[indx+1]
                frappe.set_value("Address Check",j,"workflow_state",next_indx)
        else:
            if doc.workflow_state == "Supplier Pending":
                frappe.set_value("Address Check",j,"workflow_state","Execution Pending")
                frappe.set_value("Address Check",j,"execution_allocation_date",frappe.utils.nowdate())
            else:
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
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
        check_status=['Draft','Entry Completed','Entry QC Pending','Entry QC Completed','Execution Initiated','Execution Pending','Execution Completed','Final QC Pending']
        if doc.workflow_state in check_status:
            indx=check_status.index(doc.workflow_state)
            next_indx=check_status[indx+1]
            frappe.set_value("Identity Aadhar",j,"workflow_state",next_indx)
    
# @frappe.whitelist()
# def update_case():
    # addrs = frappe.db.get_all("Address Check",{"check_status":"Draft"},['*'])
# 	for i in addrs:
# 		if i.workflow_state:
# 			frappe.db.set_value("Address Check",i.name,"check_status",i.workflow_state)
    # frappe.db.sql("""update `tabCase` set case_status = 'Case Completed' where case_status = 'Completed'""")
    # frappe.db.sql("""update `tabCase` set case_completion_date = '2024-01-22' where name = 'CS-006492'""")
    # frappe.db.sql("""update `tabSocial Media` set check_status = 'Draft' where name = 'Social Media-132'""")
    # frappe.db.sql("""update `tabSocial Media` set workflow_state = 'Draft' where name = 'Social Media-132'""")
    

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
                frappe.db.set_value("Case",c.name,"custom_case_update_status","Case Completed")
                print(ind)
    print(ind)
    
@frappe.whitelist()
def update_case_check():
    filename='96e1e0fa9fa3573billingstatus.csv'
    from frappe.utils.file_manager import get_file
    filepath = get_file(filename)
    pps = read_csv_content(filepath[1])
    ind=0
    for pp in pps:
        frappe.db.sql("""update `tabCase` set billing_status = 'Billed' where name = %s""",(pp[0]))
        ind+=1
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
        update_case_status_report, 
        queue="long", 
        timeout=36000,
        is_async=True, 
        now=False,  
        job_name='Update Case Status',
        enqueue_after_commit=False,

    ) 
@frappe.whitelist()
def update_case_status_report():
    i=0
    case=frappe.db.get_all("Case",{"case_report":["in", ['Positive', 'Negative', 'Dilemma']],"case_status":"Generate Report"},['*'])
    for c in case:
        i+=1
        frappe.db.set_value("Case",c.name,"case_status","Case Report Completed")
        frappe.db.set_value("Case",c.name,"custom_case_update_status","Case Report Completed")
        frappe.db.set_value("Case",c.name,"case_completion_date",c.end_date)
    print(i)

# @frappe.whitelist()
# def update_case_report_drop():
#     frappe.db.set_value("Education Checks",{"name":"Education Checks-21082"},"check_status","Draft")
#     frappe.db.set_value("Education Checks",{"name":"Education Checks-21082"},"report_status","YTS")
    # frappe.db.set_value("Identity Aadhar",{"name":"Identity Aadhar-1488"},"drop",0)
    # frappe.db.set_value("Education Checks",{"name":"Education Checks-21082"},"workflow_state","Draft")
    # frappe.db.set_value("Case",{"name":"KBL-190924-14871-00008"},"case_status","Generate Report")
    # frappe.db.sql("""update `tabCase` set case_status = 'Case Report Completed' where name = 'CS-009352'""")
    # frappe.db.sql("""update `tabCriminal` set check_status = 'Report Completed' where name = 'Criminal-1393'""")
    # frappe.db.sql("""update `tabCriminal` set workflow_state = 'Report Completed' where name = 'Criminal-1393'""")
    # frappe.db.sql("""update `tabEducation Checks` set dropped_date = NULL where name = 'Education Checks-7384'""")
    # frappe.db.sql("""update `tabCase` set check_status = 'Report Completed' where name = 'CS-008628'""")
    # frappe.db.sql("""update `tabCase` set dropped_date = NULL where name = 'CS-009352'""")
    # frappe.db.sql("""update `tabCase` set case_report = 'Drop' where name = 'CS-008628'""")


@frappe.whitelist()
def cases_beyond_tat_age_10():
    cases = frappe.get_all("Case", {"batch_age": (">=", 10), "case_status": ("not in", ['Case Report Completed', 'Case Completed', 'Drop','Execution-Insuff','Entry-Insuff','To be Billed','Generate Report','SO Created'])},['*'],order_by='batch_age DESC')
    data = '<table border="1" width="100%" style="border-collapse: collapse;">'
    data += '<tr style="background-color: #009dd1;"><td width=5% >S.No</td><td width=15% >Batch</td><td width=15% >Case ID</td><td width=25% >Customer</td><td width=20% >Employee Name</td><td width=10% >TAT Age</td><td width=10% >Case Status</td></tr>'
    i=1
    for c in cases:
        data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(i, c.batch, c.name, c.customer, c.case_name, c.batch_age, c.case_status)
        i+=1
    data += '</table>'
    frappe.sendmail(
        recipients=['dineshbabu.k@groupteampro.com','sangeetha.s@groupteampro.com','sangeetha.a@groupteampro.com','chitra.g@groupteampro.com',"keerthana.b@groupteampro.com"],
        cc=[''],
        subject=_("Cases having TAT Age 10 and above"),
        message="""
            Dear Sir/Madam,<br>Kindly Find the below List of Cases that are having TAT Age 10 and above %s<br>
            Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
            """%(data)
    )
    print(i)


import frappe
from frappe.utils import formatdate

@frappe.whitelist()
def cases_with_insuff():
    cases = frappe.get_all(
        "Case",
        filters={"case_status": ("in", ['Execution-Insuff', 'Entry-Insuff'])},
        fields=['*'],
        order_by='insufficiency_reported ASC'
    )
    

    data = '''
    <table border="1" width="100%" style="border-collapse: collapse; text-align: center;">
        <thead style="background-color: #0f1568; color: white;">
            <tr>
                <th width="5%">S.No</th>
                <th width="10%">Insuff Reported On</th>
                <th width="15%">Batch</th>
                <th width="15%">Case ID</th>
                <th width="25%">Customer</th>
                <th width="20%">Employee Name</th>
                <th width="10%">Employee Code</th>
                <th width="10%">Case Status</th>
                <th width="50%">Insuff Check(s)</th>
                <th width="5%">Age of Insufficiency</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    i = 1
    for c in cases:
        check_types = ["Education Checks", "Family", "Reference Check", "Court", "Social Media", "Criminal", "Employment", "Identity Aadhar", "Address Check"]
        checks = []
        
        for check_type in check_types:
            docs = frappe.get_all(
                check_type,
                filters={"case_id": c.name, "check_status": "Insufficient Data"},
                fields=["name"]
            )
            checks.extend([doc.name for doc in docs])
        
        checks_str = ", ".join(checks)
        insuff_reported = formatdate(c.insufficiency_reported) if c.insufficiency_reported else ''
        
        data += f'''
        <tr>
            <td>{i}</td>
            <td>{insuff_reported}</td>
            <td>{c.batch}</td>
            <td>{c.name}</td>
            <td>{c.customer}</td>
            <td>{c.case_name}</td>
            <td>{c.client_employee_code or "-"}</td>
            <td>{c.case_status}</td>
            <td>{checks_str}</td>
            <td>{c.insufficiency_days or "-"}</td>
        </tr>
        '''
        i += 1
    
    
    data += '''
        </tbody>
    </table>
    '''
    
    frappe.sendmail(
        # recipients=['divya.p@groupteampro.com'],
        # recipients="siva.m@groupteampro.com",
        recipients=['dineshbabu.k@groupteampro.com','sangeetha.s@groupteampro.com','sangeetha.a@groupteampro.com','chitra.g@groupteampro.com',"keerthana.b@groupteampro.com"],
        cc=[''],
        subject=_("Cases with Insuff"),
        message=f"""
            Dear Madam,<br>Kindly find the below list of cases that are in Insuff status:<br>{data}<br><br>
            Thanks & Regards,<br>TEAMPRO<br>"This email has been automatically generated. Please do not reply"<br><br>"initiate further action and intimate a direct manager through email."
        """
    )
    print(i)



@frappe.whitelist()
def cases_with_insuff_daily_report():
    customers_with_cases = frappe.get_all("Case", {
        "case_status": ("in", ['Execution-Insuff', 'Entry-Insuff'])
    }, ["customer"], distinct=True, pluck="customer")

    for customer in customers_with_cases:
        cases = frappe.get_all("Case", {
            "customer": customer,
            "case_status": ("in", ['Execution-Insuff', 'Entry-Insuff'])
        }, ['*'])

        if cases:
            cust_mail=''
            batch=''
            cs=''
            data = '<table border="1" width="100%" style="border-collapse: collapse;">'
            data += '<tr style="background-color: #009dd1;"><td width=5% >S.No</td><td width=10% >Insuff Reported On</td><td width=15% >Batch</td><td width=15% >Case ID</td><td width=10% >Customer</td><td width=10% >Employee Name</td><td width=10% >Employee Code</td><td width=10% >Check Type</td><td width=10% >ID</td><td width=15% >Insuff Reported By</td><td width=20% >Remarks</td></tr>'
            ind = 0
            check_types = ["Education Checks", "Family", "Reference Check", "Court", "Social Media", "Criminal", "Employment", "Identity Aadhar", "Address Check"]
            for c in cases:
                batch = c.batch
                cs=c.name
                cust_mail=frappe.db.get_value("Batch",{"name":c.batch},['customer_mail_ids'])
                for check_type in check_types:
                    doc = frappe.get_all(check_type, {
                        "case_id": c.name,
                        "check_status": "Insufficient Data",
                        "insufficiency_date": frappe.utils.nowdate()
                    }, ["name", "workflow_state", "custom_insufficiency_reported_by", "insufficiency_date", "case_id", "batch", 'insufficient_remarks'])

                    for j in doc:
                        ind += 1
                        data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                            ind, j.insufficiency_date or '', j.batch, j.case_id, c.customer, c.case_name,c.client_employee_code, check_type, j.name, j.custom_insufficiency_reported_by or '',  j.insufficient_remarks)

            data += '</table>'
            if ind>0:
                formatted_date = frappe.utils.format_datetime(frappe.utils.nowdate(), "dd-MMM-yyyy")
                frappe.sendmail(
                    # recipients=[cust_mail],
                    # recipients=["giftyannie6@gmail.com"],
                    recipients=['sangeetha.s@groupteampro.com','chitra.g@groupteampro.com',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],  
                    subject=_("Insufficiency Report - Customer: %s - Date: %s" % (customer, formatted_date)),
                    message="""
                        Dear Sir/Madam,<br>Kindly Find the below List of Cases that are Reported as Insuff on Today for Customer %s %s<br>
                        Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
                    """ % (customer, data)
                )


@frappe.whitelist()    
def batch_creation_mail(name):
    batch_doc = frappe.get_doc("Batch",name)
    for i in batch_doc:
        frappe.sendmail(
        recipients=['sangeetha.s@groupteampro.com',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],
        cc = [''],
        subject=('New Batch Creation'),
        message="""   
            Dear Sir/Mam,<br>
            <p>New batch <b>%s</b> has been created with <b>%s</b> cases for customer : <b>%s</b> on the Date : <b>%s</b> </p><br>
         
                Thanks & Regards<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
        """ % (batch_doc.name,batch_doc.no_of_cases,batch_doc.customer,batch_doc.expected_start_date)
        ) 
    return True

@frappe.whitelist()
def dsr_mail():
    # current_date = datetime.now().date()
    # previous_day = current_date - timedelta(days=1)
    user = frappe.get_all("User", filters={"role": "BCS User",'enabled':1},  fields=["*"])
    # user = frappe.get_all("User",{"roles":"BCS User"},["*"])
    table = '<table  text-align: center; border="1" width="100%" style="border-collapse: collapse;"><tr><td style="width: 40%; font-weight: bold;">Executive</td><td style="width: 20%; font-weight: bold;">Total Allocated To</td><td style="width: 20%; font-weight: bold;">Completed by Today</td><td style="width: 20%; font-weight: bold;">Total Pending</td></tr> '
    for u in user:
        total_tasks = 0
        pending_tasks = 0
        completed_today = 0
        case=frappe.get_all("Case",{"case_status":("in",['Draft',"Entry Completed"]),"allocated_to":u.name},["*"])
        for c in case:
            total_tasks += 1
            pending_tasks += 1
            if c.date_of_entry_completion.date() == frappe.utils.nowdate():
                completed_today += 1
        list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
        for i in list:
            doc=frappe.get_all(i,{"allocated_to":u.name},['*'])
            for j in doc:
                if j.check_status in ["Draft","Execution Pending"]:
                    total_tasks += 1
                    pending_tasks += 1
                    # table += '<td></td><td>{}</td><td></td><td>{}</td>'.format(total_tasks, pending_tasks)
                if str(j.date_of_entry_completion) == frappe.utils.nowdate() and j.entered_by == u.name:
                    # if j.date_of_entry_completion == nowdate():
                    # if j.date_of_entry_completion == frappe.utils.add_days(frappe.utils.nowdate(),-1):
                    completed_today += 1
                    total_tasks += 1
                        # table += '<td></td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(total_tasks, completed_today, pending_tasks)
                if str(j.date_of_execution_completion) == frappe.utils.nowdate() and j.execution_by == u.name:
                    # if j.date_of_execution_completion == nowdate():
                    # if j.date_of_execution_completion == frappe.utils.add_days(frappe.utils.nowdate(),-1):
                    completed_today += 1
                    total_tasks += 1
                        # table += '<td></td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(total_tasks, completed_today, pending_tasks)
        table += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (u.name, total_tasks, completed_today, pending_tasks)
    table += '</table>'
    frappe.sendmail(
        recipients=['chitra.g@groupteampro.com','sangeetha.s@groupteampro.com',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],
        subject=_("DSR-%s"%(nowdate()) ),
        message="""
            Dear Sir/Madam,<br>Kindly Find the below attached DSR - %s<br>
            Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
            """%(table)
    )
    return "ok"     


# @frappe.whitelist()
# def dpr_mail():
# 	user = frappe.get_all("User", filters={"role": "BCS User"},  fields=["*"])
    
# 	for u in user:
# 		table = '<table  text-align: center; border="1" width="100%" style="border-collapse: collapse;"><tr><td style="width: 15%; font-weight: bold;">ID</td><td style="width: 15%; font-weight: bold;">Batch</td><td style="width: 15%; font-weight: bold;">Employee Name</td><td style="width: 10%; font-weight: bold;">Employee Code</td><td style="width: 20%; font-weight: bold;">Client</td><td style="width: 10%; font-weight: bold;">Case ID</td><td style="width: 10%; font-weight: bold;">Case/Check Type</td><td style="width: 10%; font-weight: bold;">Case/Check Status</td><td style="width: 10%; font-weight: bold;">Actual Age</td><td style="width: 20%; font-weight: bold;">Allocated To</td></tr> '
# 		cases=frappe.get_all("Case",{"case_status":"Draft","allocated_to":u.name},['*'],order_by='actual_tat DESC')
# 		for c in cases:
# 			table += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>Case</td><td>%s</td><td>%s</td>td>%s</td></tr>' % (c.name, c.batch, c.case_name, c.client_employee_code, c.customer, c.name,c.case_status,c.actual_tat,u.name)
# 		list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
# 		for i in list:
# 			doc=frappe.get_all(i,{"allocated_to":u.name},['*'],order_by='actual_tat DESC')
# 			for j in doc:
# 				if j.check_status in ["Draft","Entry Completed","Execution Pending"]:
# 					if i == "Address Check":
# 						table += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (j.name, j.batch,j.name1,j.client_employee_code,j.client,j.case_id,i,j.check_status,j.actual_tat, u.name)
# 					else:
# 						table += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (j.name, j.batch,j.name1,j.client_employee_code,j.customer,j.case_id,i,j.check_status,j.actual_tat, u.name)
# 		table += '</table>'
# 		frappe.sendmail(
# 			# recipients=['giftyannie6@gmail.com'],
# 			recipients=[u.name],
# 			cc=['sangeetha.s@groupteampro.com'],
# 			subject=_("DPR-%s"%(nowdate()) ),
# 			message="""
# 				Dear Sir/Madam,<br>Kindly Find the below attached DPR, %s<br>
# 				Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
# 				"""%(table)
# 		)
# 	return "ok"
    

from datetime import datetime, timedelta
from frappe.utils import add_days
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def submitted_bg_entry():
    data = '<table  text-align: center; border="1" width="100%" style="border-collapse: collapse;text-align: center;">'
    data += '<tr style="font-weight: bold;background-color: #009dd1;"><td width=15%>ID</td><td width=25%>Name</td><td width=15%>DOB</td><td width=25%>Case Type</td><td width=25%>Status</td><td width=25%>Submitted Date</td><td width=25%>Submitted Time</td></tr>'
    today = datetime.now().date()
    prev_date = today - timedelta(days=1)
    start_time = datetime.combine(prev_date, datetime.min.time()) + timedelta(hours=18) 
    end_time = datetime.combine(today, datetime.min.time()) + timedelta(hours=18)   
    saved = frappe.db.sql("""
        SELECT * 
        FROM `tabBG Entry Form` 
        WHERE modified BETWEEN %s AND %s and docstatus = 1 order by experience DESC
    """, (start_time, end_time), as_dict=True)
    ind=0
    print(saved)
    for i in saved:
        print("hi")
        ind+=1
        modified_date = i.modified.date()
        modified_time = i.modified.strftime("%H:%M:%S")
        data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>Submitted</td><td>%s</td><td>%s</td></tr>' % (i.name,i.employee_name,i.date_of_birth, i.experience, modified_date,modified_time)
    data += '</table>'
    if ind >= 1:   
        frappe.sendmail(
            # recipients=['divya.p@groupteampro.com'],
            recipients=['sangeetha.s@groupteampro.com','evasengupta@kblservices.in','hrops@kblservices.in',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],
            subject=_("KBL New Cases"),
            message="""
                Dear Sir/Madam,<br>
                Kindly Find the below attached KBL New Cases  %s<br>
                Thanks & Regards,<br>
                TEAM ERP<br>
                "This email has been automatically generated. Please do not reply"
            """ % data
        )
    else:
        frappe.sendmail(
            # recipients=['divya.p@groupteampro.com'],
            recipients=['sangeetha.s@groupteampro.com','evasengupta@kblservices.in','hrops@kblservices.in',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],
            subject=_("KBL New Cases"),
            message="""
                Dear Sir/Madam,<br>
                No New Cases has been Submitted today  %s<br>
                Thanks & Regards,<br>
                TEAM ERP<br>
                "This email has been automatically generated. Please do not reply"
            """ % today
        )




@frappe.whitelist()
def insuff_consolidated_mail():
    user = frappe.get_all("User", filters={"role": "BCS User"},  fields=["*"])
    for u in user:
        ind=0
        table = '<table  text-align: center; border="1" width="100%" style="border-collapse: collapse;"><tr><td style="width: 15%; font-weight: bold;">ID</td><td style="width: 15%; font-weight: bold;">Batch</td><td style="width: 15%; font-weight: bold;">Employee Name</td><td style="width: 10%; font-weight: bold;">Employee Code</td><td style="width: 20%; font-weight: bold;">Client</td><td style="width: 10%; font-weight: bold;">Case ID</td><td style="width: 10%; font-weight: bold;">Check Type</td><td style="width: 10%; font-weight: bold;">Check ID</td><td style="width: 10%; font-weight: bold;">Check Status</td><td style="width: 10%; font-weight: bold;">Actual Age</td><td style="width: 20%; font-weight: bold;">Allocated To</td></tr> '
        list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
        for i in list:
            doc=frappe.get_all(i,{"allocated_to":u.name},['*'],order_by='actual_tat DESC')
            for j in doc:
                if j.clear_insufficiency:
                    if j.clear_insufficiency.strftime('%Y-%m-%d') == today():

                        ind+=1
                        if i == "Address Check":
                            table += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (j.name, j.batch,j.name1,j.client_employee_code,j.client,j.case_id,i,j.name,j.check_status,j.actual_tat, u.name)
                        else:
                            table += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (j.name, j.batch,j.name1,j.client_employee_code,j.customer,j.case_id,i,j.name,j.check_status,j.actual_tat, u.name)
        table += '</table>'
        if ind>0:
            frappe.sendmail(
                # recipients=['giftyannie6@gmail.com'],
                recipients=['sangeetha.s@groupteampro.com',u.name,'chitra.g@groupteampro.com',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],
                subject=_("Insuff Cleared-%s"%(nowdate()) ),
                message="""
                    Dear Sir/Madam,<br>Kindly Find the below attached List of Insuff Cleared Checks, %s<br>
                    Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
                    """%(table)
            )
    return "ok"


@frappe.whitelist()
def cases_with_gr_daily_report():
    data = '<table border="1" width="100%" style="border-collapse: collapse;">'
    data += '<tr style="background-color: #009dd1;"><td width=5% >S.No</td><td width=70% >Customer</td><td width=25% >Generate Report Count</td></tr>'
    customers_with_cases = frappe.get_all("Case", {
        "case_status": 'Generate Report'
    }, ["customer"], distinct=True, pluck="customer")
    ind = 0
    for customer in customers_with_cases:
        count=0
        ind += 1
        cases = frappe.get_all("Case", {
            "customer": customer,
            "case_status": 'Generate Report'
        }, ['*'])
        if cases:
            for c in cases:
                count+=1			
        data += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                ind, customer, count)
    data += '</table>'	
    formatted_date = frappe.utils.format_datetime(frappe.utils.nowdate(), "dd-MMM-yyyy")
    frappe.sendmail(
        # recipients=["giftyannie6@gmail.com"],
        recipients=['sangeetha.s@groupteampro.com','chitra.g@groupteampro.com',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],  
        subject=_("Customer-Wise Generate Report Count - %s" % (formatted_date)),
        message="""
            Dear Sir/Madam,<br>Kindly Find the below attached Customer-Wise Generate Report Count %s<br>
            Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
        """ % (data)
    )



import openpyxl
from io import BytesIO
@frappe.whitelist()
def dpr_excel_format_bcs():
    filename = "DPR_" + today()
    users = frappe.get_all("User", filters={"role": "BCS User","enabled":1,"name":"thelothamma.r@groupteampro.com"}, fields=["*"])
    for user in users:
        email = user.name
        xlsx_file = build_xlsx_response_file(filename,user.name)
        send_mail_with_dpr_attachment(email, filename, xlsx_file.getvalue())


def send_mail_with_dpr_attachment(recipient, filename, file_content):
    subject = ("DPR-%s-%s"%(nowdate(),recipient) )
    message = "Dear Sir/Madam,<br> Please find attached the Daily Progress Report.<br>Thanks & Regards,<br>TEAM ERP<br>This email has been automatically generated. Please do not reply"
    attachments = [{"fname": filename + '.xlsx', "fcontent": file_content}]
    frappe.sendmail(
        recipients=[recipient],
        # recipients="divya.p@groupteampro.com",
        cc=['sangeetha.s@gmail.com',"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],
        sender=None,  
        subject=subject,
        message=message,
        attachments=attachments,
    )


def build_xlsx_response_file(filename,user_name):
    xlsx_file = make_xlsx_file(filename,user_name)
    return xlsx_file

def make_xlsx_file(filename, user_name, sheet_name=None, wb=None, column_widths=None):
    from collections import defaultdict

    column_widths = column_widths or []
    if wb is None:
        wb = openpyxl.Workbook()
        # Remove the default sheet
        default_sheet = wb.active
        wb.remove(default_sheet)

    # Sheet 1: Main DPR
    ws1 = wb.create_sheet(title="DPR", index=0)
    ws1.append(["ID", "Batch", "Employee Name", "Employee Code", 'Client', 'Case ID', 'Case/Check Type',
                'Case/Check Status', 'Actual Age', 'Allocated To', 'Entry Allocated Date', 'Execution Allocated Date'])
    # Dict to track summary counts by Check Type only
    summary_counts = defaultdict(int)

    # Add Cases
    cases = frappe.get_all("Case", {"case_status": "Draft", "allocated_to": user_name},
                           ['*'], order_by='actual_tat DESC')
    for c in cases:
        ws1.append([
            c.name, c.batch, c.case_name, c.client_employee_code, c.customer, c.name,
            "Case", c.case_status, c.actual_tat, user_name,
            c.custom_allocation_date or '', ''
        ])
        summary_counts["Case"] += 1
    case_id_set = set()
    # Add Checks
    check_types = ["Education Checks", "Family", "Reference Check", "Court", "Social Media", "Criminal", "Employment", "Identity Aadhar", "Address Check"]
    for check in check_types:
        docs = frappe.get_all(check, {"allocated_to": user_name}, ['*'], order_by='actual_tat DESC')
        for d in docs:
            if d.check_status in ["Draft", "Entry QC Completed", "Execution Pending", "Execution Initiated"]:
                row = [
                    d.name, d.batch, d.name1, d.client_employee_code,
                    d.client if check in ["Address Check", "Court", "Employment", "Criminal", "Social Media", "Family"] else d.customer,
                    d.case_id, check, d.check_status, d.actual_tat, user_name,
                    d.custom_allocation_date or '', d.custom_date_of_execution_initiated or ''
                ]
                ws1.append(row)
                summary_counts[check] += 1
                if d.case_id:
                    case_id_set.add(d.case_id)

    # Sheet 2: Horizontal Summary
    ws2 = wb.create_sheet(title="Summary", index=1)
    ws2.append([])
    # Check types to include (as-is)
    check_types = ["Case","Education Checks", "Family", "Reference Check", "Court", "Social Media", "Criminal", "Employment", "Identity Aadhar", "Address Check"]

    # Add header row with original names
    # header_row = ["User"]+check_types
    # Mapping original keys to new column headers
    check_type_labels = {
        "Case": "Draft",
        "Education Checks": "Education Checks",
        "Criminal": "Criminal",
        "Employment": "Employment",
        "Identity Aadhar": "Identity Aadhar",
        "Address Check": "Address Check",
        "Family":"Family",
        "Reference Check":"Reference Check",
         "Court": "Court",
         "Social Media":"Social Media",

    }
    check_types = list(check_type_labels.keys())
    header_row = ["User"] + [check_type_labels[ct] for ct in check_types]

    ws2.append(header_row)

    # Add data row: user name + counts
    summary_row = [user_name] +[summary_counts.get(ct, 0) for ct in check_types]
    ws2.append(summary_row)

    # Apply formatting: bold header, blue fill
    header_fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
    bold_font = Font(bold=True)

    for cell in ws2[2]:  # first row (headers)
        cell.font = bold_font
        cell.fill = header_fill
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    return xlsx_file

# def make_xlsx_file(filename, user_name, sheet_name=None, wb=None, column_widths=None):
#     column_widths = column_widths or []
#     if wb is None:
#         wb = openpyxl.Workbook()
#     ws = wb.create_sheet(sheet_name, 0)

#     ws.append(["ID", "Batch", "Employee Name", "Employee Code", 'Client', 'Case ID', 'Case/Check Type',
#                'Case/Check Status', 'Actual Age', 'Allocated To','Entry Allocated Date','Execution Allocated Date'])

#     cases = frappe.get_all("Case", {"case_status": "Draft", "allocated_to": user_name},
#                            ['*'], order_by='actual_tat DESC')

#     for c in cases:
#         ws.append([c.name, c.batch, c.case_name, c.client_employee_code, c.customer, c.name, "Case",
#                    c.case_status, c.actual_tat, user_name,c.custom_allocation_date if c.custom_allocation_date else '',''])
#     list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
#     for i in list:
#         doc=frappe.get_all(i,{"allocated_to":user_name},['*'],order_by='actual_tat DESC')
#         for j in doc:
#             if j.check_status in ["Draft","Entry QC Completed","Execution Pending","Execution Initiated"]:
#                 if i in ["Address Check","Court","Employment","Criminal","Social Media","Family"]:
#                     ws.append([j.name, j.batch,j.name1,j.client_employee_code,j.client,j.case_id,i,j.check_status,j.actual_tat, user_name,j.custom_allocation_date if j.custom_allocation_date else '',j.custom_date_of_execution_initiated if j.custom_date_of_execution_initiated else ''])	
#                 else:
#                     ws.append([j.name, j.batch,j.name1,j.client_employee_code,j.customer,j.case_id,i,j.check_status,j.actual_tat, user_name,j.custom_allocation_date if j.custom_allocation_date else '',j.custom_date_of_execution_initiated if j.custom_date_of_execution_initiated else ''])

#     xlsx_file = BytesIO()
#     wb.save(xlsx_file)
#     return xlsx_file


@frappe.whitelist()
def cases_with_generate_report_status():
    cases = frappe.get_all("Case", {"case_status": "Generate Report"}, ['*'])

    if cases:
        data = '<table border="1" width="100%" style="border-collapse: collapse;">'
        data += '<tr style="background-color: #009dd1;"><td width=5% >S.No</td><td width=15% >Batch</td><td width=15% >Case ID</td><td width=10% >Customer</td><td width=10% >Employee Name</td><td width=10% >Employee Code</td></tr>'
        ind = 0
        for c in cases:	
            ind += 1
            data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                ind, c.batch, c.name, c.customer, c.case_name,c.client_employee_code)

        data += '</table>'
        if ind>0:
            formatted_date = frappe.utils.format_datetime(frappe.utils.nowdate(), "dd-MMM-yyyy")
            frappe.sendmail(
                # recipients=[cust_mail],
                # recipients=["giftyannie6@gmail.com"],
                recipients=['sangeetha.s@groupteampro.com','chitra.g@groupteampro.com',c.allocated_to_batch_manager,"sangeetha.a@groupteampro.com","keerthana.b@groupteampro.com"],  
                subject=_("Cases in Generate Report- Date: %s" % ( formatted_date)),
                message="""
                    Dear Sir/Madam,<br>Kindly Find the below List of Cases that are in "Generate Report" Status %s<br>
                    Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
                """ % (data)
            )

@frappe.whitelist()
def cases_with_to_be_billed_status():
    cases = frappe.get_all("Case", {"case_status": "To be Billed"}, ['*'])

    if cases:
        data = '<table border="1" width="100%" style="border-collapse: collapse;">'
        data += '<tr style="background-color: #009dd1;"><td width=5% >S.No</td><td width=15% >Batch</td><td width=15% >Case ID</td><td width=10% >Customer</td><td width=10% >Employee Name</td><td width=10% >Employee Code</td></tr>'
        ind = 0
        for c in cases:	
            ind += 1
            data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                ind, c.batch, c.name, c.customer, c.case_name,c.client_employee_code)

        data += '</table>'
        if ind>0:
            formatted_date = frappe.utils.format_datetime(frappe.utils.nowdate(), "dd-MMM-yyyy")
            frappe.sendmail(
                # recipients=[cust_mail],
                # recipients=["giftyannie6@gmail.com"],
                recipients=['sangeetha.s@groupteampro.com','chitra.g@groupteampro.com',c.allocated_to_batch_manager,"sangeetha.a@groupteampro.com"],  
                subject=_("Cases in To be Billed- Date: %s" % ( formatted_date)),
                message="""
                    Dear Sir/Madam,<br>Kindly Find the below List of Cases that are in "To be Billed" Status %s<br>
                    Thanks & Regards,<br>TEAM ERP<br>"This email has been automatically generated. Please do not reply"
                """ % (data)
            )

@frappe.whitelist()
def delete_batch_projects():
    projects=frappe.get_all("Project",{'project_type':"BCS","service":"BCS"},['*'])
    for p in projects:
        frappe.db.sql("""delete from `tabProject` where project_type = 'BCS'""",as_dict = True)
        print(p.project_type)

import frappe

import frappe

@frappe.whitelist()
def delete_batch_projects():
    projects = frappe.get_all("Project", {'project_type': "BCS", 'service': "BCS"}, ['*'])
    for p in projects:
        frappe.db.sql("""delete from `tabProject` where project_type = 'BCS'""", as_dict=True)
        print(p.project_type)

import frappe

@frappe.whitelist()
def delete_batch_projects():
    projects = frappe.get_all("Project", {'project_type': "BCS", 'service': "BCS"}, ['*'])
    for p in projects:
        frappe.db.sql("""delete from `tabProject` where project_type = 'BCS'""", as_dict=True)
        print(p.project_type)

# Project-Task-Candidate Automated Feedback Report
# @frappe.whitelist()
# def task_mail_notification():
#     data = ""

#     projects = frappe.db.get_list("Project", filters={'status': 'Open', 'service': ('in', ('REC-I', 'REC-D'))}, fields=['name'])
    
#     customer_data = {}

#     for project in projects:
#         tasks = frappe.db.get_all('Task', filters={'project': project.name, 'status': ('in', ('Open', 'Working', 'Pending Review', 'Overdue'))}, fields=['name', 'account_manager', 'spoc'])
        
#         for task in tasks:
#             candidate_task = frappe.get_doc('Task', task.name)
#             for candidate in candidate_task.task_candidate:
#                 if candidate.candidate_status not in ['IDB','Sourced','Proposed PSL']:
#                     if candidate.customer not in customer_data:
#                         customer_data[candidate.customer] = {
#                             'account_manager': task.account_manager or "-",
#                             'spoc': task.spoc or "-",
#                             'candidates': []
#                         }

#                     customer_data[candidate.customer]['candidates'].append({
#                         'candidate_id': candidate.candidate_id,
#                         'candidate_status': candidate.candidate_status,
#                         'given_name': candidate.given_name,
#                         'position': candidate.position,
#                         'passport_number': candidate.passport_number or "-",
#                         'project': candidate.project,
#                     })
    
#     for customer, info in customer_data.items():
#         candidates = info['candidates']
#         data += f'''
#         <table class="table table-bordered">
            
#             <tr><td style="padding:1px;border: 1px solid black" colspan="2">Customer Name:</td><td style="padding:1px;border: 1px solid black" colspan="4">&nbsp;&nbsp;&nbsp;&nbsp;{customer or '-'}</td></tr>
#             <tr><td style="padding:1px;border: 1px solid black" colspan="2">SPOC:</td><td style="padding:1px;border: 1px solid black" colspan="4">&nbsp;&nbsp;&nbsp;&nbsp;{info['spoc']}</td></tr>
#             <tr><td style="padding:1px;border: 1px solid black" colspan="2">Account Manager:</td><td style="padding:1px;border: 1px solid black" colspan="4">&nbsp;&nbsp;&nbsp;&nbsp;{info['account_manager']}</td></tr>
#             <tr>
#                 <td style="padding:1px;border: 1px white;background-color:#0f1568"><b>ID</b></td>
#                 <td style="padding:1px;border: 1px white;background-color:#0f1568"><b>Status</b></td>
#                 <td style="padding:1px;border: 1px white;background-color:#0f1568"><b>Given Name</b></td>
#                 <td style="padding:1px;border: 1px white;background-color:#0f1568"><b>Position</b></td>
#                 <td style="padding:1px;border: 1px white;background-color:#0f1568"><b>Passport NO</b></td>
#                 <td style="padding:1px;border: 1px white;background-color:#0f1568"><b>Project</b></td>
#             </tr>'''

#         for candidate in candidates:
#             data += f'''
#             <tr>
#                 <td style="padding:1px;border: 1px solid black">{candidate['candidate_id']}</td>
#                 <td style="padding:1px;border: 1px solid black">{candidate['candidate_status']}</td>
#                 <td style="padding:1px;border: 1px solid black">{candidate['given_name']}</td>
#                 <td style="padding:1px;border: 1px solid black">{candidate['position']}</td>
#                 <td style="padding:1px;border: 1px solid black">{candidate['passport_number']}</td>
#                 <td style="padding:1px;border: 1px solid black">{candidate['project']}</td>
#             </tr>'''

#         data += '</table><br><br>'
    
    
#     frappe.sendmail(
#         # recipients=['sangeetha.a@groupteampro.com','lokeshkumar.a@groupteampro.com','ponkamaleshwari.i@groupteampro.com','rama.a@groupteampro.com'],
#         # cc=['sangeetha.s@groupteampro.com','dineshbabu.k@groupteampro.com'],
#         recipients='divya.p@groupteampro.com',
#         subject='Candidate Feedback Pending Report',
#         message=f"""
#         <br>
#          <p>As per the mail, Profile feedback pending list.</p>
        
        
#           {data}<br><br>
#         "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
#             <br><br>
#             "With Best Wishes & Regards "
#             <br><br>
#             <span style="color:#203ed5;">
#             "TEN – Auto Mail "
#             </span>
#             <br><br>
#             <span style="color:#203ed5;">
#                 "Disclaimers:<br>
#                 This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
#             </span>
#         """
#     )
    # return data

# @frappe.whitelist()
# def task_mail_notification_status ():
#     job = frappe.db.exists('Scheduled Job Type','task_mail_notification')
#     if not job:
#         task = frappe.new_doc("Scheduled Job Type")
#         task.update({
#             "method": 'checkpro.custom.task_mail_notification',
#             "frequency": 'Cron',
#             "cron_format": '00 10 * * 1'
#         })
#         task.save(ignore_permissions=True)

# @frappe.whitelist()
# def task_mail_notification():
#     data = ""
#     data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#0f1568" colspan=9><center>Candidate Details</center></th></tr>'
#     data += '''
#     <tr>
#     <td style="padding:1px;border: 1px solid black"><b>ID</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Candidate Status</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Given Name / Surname</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Position</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Candidate Passport Number</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Project</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Customer</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>Account Manager</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan=1><b>SPOC</b></td>
#     </tr>'''

#     projects = frappe.db.get_list("Project", filters={'status': 'Open', 'service': ('in', ('REC-I', 'REC-D'))}, fields=['name'])

#     for project in projects:
#         tasks = frappe.db.get_all('Task', filters={'project': project.name, 'status': ('in', ('Open', 'Working', 'Pending Review', 'Overdue'))}, fields=['name','account_manager','spoc'])
        
#         for task in tasks:
#             candidate_task = frappe.get_doc('Task', task.name,task.account_manager)
            
#             for candidate in candidate_task.task_candidate:
#                 if candidate.candidate_status not in ['IDB', 'Sourced', 'Proposed PSL']:
#                     data += '''<tr>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1 nowrap>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1 nowrap>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#                     </tr>'''.format(candidate.candidate_id, candidate.candidate_status, candidate.given_name, candidate.position, candidate.passport_number or "-", candidate.project, candidate.customer,task.account_manager or "-",task.spoc or"-")

#     data += '</table>'
#     frappe.sendmail(
#         # recipients=['sangeetha.a@groupteampro.com','lokeshkumar.a@groupteampro.com','ponkamaleshwari.i@groupteampro.com','rama.a@groupteampro.com'],
#         # cc=['sangeetha.s@groupteampro.com','dineshbabu.k@groupteampro.com'],
#         recipients='siva.m@groupteampro.com',
#         subject=('Automated Candidate Feedback Report'),
#         message=f"""
#                 Dear Sir/Mam,<br>
#                 <p>As per the mail, Profile feedback pending list.</p>
#                 %s
#                 """ % (data)
#         )
#     return data

# Project-Task-Candidate Automated Feedback Report Internal Report
# @frappe.whitelist()
# def task_mail_notification_test():
#     data = ""

#     projects = frappe.db.get_list("Project", filters={'status': 'Open', 'service': ('in', ('REC-I', 'REC-D'))}, fields=['name'])
    
#     customer_data = {}

#     for project in projects:
#         tasks = frappe.db.get_all('Task', filters={'project': project.name, 'status': ('in', ('Open', 'Working', 'Pending Review', 'Overdue'))}, fields=['name','account_manager','spoc'])
        
#         for task in tasks:
#             candidate_task = frappe.get_doc('Task', task.name, task.account_manager)
            
#             for candidate in candidate_task.task_candidate:
#                 if candidate.candidate_status not in ['IDB', 'Sourced', 'Proposed PSL']:
#                     if candidate.customer not in customer_data:
#                         customer_data[candidate.customer] = []
                    
#                     customer_data[candidate.customer].append({
#                         'candidate_id': candidate.candidate_id,
#                         # 'surname': candidate.surname
#                         'project': candidate.project,
#                         'customer':candidate.customer,
#                         'account_manager': task.account_manager or "-",
#                         'spoc': task.spoc or "-"
#                     })
    
#     for customer, candidates in customer_data.items():
#         data += f'<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#0f1568" colspan=5><center>Candidate Details for {customer}</center></th></tr>'
#         data += '''
#         <tr>
#         <td style="padding:1px;border: 1px solid black"><b>ID</b></td>
#         <td style="padding:1px;border: 1px solid black" colspan=1><b>Project</b></td>
#         <td style="padding:1px;border: 1px solid black" colspan=1><b>Customer</b></td>
#         <td style="padding:1px;border: 1px solid black" colspan=1><b>Account Manager</b></td>
#         <td style="padding:1px;border: 1px solid black" colspan=1><b>SPOC</b></td>
#         </tr>'''

#         for candidate in candidates:
#             data += '''<tr>
#             <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#             <td style="padding:1px;border: 1px solid black" colspan=1 nowrap>{}</td>
#             <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#             <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#             <td style="padding:1px;border: 1px solid black" colspan=1>{}</td>
#             </tr>'''.format(
#                 candidate['candidate_id'],
#                  candidate['project'], candidate['customer'],
#                 candidate['account_manager'], candidate['spoc']
#             )

#         data += '</table><br><br>'

#     frappe.sendmail(
#         recipients=['sangeetha.a@groupteampro.com','lokeshkumar.a@groupteampro.com','ponkamaleshwari.i@groupteampro.com','rama.a@groupteampro.com'],
#         cc=['sangeetha.s@groupteampro.com','dineshbabu.k@groupteampro.com'],
#         #  recipients='siva.m@groupteampro.com',
#         subject='Automated Candidate Feedback Report',
#         message=f"""
#             Dear Sir/Mam,<br>
#             <p>As per the mail, Profile feedback pending list.</p>
#             {data}
#         """
#     )
#     return data
# @frappe.whitelist()
# def task_mail_notification_status_test():
#     job = frappe.db.exists('Scheduled Job Type','task_mail_notification_test')
#     if not job:
#         all = frappe.new_doc("Scheduled Job Type")
#         all.update({
#             "method": 'checkpro.custom.task_mail_notification_test',
#             "frequency": 'Cron',
#             "cron_format": '00 10 * * 1'
#         })
#         all.save(ignore_permissions=True)


@frappe.whitelist()
def gl_report(entry_report):
    data= ""
    data= ""
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:black;background-color:lightblue" colspan=7><center>General Ledger</center></th></tr>'
    data += '''
    <tr>
    <td  style="padding:1px;border: 1px solid black" ><b>Posting Date</b></td>
    <td style="padding:1px;border: 1px solid black" colspan =1><b>Account</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Debit(INR)</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Credit(INR)</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Balance(INR)</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Vocher Type</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Vocher NO</b>
    </td></tr>'''
    sq = frappe.db.sql(""" select * from `tabGL Entry` where account='%s' and posting_date between '%s' and '%s' and is_opening = 'No' and is_cancelled = 0 """%(entry_report,today(),today()),as_dict=True)
    for i in sq:
        balance=i.debit-i.credit
        data += '''<tr>
            <td style="padding:1px;border: 1px solid black" colspan =1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1 >%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1 >%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            </tr>'''%(i.posting_date,i.account,i.debit,i.credit,balance,i.voucher_type,i.voucher_no)

    data += '</table>'
    return data

from datetime import timedelta
import frappe
# Daily Transaction Report
# @frappe.whitelist()
# def statement_of_account():
#     data = ''
    
#     company=frappe.db.get_all('Company',{'name':('Not in',['TEAMPRO Saudi Arabia'])},['*'])
#     for j in company:
#         account=[]
        
#         if j.name=='TEAMPRO HR & IT Services Pvt. Ltd.':
#             account=['50200054611436 - HDFC - THIS','777705160983 - ICICI Bank - THIS','Cash - THIS']
#         elif j.name=='TEAMPRO General Trading':
#             account=['50200050787897 - HDFC Account - TGT','Cash - TGT']
#         elif j.name=='TEAMPRO Food Products':
#             account=['50200059117831 - HDFC Bank - TFP','Cash - TFP']	

        
#         data += "<br><table border=1 width='100%' style='margin-left:2px;margin-right:2px;'><tr style='font-size:10px;background-color:#D3D3D3'><td width=10%><b>Posting Date</b></td><td width=10%><b style='text-align:center;'>Voucher Type</b></td><td width=10%><b style='text-align:center'>Voucher No</b></td><td width=30%><b style='text-align:center'>Account</b></td><td width=10%><b style='text-align:center'>Debit(INR)</b></td><td width=10%><b style='text-align:center'>Credit(INR)</b></td><td width=10%><b style='text-align:center'>Balance(INR)</b></td><td width=10%><b style='text-align:center'>Company</b></td></tr>"
        
#         for a in account:

#             if a:
#                 data += f'<tr style="font-size:10px"><td colspan =2 style="text-align:right" width=20%><b>Account</b></td></td><td colspan=6 style="text-align:right" width=80%><b>{a}</b></td></tr>'

#                 today_date = frappe.utils.now_datetime().date()
#                 yesterday_date = today_date - timedelta(days=1)
#                 gl_entry = frappe.db.sql("""
#                     select voucher_type, voucher_no, posting_date, sum(debit) as debit, sum(credit) as credit,account
#                     from `tabGL Entry` 
#                     where account=%s and posting_date between %s and %s and is_cancelled = 0 and Company=%s 
#                     order by posting_date
#                 """, (a, today_date, today_date,j.name), as_dict=True)

#                 gle = frappe.db.sql("""
#                     select sum(debit) as opening_debit, sum(credit) as opening_credit 
#                     from `tabGL Entry` 
#                     where account=%s and (posting_date < %s or (ifnull(is_opening, 'No') = 'Yes' and posting_date >= %s)) 
#                     and is_cancelled = 0  and Company=%s
#                 """, (a, today_date, today_date,j.name), as_dict=True)

#                 opening_balance = 0
#                 t_p_debit = 0
#                 t_p_credit = 0
                
#                 for g in gle:
#                     opening_balance = (g.opening_debit or 0) - (g.opening_credit or 0)
#                     if not g.opening_debit:
#                         g.opening_debit = 0
#                     if not g.opening_credit:
#                         g.opening_credit = 0
#                     t_p_debit += g.opening_debit
#                     t_p_credit += g.opening_credit
#                     opening_balance = t_p_debit - t_p_credit
                
#                 data += f'<tr style="font-size:10px"><td colspan =6 style="text-align:right" width=90%><b>Opening Balance</b></td></td><td style="text-align:right" width=10%><b>{round(opening_balance,2)}</b></td></tr>'
                
#                 balance = opening_balance
                
#                 for i in gl_entry:
#                     posting_date = i.posting_date.strftime("%d-%m-%Y") if i.posting_date else "-"
#                     balance += (i.debit or 0) - (i.credit or 0)
#                     data += f'<tr style="font-size:10px"><td width=10% nowrap>{posting_date}</td><td width=10%>{i.voucher_type or " "}</td><td width=10%>{i.voucher_no or "-"}</td><td width=30%>{i.against or " "}</td><td width=10% style="text-align:right">{round(i.debit,2) or "-"}</td><td width=10% style="text-align:right">{round(i.credit,2) or "-"}</td><td style="text-align:right" width=10%>{round(balance,2)}</td><td style="text-align:left" width=10%>{j.name}</td></tr>'
                
#                 total_debit = sum(i.get('debit', 0) or 0 for i in gl_entry)
#                 total_credit = sum(i.get('credit', 0) or 0 for i in gl_entry)
#                 total_balance = balance
                
#                 data += f'<tr style="font-size:10px"><td colspan=4 style="text-align:right"><b>Total</b></td><td style="text-align:right"><b>{round(total_debit,2)}</b></td><td style="text-align:right"><b>{round(total_credit,2)}</b></td><td style="text-align:right"><b></b></td></tr>'
#                 data += f'<tr style="font-size:10px"><td colspan =6 style="text-align:right" width=90%><b>Closing Balance</b></td></td><td style="text-align:right" width=10%><b>{round(total_balance,2)}</b></td></tr>'
            
#         data += '</table><br><br>'
#     frappe.sendmail(
#         recipients=['dineshbabu.k@groupteampro.com'],
#         cc=['sangeetha.a@groupteampro.com','sangeetha.s@groupteampro.com','accounts@groupteampro.com'],
#         subject=('Daily Transaction Report'),
#         message=f"""
#                 Dear Sir/Mam,<br>
#                 <p>Please find the enclosed details for your reference. Kindly check the Daily Transaction Report</p>
#                 %s
#                 """ % (data)
#         )
#     return data
# def daily_transaction_mail_trigger():
#     job = frappe.db.exists('Scheduled Job Type', 'statement_of_account')
#     if not job:
#         var = frappe.new_doc("Scheduled Job Type")
#         var.update({
#             "method": 'checkpro.custom.statement_of_account',
#             "frequency": 'Cron',
#             "cron_format": '30 18 * * *'
#         })
#         var.save(ignore_permissions=True)

# Daily Transaction Report For New Correction
@frappe.whitelist()
def statement_of_account_test_1():
    data = """
    <style>
        .responsive-table {
            width: 100%;
            border-collapse: collapse;
        }
        .responsive-table th, .responsive-table td {
            padding: 8px;
            text-align: center;
        }
        .responsive-table th {
            background-color: #063970;
            color: white;
        }
        .responsive-table td.account {
            text-align: left;
        }
        .company-header {
            text-align: center;
            font-weight: bold;
        }
        @media (max-width: 600px) {
            .responsive-table thead {
                display: none;
            }
            .responsive-table, .responsive-table tbody, .responsive-table tr, .responsive-table td {
                display: block;
                width: 100%;
            }
            .responsive-table tr {
                margin-bottom: 15px;
            }
            .responsive-table td {
                text-align: right;
                padding-left: 50%;
                position: relative;
            }
            .responsive-table td::before {
                content: attr(data-label);
                position: absolute;
                left: 0;
                width: 50%;
                padding-left: 15px;
                text-align: left;
                font-weight: bold;
            }
        }
    </style>
    """
    company_order = [
        'TEAMPRO HR & IT Services Pvt. Ltd.',
        'TEAMPRO General Trading Pvt. Ltd.',
        'TEAMPRO General Trading',
        'TEAMPRO Food Products'
    ]

    company = frappe.db.get_all('Company', {'name': ('Not in', ['TEAMPRO Saudi Arabia'])}, ['*'])
    company_dict = {c.name: c for c in company}

    for company_name in company_order:
        j = company_dict.get(company_name)
        if not j:
            continue

        accounts = []

        if j.name == 'TEAMPRO HR & IT Services Pvt. Ltd.':
            accounts = ['50200054611436 - HDFC - THIS', '777705160983 - ICICI Bank - THIS', 'Cash - THIS']
        elif j.name == 'TEAMPRO General Trading Pvt. Ltd.':
            accounts = ['777705755022 - ICICI Bank - TGTP', 'Cash - TGTP']
        elif j.name == 'TEAMPRO General Trading':
            accounts = ['50200050787897 - HDFC Account - TGT', 'Cash - TGT']
        elif j.name == 'TEAMPRO Food Products':
            accounts = ['50200059117831 - HDFC Bank - TFP', 'Cash - TFP']

        data += f"<br><table class='responsive-table' border=1 style='margin:2px;'><tr class='company-header' style='text-align:center;font-size:10px;background-color:#063970;color:#FFFFFF;'><td width='100%'><b>{j.name}</b></td></tr></table>"
        data += "<table class='responsive-table' border=1 style='margin:2px;'><thead><tr style='font-size:10px;background-color:#063970;color:#FFFFFF;'><th width='10%'><b>Posting Date</b></th><th width='10%'><b>Voucher Type</b></th><th width='10%'><b>Voucher No</b></th><th width='30%'><b>Against Account</b></th><th width='10%'><b>Debit (INR)</b></th><th width='10%'><b>Credit (INR)</b></th><th width='10%'><b>Balance (INR)</b></th></tr></thead><tbody>"

        today_date = frappe.utils.now_datetime().date()

        for a in accounts:
            data += f'<tr style="font-size:10px"><td class="account" colspan=7><b>{a}</b></td></tr>'

            gl_entry = frappe.db.sql("""
                select voucher_type, voucher_no, posting_date, sum(debit) as debit, sum(credit) as credit, account, against
                from `tabGL Entry`
                where account=%s and posting_date=%s and is_cancelled = 0 and company=%s
                group by voucher_type, voucher_no, posting_date, account, against
                order by posting_date
            """, (a, today_date, j.name), as_dict=True)

            gle = frappe.db.sql("""
                select sum(debit) as opening_debit, sum(credit) as opening_credit
                from `tabGL Entry`
                where account=%s and posting_date < %s and is_cancelled = 0 and company=%s
            """, (a, today_date, j.name), as_dict=True)

            opening_balance = round((gle[0].opening_debit or 0) - (gle[0].opening_credit or 0), 2)
            data += f'<tr style="font-size:10px"><td colspan=6 style="text-align:right" data-label="Opening Balance"><b>Opening Balance</b></td><td style="text-align:right" data-label="Opening Balance"><b>{opening_balance}</b></td></tr>'

            balance = opening_balance
            total_debit = 0
            total_credit = 0

            for entry in gl_entry:
                posting_date = entry.posting_date.strftime("%d-%m-%Y") if entry.posting_date else "-"
                debit = round(entry.debit or 0, 2)
                credit = round(entry.credit or 0, 2)
                balance += debit - credit

                data += f'<tr style="font-size:10px"><td data-label="Posting Date">{posting_date}</td><td data-label="Voucher Type">{entry.voucher_type or "-"}</td><td data-label="Voucher No">{entry.voucher_no or "-"}</td><td data-label="Against Account">{entry.against or "-"}</td><td style="text-align:right" data-label="Debit (INR)">{debit}</td><td style="text-align:right" data-label="Credit (INR)">{credit}</td><td style="text-align:right" data-label="Balance (INR)">{round(balance, 2)}</td></tr>'

                total_debit += debit
                total_credit += credit

            total_balance = round(balance, 2)
            data += f'<tr style="font-size:10px"><td colspan=4 style="text-align:right" data-label="Total"><b>Total</b></td><td style="text-align:right" data-label="Total Debit"><b>{round(total_debit, 2)}</b></td><td style="text-align:right" data-label="Total Credit"><b>{round(total_credit, 2)}</b></td><td></td></tr>'
            data += f'<tr style="font-size:10px"><td colspan=6 style="text-align:right" data-label="Closing Balance"><b>Closing Balance</b></td><td style="text-align:right" data-label="Closing Balance"><b>{total_balance}</b></td></tr>'

        data += '</tbody></table><br><br>'


    frappe.sendmail(
        recipients=['dineshbabu.k@groupteampro.com'],
        cc=['sangeetha.a@groupteampro.com', 'sangeetha.s@groupteampro.com', 'accounts@groupteampro.com'],
        # recipients='divya.p@groupteampro.com',
        subject='Daily Transaction Report',
        message=f"""
            Dear Sir,<br>
            <p>Please find the enclosed details for your reference. Kindly check the Daily Transaction Report</p>
            {data}
            "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """
    )


# from datetime import timedelta
# import frappe

# @frappe.whitelist()
# def statement_of_account_1(entry_report):
#     data = ''
    
#     data += "<table border='1px solid black' width='100%' style='margin-left:2px;margin-right:2px;'><tr style='font-size:10px;background-color:#D3D3D3'><td width=10%><b>Posting Date</b></td><td width=10%><b style='text-align:center;'>Voucher Type</b></td><td width=10%><b style='text-align:center'>Voucher No</b></td><td width=30%><b style='text-align:center'>Account</b></td><td width=10%><b style='text-align:center'>Debit(INR)</b></td><td width=10%><b style='text-align:center'>Credit(INR)</b></td><td width=10%><b style='text-align:center'>Balance(INR)</b></td><td width=10%><b style='text-align:center'>Company</b></td></tr>"
#     if entry_report:
#         today_date = frappe.utils.now_datetime().date()
#         yesterday_date = today_date - timedelta(days=1)
#         gl_entry = frappe.db.sql("""
#             select voucher_type, voucher_no, posting_date, sum(debit) as debit, sum(credit) as credit, account, company 
#             from `tabGL Entry` 
#             where account=%s and posting_date between %s and %s and is_cancelled = 0
#             order by posting_date
#         """, (entry_report, today_date, today_date), as_dict=True)

#         gle = frappe.db.sql("""
#             select sum(debit) as opening_debit, sum(credit) as opening_credit 
#             from `tabGL Entry` 
#             where account=%s and (posting_date < %s or (ifnull(is_opening, 'No') = 'Yes' and posting_date >= %s)) 
#             and is_cancelled = 0
#         """, (entry_report, today_date, today_date), as_dict=True)

#         opening_balance = 0
#         t_p_debit = 0
#         t_p_credit = 0
        
#         for g in gle:
#             opening_balance = (g.opening_debit or 0) - (g.opening_credit or 0)
#             if not g.opening_debit:
#                 g.opening_debit = 0
#             if not g.opening_credit:
#                 g.opening_credit = 0
#             t_p_debit += g.opening_debit
#             t_p_credit += g.opening_credit
#             opening_balance = t_p_debit - t_p_credit
        
#         data += f'<tr style="font-size:10px"><td colspan =6 style="text-align:right" width=90%><b>Opening Balance</b></td></td><td style="text-align:right" width=10%><b>{opening_balance}</b></td></tr>'
        
#         balance = opening_balance
        
#         for i in gl_entry:
#             posting_date = i.posting_date.strftime("%d-%m-%Y") if i.posting_date else "-"
#             balance += (i.debit or 0) - (i.credit or 0)
#             data += f'<tr style="font-size:10px"><td width=10% nowrap>{posting_date}</td><td width=10%>{i.voucher_type}</td><td width=10%>{i.voucher_no}</td><td width=30%>{i.account}</td><td width=10% style="text-align:right">{i.debit or "-"}</td><td width=10% style="text-align:right">{i.credit or "-"}</td><td style="text-align:right" width=10%>{balance}</td><td style="text-align:right" width=10%>{i.company}</td></tr>'
        
#         total_debit = sum(i.get('debit', 0) or 0 for i in gl_entry)
#         total_credit = sum(i.get('credit', 0) or 0 for i in gl_entry)
#         total_balance = balance
        
#         data += f'<tr style="font-size:10px"><td colspan=4 style="text-align:right"><b>Total</b></td><td style="text-align:right"><b>{total_debit}</b></td><td style="text-align:right"><b>{total_credit}</b></td><td style="text-align:right"><b></b></td></tr>'
#         data += f'<tr style="font-size:10px"><td colspan =6 style="text-align:right" width=90%><b>Closing Balance</b></td></td><td style="text-align:right" width=10%><b>{total_balance}</b></td></tr>'
        
#     data += '</table>'
#     return data




# #Sales Order Follow Up New Correction

from frappe.utils import date_diff
from frappe import _

@frappe.whitelist()
def sales_order_follow_up():
    sales_orders = frappe.get_list(
        "Sales Order",
        filters={"status": ["not in", ["Hold", "To Deliver", "Closed", "Cancelled", "Completed"]]},
        fields=["name", "account_manager", "service", "status", "customer", "company", "transaction_date", "base_grand_total", "per_billed", "advance_paid"],
        order_by='customer asc'  
    )
    
    additional_table = '<br><br><table border=1><tr><td style="background-color:#063970;color:white">S.No</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
    tfp = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'
    
    total_amount = 0
    grand_total = 0
    serial_number = 1  

    for j in sales_orders:
        if j.get('service') == 'TFP':
            to_be_billed = j.get('base_grand_total') - (j.get('advance_paid') + ((j.get('per_billed') / 100) * j.get('base_grand_total')))
            total_amount += to_be_billed
            grand_total += j.get('base_grand_total')
            formatted_date = j.get("transaction_date").strftime('%d-%m-%Y')
            tfp += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
               j.get('name'), j.get('account_manager'), j.get('service'), j.get('status'), j.get('customer'), j.get('company'), formatted_date, "{:,.0f}".format(j.get('base_grand_total')), "{:,.0f}".format(j.get('per_billed')), "{:,.0f}".format(j.get('advance_paid')), "{:,.0f}".format(to_be_billed))
    
    additional_table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(serial_number, "TFP", "{:,.0f}".format(grand_total), "{:,.0f}".format(total_amount))
    
    tfp += '<tr><td style="text-align:center;" colspan=7>Total</td><td style="text-align:right">{}</td><td></td><td></td><td style="text-align:right;">{}</td></tr>'.format("{:,.0f}".format(grand_total), "{:,.0f}".format(total_amount))
    additional_table += '</table>'
    tfp += '</table>'

    frappe.sendmail(
        # recipients=["siva.m@groupteampro.com","accounts@groupteampro.com"],
        recipients='amirtham.g@groupteampro.com',
        cc=['sangeetha.s@groupteampro.com','dineshbabu.k@groupteampro.com','accounts@groupteampro.com'],
        subject='Sales Invoice Follow Up-Sales Order Outstanding',
        message="""
        Dear Mam,<br>
        <p>Collection Outstanding Report For Further Action.</p>
        TFP : SBMK/AM
        <br>
        {}
        <br>
        {}<br><br>
        "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """.format(additional_table, tfp)
    )



    additional_table = '<br><br><table border=1><tr><td style="background-color:#063970;color:white">S.No</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
    bcs = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'
    
    total_amount_bcs = 0
    grand_total_bcs = 0
    serial_number = 1  
    
    for i in sales_orders:
        if i.get('service') == 'BCS':
            to_be_billed = i.get('base_grand_total') - (i.get('advance_paid') + ((i.get('per_billed') / 100) * i.get('base_grand_total')))
            total_amount_bcs += to_be_billed
            grand_total_bcs += i.get('base_grand_total')
            formatted_date = i.get("transaction_date").strftime('%d-%m-%Y')
            bcs += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
                i.get('name'), i.get('account_manager'), i.get('service'), i.get('status'), i.get('customer'), i.get('company'), formatted_date, "{:,.0f}".format(i.get('base_grand_total')), "{:,.0f}".format(i.get('per_billed')), "{:,.0f}".format(i.get('advance_paid')), "{:,.0f}".format(to_be_billed))
    
    additional_table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(serial_number, "BCS", "{:,.0f}".format(grand_total_bcs), "{:,.0f}".format(total_amount_bcs))
    
    bcs += '<tr><td style="text-align:center;" colspan=7>Total</td><td style="text-align:right">{}</td><td></td><td></td><td style="text-align:right;">{}</td></tr>'.format("{:,.0f}".format(grand_total_bcs), "{:,.0f}".format(total_amount_bcs))
    additional_table += '</table>'
    bcs += '</table>'

    frappe.sendmail(
        # recipients=["siva.m@groupteampro.com","accounts@groupteampro.com"],
        recipients=['chitra.g@groupteampro.com', 'sangeetha.a@groupteampro.com'],
        cc=['dineshbabu.k@groupteampro.com', 'accounts@groupteampro.com', 'sangeetha.s@groupteampro.com'],
        subject='Sales Invoice Follow Up-Sales Order Outstanding',
        message="""
        Dear Mam,<br>
        <p>Collection Outstanding Report For Further Action.</p>
        BCS : SBMK
        <br>
        {}
        <br>
        {}<br><br>
        "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """.format(additional_table, bcs)
    )

    additional_table = '<br><br><table border=1><tr><td style="background-color:#063970;color:white">S.No</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
    rec = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'
    
    total_amount_rec = 0
    grand_total_rec = 0
    serial_number = 1  
    
    for k in sales_orders:
        if k.get('service') in ['REC-I', 'REC-D']:
            to_be_billed = k.get('base_grand_total') - (k.get('advance_paid') + ((k.get('per_billed') / 100) * k.get('base_grand_total')))
            total_amount_rec += to_be_billed
            grand_total_rec += k.get('base_grand_total')
            formatted_date = k.get("transaction_date").strftime('%d-%m-%Y')
            rec += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;" nowrap>{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
               k.get('name'), k.get('account_manager'), k.get('service'), k.get('status'), k.get('customer'), k.get('company'), formatted_date, "{:,.0f}".format(k.get('base_grand_total')), "{:,.0f}".format(k.get('per_billed')), "{:,.0f}".format(k.get('advance_paid')), "{:,.0f}".format(to_be_billed))
    
    additional_table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(serial_number, "REC", "{:,.0f}".format(grand_total_rec), "{:,.0f}".format(total_amount_rec))
    
    rec += '<tr><td style="text-align:center;" colspan=7>Total</td><td style="text-align:right">{}</td><td></td><td></td><td style="text-align:right;">{}</td></tr>'.format("{:,.0f}".format(grand_total_rec), "{:,.0f}".format(total_amount_rec))
    additional_table += '</table>'
    rec += '</table>'

    frappe.sendmail(
        # recipients=["siva.m@groupteampro.com","accounts@groupteampro.com"],
        recipients=['sangeetha.a@groupteampro.com'],
        cc=['dineshbabu.k@groupteampro.com', 'sangeetha.s@groupteampro.com', 'accounts@groupteampro.com', 'annie.m@groupteampro.com'],
        subject='Sales Invoice Follow Up-Sales Order Outstanding',
        message="""
        Dear Mam,<br>
        <p>Collection Outstanding Report For Further Action.</p>
        REC : AS/AM
        <br>
        {}
        <br>
        {}<br><br>
        "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """.format(additional_table, rec)
    )

    
    additional_table = '<br><br><table border=1><tr><td style="background-color:#063970;color:white">S.No</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
    itsw = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'
    
    total_amount_itsw = 0
    grand_total_itsw = 0
    serial_number = 1  

    for i in sales_orders:
        if i.get('service') in ['IT-SW', 'IT-IS']:
            to_be_billed = i.get('base_grand_total') - (i.get('advance_paid') + ((i.get('per_billed') / 100) * i.get('base_grand_total')))
            total_amount_itsw += to_be_billed
            grand_total_itsw += i.get('base_grand_total')
            formatted_date = i.get("transaction_date").strftime('%d-%m-%Y')
            itsw += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;" nowrap>{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
                i.get('name'), i.get('account_manager'), i.get('service'), i.get('status'), i.get('customer'), i.get('company'), formatted_date, "{:,.0f}".format(i.get('base_grand_total')), "{:,.0f}".format(i.get('per_billed')), "{:,.0f}".format(i.get('advance_paid')), "{:,.0f}".format(to_be_billed))
    
    additional_table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(serial_number, "IT-SW/IT-IS", "{:,.0f}".format(grand_total_itsw), "{:,.0f}".format(total_amount_itsw))
    
    itsw += '<tr><td style="text-align:center;" colspan=7>Total</td><td style="text-align:right">{}</td><td></td><td></td><td style="text-align:right;">{}</td></tr>'.format("{:,.0f}".format(grand_total_itsw), "{:,.0f}".format(total_amount_itsw))
    additional_table += '</table>'
    itsw += '</table>'

    frappe.sendmail(
        # recipients=["siva.m@groupteampro.com","accounts@groupteampro.com"],
        recipients=['dineshbabu.k@groupteampro.com'],
        cc=['anil.p@groupteampro.com', 'sangeetha.s@groupteampro.com', 'accounts@groupteampro.com'],
        subject='Sales Invoice Follow Up-Sales Order Outstanding',
        message="""
        Dear Sir,<br>
        <p>Collection Outstanding Report For Further Action.</p>
        IT-SW/IT-IS : DKB/APP
        <br>
        {}
        <br>
        {}<br><br>
        "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """.format(additional_table, itsw)
    )

    additional_table = '<br><br><table border=1><tr><td style="background-color:#063970;color:white">S.No</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
    tgt = ''
    tgt += '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'

    total_amount_tgt = 0
    grand_total_tgt = 0
    serial_number = 1 

    for i in sales_orders:
        if i.service == 'TGT':
            to_be_billed = i.base_grand_total - (i.advance_paid + ((i.per_billed / 100) * i.base_grand_total))
            total_amount_tgt += to_be_billed
            grand_total_tgt += i.base_grand_total
            formatted_date = i.transaction_date.strftime('%d-%m-%Y')
            tgt += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;" nowrap>{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
                i.name, i.account_manager, i.service, i.status, i.customer, i.company, formatted_date, "{:,.0f}".format(i.base_grand_total), "{:,.0f}".format(i.per_billed), "{:,.0f}".format(i.advance_paid), "{:,.0f}".format(to_be_billed))

    additional_table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(serial_number, "TGT", "{:,.0f}".format(grand_total_tgt), "{:,.0f}".format(total_amount_tgt))
    tgt += '<tr><td style="text-align:center;" colspan=7>Total</td><td style="text-align:right">{}</td><td></td><td></td><td style="text-align:right;">{}</td></tr>'.format("{:,.0f}".format(grand_total_tgt), "{:,.0f}".format(total_amount_tgt))
    additional_table += '</table>'
    tgt += '</table>'

    frappe.sendmail(
        # recipients=["siva.m@groupteampro.com","accounts@groupteampro.com"],
        recipients=['sangeetha.s@groupteampro.com'],
        cc=['dineshbabu.k@groupteampro.com', 'accounts@groupteampro.com'],
        subject='Sales Invoice Follow Up-Sales Order Outstanding',
        message="""
        Dear Mam,<br>
        <p>Collection Outstanding Report For Further Action.</p>
        TGT : SBMK
        <br>
        {}
        <br>
        {}<br><br>
        "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """.format(additional_table, tgt)
    )



# @frappe.whitelist()
# def sales_order_follow_up():
#     sales_orders = frappe.get_list(
#         "Sales Order",
#         filters={"status": ["not in", ["Hold", "To Deliver", "Closed", "Cancelled", "Completed"]]},
#         fields=["name", "account_manager", "service", "status", "customer", "company", "transaction_date", "grand_total", "per_billed", "advance_paid"]
#     )

#     # Generate table for Thai Summit
#     thai_summit = ''
#     thai_summit += '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'

#     total_amount_thai_summit = 0
#     for order in sales_orders:
#         if order.service == 'TFP' and order.customer == 'THAI SUMMIT AUTOPARTS INDIA PRIVATE LIMITED':
#             to_be_billed = order.grand_total - (order.advance_paid + ((order.per_billed / 100) * order.grand_total))
#             total_amount_thai_summit += to_be_billed
#             thai_summit += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;">{}</td><td>{}</td><td style="text-align:right;">{}</td><td>{}</td><td style="text-align:right;">{}</td></tr>'.format(
#                 order.name, order.account_manager, order.service, order.status, order.customer, order.company, order.transaction_date, order.grand_total, order.per_billed, order.advance_paid, to_be_billed)

#     thai_summit += '<tr><td></td><td></td><td style="text-align:center;" colspan=3>Total</td><td></td><td style="text-align:right;">{}</td><td></td><td></td><td></td></tr>'.format(total_amount_thai_summit)
#     thai_summit += '</table>'

#     frappe.sendmail(
#         recipients='siva.m@groupteampro.com',
#         subject='Sales Order Follow Up - Thai Summit',
#         message="""
#         Dear Sir/Mam,<br>
#         {}
#         <br>
#         Thanks & Regards<br>TEAMPRO<br>
#         """.format(thai_summit)
#     )

#     # Generate table for other customers
#     tfp = ''
#     tfp += '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'

#     total_amount_others = 0
#     for order in sales_orders:
#         if order.service == 'TFP' and order.customer != 'THAI SUMMIT AUTOPARTS INDIA PRIVATE LIMITED':
#             to_be_billed = order.grand_total - (order.advance_paid + ((order.per_billed / 100) * order.grand_total))
#             total_amount_others += to_be_billed
#             tfp += '<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;">{}</td><td>{}</td><td style="text-align:right;">{}</td><td>{}</td><td style="text-align:right;">{}</td></tr>'.format(
#                 order.name, order.account_manager, order.service, order.status, order.customer, order.company, order.transaction_date, order.grand_total, order.per_billed, order.advance_paid, to_be_billed)

#     tfp += '<tr><td></td><td></td><td style="text-align:center;" colspan=3>Total</td><td></td><td style="text-align:right;">{}</td><td></td><td></td><td></td></tr>'.format(total_amount_others)
#     tfp += '</table>'

#     frappe.sendmail(
#         recipients='siva.m@groupteampro.com',
#         subject='Sales Order Follow Up - Other Customers',
#         message="""
#         Dear Sir/Mam,<br>
#         {}
#         <br>
#         Thanks & Regards<br>TEAMPRO<br>
#         """.format(tfp)
#     )




# Overall Service Report With Excel Sheet Attachment

import frappe
import openpyxl
from openpyxl.styles import PatternFill
from frappe.utils import nowdate, add_days
from io import BytesIO

@frappe.whitelist()
def sales_order_follow_up_test():
    def send_sales_report_with_table():
        filename = "Sales_Order_Follow_Up_" + nowdate() + ".xlsx"
        xlsx_file = build_xlsx_response_sales(filename)
        html_table, total_count = sales_next_action()
        send_mail_with_attachment_and_html(filename, xlsx_file, html_table)

    def build_xlsx_response_sales(filename):
        return make_xlsx_sales(filename)

    def make_xlsx_sales(filename, sheet_name=None, wb=None, column_widths=None):
        if wb is None:
            wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet_name or filename
        default_column_widths = [15, 25, 25, 15, 25, 20]
        column_widths = column_widths or default_column_widths
        for i, width in enumerate(column_widths, start=1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
        
        header_fill = PatternFill(start_color="87CEFA", end_color="87CEFA", fill_type="solid")
        headers = ["name", "account_manager", "service", "status", "customer", "company", "transaction_date", "grand_total", "per_billed", "advance_paid", "to_be_billed"]
        ws.append(headers)
        for cell in ws[1]:
            cell.fill = header_fill

        sales_orders = frappe.get_list(
            "Sales Order",
            filters={"status": ["not in", ["Hold", "To Deliver", "Closed", "Cancelled", "Completed"]]},
            fields=["name", "account_manager", "service", "status", "customer", "company", "transaction_date", "base_grand_total", "per_billed", "advance_paid"]
        )

        service_summary = {}
        total_outstanding = 0

        for order in sales_orders:
            to_be_billed = order.base_grand_total - (order.advance_paid + ((order.per_billed / 100) * order.base_grand_total))
            ws.append([
                order.name, order.account_manager, order.service, order.status, order.customer, order.company,
                order.transaction_date.strftime("%d-%m-%Y"), round(order.base_grand_total, 2), round(order.per_billed, 2),
                round(order.advance_paid, 2), round(to_be_billed, 2)
            ])
            if order.service not in service_summary:
                service_summary[order.service] = {"base_grand_total": 0, "outstanding": 0}
            service_summary[order.service]["base_grand_total"] += order.base_grand_total
            service_summary[order.service]["outstanding"] += to_be_billed
            total_outstanding += to_be_billed

        # Add total row
        ws.append([""] * 9 + ["Total", round(total_outstanding, 2)])

        with BytesIO() as b:
            wb.save(b)
            b.seek(0)
            return b.read()

    def sales_next_action():
        sales_orders = frappe.get_list(
            "Sales Order",
            filters={"status": ["not in", ["Hold", "To Deliver", "Closed", "Cancelled", "Completed"]]},
            fields=["name", "account_manager", "service", "status", "customer", "company", "transaction_date", "base_grand_total", "per_billed", "advance_paid"]
        )

        service_summary = {}
        detailed_rows = []

        for order in sales_orders:
            if order.service not in service_summary:
                service_summary[order.service] = {"base_grand_total": 0, "outstanding": 0}
            
            to_be_billed = order.base_grand_total - (order.advance_paid + ((order.per_billed / 100) * order.base_grand_total))
            service_summary[order.service]["base_grand_total"] += order.base_grand_total
            service_summary[order.service]["outstanding"] += to_be_billed

            transaction_date = order.transaction_date.strftime("%d-%m-%Y")
            
            detailed_rows.append('<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
                order.name, order.account_manager, order.service, order.status, order.customer, order.company, transaction_date, round(order.base_grand_total, 2), round(order.per_billed, 2), round(order.advance_paid, 2), round(to_be_billed, 2)))

        summary_table = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">Services</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
        grand_total_amount = 0
        total_outstanding = 0

        for service, amounts in service_summary.items():
            summary_table += '<tr style="font-size:14px"><td>{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(service, round(amounts["base_grand_total"], 2), round(amounts["outstanding"], 2))
            grand_total_amount += amounts["base_grand_total"]
            total_outstanding += amounts["outstanding"]

        summary_table += '<tr><td></td><td style="text-align:center;" colspan=1>Total</td><td style="text-align:right;">{}</td></tr>'.format(round(total_outstanding, 2))
        summary_table += '</table>'
        
        details_table = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Status</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">% Amount Billed</td><td style="background-color:#063970;color:white">Advance Paid</td><td style="background-color:#063970;color:white">To Be Billed</td></tr>'
        details_table += ''.join(detailed_rows)
        details_table += '<tr><td colspan=9></td><td style="text-align:center;">Total</td><td style="text-align:right;">{}</td></tr>'.format(round(total_outstanding, 2))
        details_table += '</table>'
        
        total_count = len(sales_orders)
        return summary_table + details_table, total_count

    def send_mail_with_attachment_and_html(filename, file_content, html_content):
        attachments = [{"fname": filename, "fcontent": file_content}]
        frappe.sendmail(
            # recipients='siva.m@groupteampro.com',
           recipients='dineshbabu.k@groupteampro.com',
            cc=["accounts@groupteampro.com","sangeetha.s@groupteampro.com","sangeetha.a@groupteampro.com","annie.m@groupteampro.com","amirtham.g@groupteampro.com","anil.p@groupteampro.com"],
            subject='Sales Invoice Follow Up-Sales Order Outstanding',
            message="""
            <br>
            <p>Collection Outstanding Report For Further Action.</p>
            REC   : AS/AM<br><br>
            IT-SW : DKB/APP<br><br>
            TFP   : SBMK/AM<br><br>
            BCS   : SBMK<br><br>
            TGT   : SBMK<br><br>
            <br>
            {0}
            <br><br>
            Thanks & Regards,<br>TEAMPRO<br>"This email has been automatically generated. Please do not reply"<br><br>"Initiate further action and intimate a direct manager through email."
            """.format(html_content),
            attachments=attachments,
        )

    send_sales_report_with_table()


########   Sales Invoice Overall Service Excel Sheet Attachment   ###########


import frappe
import openpyxl
from openpyxl.styles import PatternFill
from frappe.utils import nowdate
from io import BytesIO

@frappe.whitelist()
def sales_invoice_follow_up_test():
    def send_sales_report_with_table():
        filename = "Sales_Invoice_Follow_Up_" + nowdate() + ".xlsx"
        xlsx_file = build_xlsx_response_sales(filename)
        html_table, total_count = sales_next_action()
        send_mail_with_attachment_and_html(filename, xlsx_file, html_table)

    def build_xlsx_response_sales(filename):
        return make_xlsx_sales(filename)

    def make_xlsx_sales(filename, sheet_name=None, wb=None, column_widths=None):
        import openpyxl
        from openpyxl.styles import PatternFill
        from io import BytesIO

        if wb is None:
            wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet_name or filename
        default_column_widths = [15, 25, 25, 15, 25, 20]
        column_widths = column_widths or default_column_widths
        for i, width in enumerate(column_widths, start=1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
        
        header_fill = PatternFill(start_color="87CEFA", end_color="87CEFA", fill_type="solid")
        headers = ["ID", "Account Manager", "Service", "Customer Name", "Company", "Date", "Grand Total", "Outstanding Amount", "Age"]
        ws.append(headers)
        for cell in ws[1]:
            cell.fill = header_fill

        sales_invoice = frappe.get_list("Sales Invoice", filters={"status": ["not in", ["Return", "Credit Note Issued", "Paid", "Cancelled"]]}, fields=["name", "company", "customer", "services", "posting_date", "due_date", "grand_total", "outstanding_amount", "account_manager", "delivery_manager"])

        service_summary = {}
        total_outstanding = 0

        for order in sales_invoice:
            todate = date.today()
            grand_total = round(order.grand_total, 2)
            outstanding_amount = round(order.outstanding_amount, 2)
            total_outstanding += outstanding_amount
            postingdate1 =(order.posting_date)
            age = (todate - postingdate1).days

            ws.append([
                order.name, order.account_manager, order.services, order.customer, order.company,
                order.posting_date.strftime("%d-%m-%Y"), grand_total, outstanding_amount, age
            ])

            if order.services not in service_summary:
                service_summary[order.services] = {"grand_total": 0, "outstanding": 0}
            service_summary[order.services]["grand_total"] += grand_total
            service_summary[order.services]["outstanding"] += outstanding_amount

        
        ws.append([""] * 6 + ["Total", round(total_outstanding, 2)])

        with BytesIO() as b:
            wb.save(b)
            b.seek(0)
            return b.read()

    def sales_next_action():
        sales_invoice = frappe.get_list("Sales Invoice", filters={"status": ["not in", ["Return", "Credit Note Issued", "Paid", "Cancelled"]]}, fields=["name", "company", "customer", "services", "posting_date", "due_date", "grand_total", "outstanding_amount", "account_manager", "delivery_manager"])

        service_summary = {}
        detailed_rows = []

        for order in sales_invoice:
            grand_total = round(order.grand_total, 2)
            outstanding_amount = round(order.outstanding_amount, 2)

            if order.services not in service_summary:
                service_summary[order.services] = {"grand_total": 0, "outstanding": 0}
            service_summary[order.services]["grand_total"] += grand_total
            service_summary[order.services]["outstanding"] += outstanding_amount

            transaction_date = (order.posting_date.strftime("%d-%m-%Y"))
            todate = date.today()
            age = (todate - order.posting_date).days
            
            detailed_rows.append('<tr style="font-size:14px"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td style="text-align:left;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(
                order.name, order.account_manager, order.services, order.customer, order.company,transaction_date, grand_total, outstanding_amount, age))

        summary_table = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">Services</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding</td></tr>'
        grand_total_amount = 0
        total_outstanding = 0

        for service, amounts in service_summary.items():
            summary_table += '<tr style="font-size:14px"><td>{}</td><td style="text-align:right;">{}</td><td style="text-align:right;">{}</td></tr>'.format(service, round(amounts["grand_total"], 2), round(amounts["outstanding"], 2))
            grand_total_amount += amounts["grand_total"]
            total_outstanding += amounts["outstanding"]

        summary_table += '<tr><td></td><td style="text-align:center;" colspan=1>Total</td><td style="text-align:right;">{}</td></tr>'.format(round(total_outstanding, 2))
        summary_table += '</table>'
        
        details_table = '<table border=1><tr style="text-align: center"><td style="background-color:#063970;color:white">ID</td><td style="background-color:#063970;color:white">Account Manager</td><td style="background-color:#063970;color:white">Service</td><td style="background-color:#063970;color:white">Customer Name</td><td style="background-color:#063970;color:white">Company</td><td style="background-color:#063970;color:white">Date</td><td style="background-color:#063970;color:white">Grand Total</td><td style="background-color:#063970;color:white">Outstanding Amount</td><td style="background-color:#063970;color:white">Age</td></tr>'
        details_table += ''.join(detailed_rows)
        details_table += '<tr><td colspan=6></td><td style="text-align:center;">Total</td><td style="text-align:right;">{}</td></tr>'.format(round(total_outstanding, 2))
        details_table += '</table>'
        
        total_count = len(sales_invoice)
        return summary_table + details_table, total_count

    def send_mail_with_attachment_and_html(filename, file_content, html_content):
        attachments = [{"fname": filename, "fcontent": file_content}]
        frappe.sendmail(
            recipients='dineshbabu.k@groupteampro.com',
            cc=["accounts@groupteampro.com","sangeetha.s@groupteampro.com","sangeetha.a@groupteampro.com","annie.m@groupteampro.com","amirtham.g@groupteampro.com","anil.p@groupteampro.com"],
            subject='Collection Follow Up-Sales Invoice Report',
            message="""
            <br>
            <p>Collection Outstanding Report For Further Action.</p>
            REC   : AS/AM<br><br>
            IT-SW : DKB/APP<br><br>
            TFP   : SBMK/AM<br><br>
            BCS   : SBMK<br><br>
            TGT   : SBMK<br><br>
            <br>
            {0}
            <br><br>
            Thanks & Regards,<br>TEAMPRO<br>"This email has been automatically generated. Please do not reply"<br><br>"Initiate further action and intimate a direct manager through email."
            """.format(html_content),
            attachments=attachments,
        )

    send_sales_report_with_table()



# def test_case_del():
#     filename='120ab20e63d47ab9ec4dcaseidlist.csv'
#     from frappe.utils.file_manager import get_file
#     filepath = get_file(filename)
#     pps = read_csv_content(filepath[1])
#     ind=0
#     for pp in pps:
#         ind+=1
#         # print(pp[0])
#         # case_ids = frappe.get_all("Case",{"name":"pp.name"},["name"])
#         # print(case_ids)
#         # for case in case_ids:
#         #     print("helo")
#         list = ["Education Checks", "Family", "Reference Check", "Court","Social Media", "Criminal", "Employment", "Identity Aadhar", "Address Check"]
#         for i in list:
#             if i == "Education Checks" and pp and pp[0]:
#                 # frappe.db.sql("""DELETE FROM `tabCase` WHERE name= '%s' """%(pp[0]))
#                 frappe.db.sql("""DELETE FROM `tabEducation Checks` WHERE case_id= '%s' """%(pp[0]))
#             if i == "Family" and pp and pp[0]:
#                 # print(i)
#                 # print(pp[0])
#                 frappe.db.sql("""DELETE FROM `tabFamily` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Reference Check" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabReference Check` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Court" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabCourt` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Social Media" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabSocial Media` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Criminal" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabCriminal` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Employment" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabEmployment` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Identity Aadhar" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabIdentity Aadhar` WHERE case_id= '%s' """%(pp[0]))
#             elif i == "Address Check" and pp and pp[0]:
#                 frappe.db.sql("""DELETE FROM `tabAddress Check` WHERE case_id= '%s' """%(pp[0]))

        

import frappe
from frappe.utils import nowdate, today
import openpyxl
from io import BytesIO
from frappe.utils.pdf import get_pdf
# candidate automated mail trigger
# @frappe.whitelist()
# def candidate_excel_format():
#     next_date=today()
#     next_dates=datetime.strptime(next_date, '%Y-%m-%d')
#     formatted_next_date=next_dates.strftime('%Y-%m-%d')
#     filename = "Candidate_Details_" + today() + ".xlsx"
#     pdffilename = "Candidate_Details_" + today() + ".pdf"
#     candidates = frappe.get_all(
#         "Candidate",
#         filters={'submitted_date': formatted_next_date},
#         fields=["candidate_created_by"],
#         group_by='candidate_created_by'
#     )

#     for user in candidates:
#         user_id = user.candidate_created_by
#         xlsx_file = make_xlsx(filename, user_id)
#         pdf_content = make_pdf(pdffilename, user_id)
#         candidate_status_mail(filename, xlsx_file.getvalue(), pdffilename, pdf_content, user_id)

# def candidate_status_mail(filename, file_content, pdffilename, pdf_content, user_id):
#     next_date=today()
#     next_dates=datetime.strptime(next_date, '%Y-%m-%d')
#     formatted_next_date=next_dates.strftime('%Y-%m-%d')
#     data = """<table class='table table-bordered' style='border-collapse: collapse; width: 100%;'>
#     <tr style='border: 1px solid black; background-color: #0f1568; color: white;'>
#     <th>S No</th><th>Candidate ID</th><th>Passport Number</th><th>Name</th><th>Project</th><th>Task</th><th>Status</th></tr>"""

#     s_no = 0
#     candidates = frappe.get_all(
#         "Candidate",
#         filters={'submitted_date': formatted_next_date, 'candidate_created_by': user_id,'pending_for':'Submitted(Internal)'},
#         fields=["name", "passport_number", "given_name", "project_name", "task", "pending_for"]
#     )

#     for candidate in candidates:
#         s_no += 1
#         data += f"""<tr style='border: 1px solid black;'>
#         <td>{s_no}</td><td>{candidate.name or '-'}</td><td>{candidate.passport_number or '-'}</td>
#         <td>{candidate.given_name or '-'}</td><td>{candidate.project_name or '-'}</td>
#         <td>{candidate.task or '-'}</td><td>{candidate.pending_for or '-'}</td></tr>"""

#     data += "</table>"
#     subject = f"Candidates Submitted - {nowdate()}"
#     message = f"""
#     Dear Sir/Madam,<br><br>
#     Kindly find the below list of candidates you submitted today:<br><br>{data if data else ''}<br><br>
#     Thanks & Regards,<br>TEAM ERP<br>
#     <i>This email has been automatically generated. Please do not reply</i>
#     """

#     frappe.sendmail(
#         # recipients=[user_id],
#         recipients=["divya.p@groupteampro.com"],
#         subject=subject,
#         message=message,
#         attachments=[
#             {"fname": filename, "fcontent": file_content},
#             {"fname": pdffilename, "fcontent": pdf_content}
#         ]
#     )

# def make_xlsx(filename, user_id):
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = 'Candidates'
#     next_date=today()
#     next_dates=datetime.strptime(next_date, '%Y-%m-%d')
#     formatted_next_date=next_dates.strftime('%Y-%m-%d')
#     # Add headers to the sheet
#     headers = ["S No", "Candidate ID", "Passport Number", "Name", "Project", "Task", "Status"]
#     ws.append(headers)

#     s_no = 0
#     candidates = frappe.get_all(
#         "Candidate",
#         filters={'submitted_date': formatted_next_date, 'candidate_created_by': user_id,'pending_for':'Submitted(Internal)'},
#         fields=["name", "passport_number", "given_name", "project_name", "task", "pending_for"]
#     )

#     for candidate in candidates:
#         s_no += 1
#         ws.append([
#             s_no, candidate.name or '-', candidate.passport_number or '-',
#             candidate.given_name or '-', candidate.project_name or '-',
#             candidate.task or '-', candidate.status or '-'
#         ])

#     # Save the workbook to a BytesIO object and return it
#     xlsx_file = BytesIO()
#     wb.save(xlsx_file)
#     xlsx_file.seek(0)
#     return xlsx_file

# def make_pdf(pdffilename, user_id):
#     html = """
#     <html>
#     <head>
#     <style>
#     table { width: 100%; border-collapse: collapse; }
#     table, th, td { border: 1px solid black; }
#     th, td { padding: 5px; text-align: left; }
#     th { background-color: #0f1568; color: white; }
#     </style>
#     </head>
#     <body>
#     <h2>Candidate Details</h2>
#     <table>
#     <tr>
#         <th>S No</th>
#         <th>Candidate ID</th>
#         <th>Passport Number</th>
#         <th>Name</th>
#         <th>Project</th>
#         <th>Task</th>
#         <th>Status</th>
#     </tr>
#     """
#     next_date=today()
#     next_dates=datetime.strptime(next_date, '%Y-%m-%d')
#     formatted_next_date=next_dates.strftime('%Y-%m-%d')
#     candidates = frappe.get_all(
#         "Candidate",
#         filters={'submitted_date': formatted_next_date, 'candidate_created_by': user_id,'pending_for':'Submitted(Internal)'},
#         fields=["name", "passport_number", "given_name", "project_name", "task", "pending_for"]
#     )

#     s_no = 0
#     for candidate in candidates:
#         s_no += 1
#         html += f"""
#         <tr>
#             <td>{s_no}</td>
#             <td>{candidate.name or '-'}</td>
#             <td>{candidate.passport_number or '-'}</td>
#             <td>{candidate.given_name or '-'}</td>
#             <td>{candidate.project_name or '-'}</td>
#             <td>{candidate.task or '-'}</td>
#             <td>{candidate.pending_for or '-'}</td>
#         </tr>
#         """

#     html += """
#     </table>
#     </body>
#     </html>
#     """

#     pdf_content = get_pdf(html)
#     return pdf_content
@frappe.whitelist()
def candidate_excel_format():
    next_date=today()
    next_dates=datetime.strptime(next_date, '%Y-%m-%d')
    formatted_next_date=next_dates.strftime('%Y-%m-%d')
    filename = "Candidate_Details_" + today() + ".xlsx"
    pdffilename = "Candidate_Details_" + today() + ".pdf"
    candidates = frappe.get_all(
        "Candidate",
        filters={'submitted_date': formatted_next_date},
        fields=["candidate_created_by"],
        group_by='candidate_created_by'
    )

    for user in candidates:
        user_id = user.candidate_created_by
        xlsx_file = make_xlsx_candidate(filename, user_id)
        pdf_content = make_pdf_candidate(pdffilename, user_id)
        candidate_status_mail_test(filename, xlsx_file.getvalue(), pdffilename, pdf_content, user_id)

def candidate_status_mail_test(filename, file_content, pdffilename, pdf_content, user_id):
    next_date=today()
    next_dates=datetime.strptime(next_date, '%Y-%m-%d')
    formatted_next_date=next_dates.strftime('%Y-%m-%d')
    data=""
    s_no = 0
    candidates = frappe.db.sql(
        """
        SELECT c.name, c.passport_number, c.given_name, c.highest_degree,
               c.total_experience, c.overseas_experience, c.current_employer,
               c.current_ctc, c.expected_ctc, c.location, c.notice_period_months,
               c.remarks_1, c.position, c.currency_ctc
        FROM `tabCandidate` c
        INNER JOIN `tabCandidate status` cs ON c.name = cs.parent
        WHERE c.candidate_created_by = %s
        AND cs.status = %s
        AND DATE(cs.sourced_date) = %s
        """,
        (user_id, "Submitted(Internal)", formatted_next_date),
        as_dict=True
    )

    grouped_candidates = {}
    for candidate in candidates:
        position = candidate.get("position", "")
        currency = candidate.get("currency_ctc", "")  # Default to SAR
        current_ctc = candidate.get("current_ctc", 0)  # Default to 0
        formatted_ctc = f"{currency} {current_ctc}" if current_ctc else " "

        if position not in grouped_candidates:
            grouped_candidates[position] = []
        grouped_candidates[position].append([
            candidate.get("name", "-"),
            candidate.get("passport_number", "-"),
            candidate.get("given_name", "-"),
            candidate.get("highest_degree", "-"),
            candidate.get("total_experience", "-"),
            candidate.get("overseas_experience", "-"),
            candidate.get("current_employer", "-"),
            formatted_ctc,
            candidate.get("expected_ctc", "-"),
            candidate.get("location", "-"),
            candidate.get("notice_period_months", "-"),
            candidate.get("remarks_1", "-"),
        ])

    # Define headers for the table
    headers = [
        "Candidate ID", "PP Number", "Candidate Name", "Qualification", 
        "Total Yrs of Exp", "Overseas Exp", "Current Employer", 
        "Current Salary", "Exp. Salary", "Current Location", 
        "Notice Period", "Remarks"
    ]

    for position, candidates in grouped_candidates.items():
        # Add position header and start table
        data += f"""
        <table class='table table-bordered' style='border: 1px solid black; border-collapse: collapse; width: 100%;'>
        <tr style='border: 1px solid black; background-color: #0f1568; color: white;'>
        <th colspan="12" style="text-align: center; font-size: 18px;">Position: {position}</th>
        </tr>
        <tr style='border: 1px solid black; background-color: #98D7F5; color: black;'>
        """
        # Add headers to the table
        for header in headers:
            data += f"<th style='border: 1px solid black;'>{header}</th>"
        data += "</tr>"

        # Add rows for each candidate under the position
        for candidate in candidates:
            data += "<tr style='border: 1px solid black;'>"
            for value in candidate:
                data += f"<td style='border: 1px solid black;'>{value}</td>"
            data += "</tr>"
        data += "</table><br>"

    subject = f"Candidates Submitted - {nowdate()}"
    message = f"""
    Dear Sir/Madam,<br><br>
    Kindly find the below list of candidates you submitted today:<br><br>{data if data else ''}<br><br>
    Thanks & Regards,<br>TEAM ERP<br>
    <i>This email has been automatically generated. Please do not reply</i>
    """

    frappe.sendmail(
        recipients=[user_id],
        # recipients=["divya.p@groupteampro.com"],
        subject=subject,
        message=message,
        attachments=[
            {"fname": filename, "fcontent": file_content},
            {"fname": pdffilename, "fcontent": pdf_content}
        ]
    )

def make_xlsx_candidate(filename, user_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Candidates'
    
    # Define column width
    for col in range(ord('A'), ord('M')):  # Columns A to L
        ws.column_dimensions[chr(col)].width = 20

    # Define headers
    headers = ["Candidate ID", "PP Number", "Candidate Name", "Qualification", 
               "Total Yrs of Exp", "Overseas Exp", "Current Employer", 
               "Current Salary", "Exp. Salary", "Current Location", 
               "Notice Period", "Remarks"]

    # Define border style
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Fetch and group candidates by position
    position_candidates = get_data_grouped_by_position_candidate(user_id)
    
    # Debug: Check if any positions are retrieved
    print(f"Positions found: {len(position_candidates)}")
    
    if not position_candidates:
        print("No candidates found for the given user.")
    
    for position, candidates in position_candidates.items():
        # Add position row
        position_row = ws.max_row + 1
        ws.merge_cells(start_row=position_row, start_column=1, end_row=position_row, end_column=12)
        cell = ws.cell(row=position_row, column=1)
        cell.value = f"{position}"
        cell.fill = PatternFill(start_color="0F1568", end_color="0F1568", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

        # Add headers
        header_row = ws.max_row + 1
        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=header_row, column=col_num)
            cell.value = header
            cell.fill = PatternFill(start_color="98D7F5", end_color="98D7F5", fill_type="solid")
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # Add candidate rows
        for candidate in candidates:
            row_num = ws.max_row + 1
            for col_num, value in enumerate(candidate, start=1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
                cell.border = thin_border  # Apply border to each cell

        # Add an empty row for separation
        ws.append([])

    # Save the file into a BytesIO stream
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)
    return xlsx_file

from frappe.utils.pdf import get_pdf
def make_pdf_candidate(pdffilename, user_id):
    html = """
    <html>
    <head>
    <style>
    table { width: 100%; border-collapse: collapse; }
    table, th, td { border: 1px solid black; }
    th, td { padding: 5px; text-align: left; }
    th { background-color: #98D7F5; color: black; }  /* Header background color */
    td.position { background-color: #0F1568; color: white; } /* Position row background color */
    </style>
    </head>
    <body>
    <h2>Candidate Details</h2>
    """
    
    next_date = today()
    next_dates = datetime.strptime(next_date, '%Y-%m-%d')
    formatted_next_date = next_dates.strftime('%Y-%m-%d')
    
    candidates = frappe.db.sql(
        """
        SELECT c.name, c.passport_number, c.given_name, c.highest_degree,
               c.total_experience, c.overseas_experience, c.current_employer,
               c.current_ctc, c.expected_ctc, c.location, c.notice_period_months,
               c.remarks_1, c.position, c.currency_ctc
        FROM `tabCandidate` c
        INNER JOIN `tabCandidate status` cs ON c.name = cs.parent
        WHERE c.candidate_created_by = %s
        AND cs.status = %s
        AND DATE(cs.sourced_date) = %s
        """,
        (user_id, "Submitted(Internal)", formatted_next_date),
        as_dict=True
    )

    # Group candidates by position
    grouped_candidates = {}
    for candidate in candidates:
        position = candidate.get("position", "")
        currency = candidate.get("currency_ctc", "")  # Default to SAR
        current_ctc = candidate.get("current_ctc", 0)  # Default to 0
        formatted_ctc = f"{currency} {current_ctc}" if current_ctc else " "

        if position not in grouped_candidates:
            grouped_candidates[position] = []
        grouped_candidates[position].append([ 
            candidate.get("name", "-"),
            candidate.get("passport_number", "-"),
            candidate.get("given_name", "-"),
            candidate.get("highest_degree", "-"),
            candidate.get("total_experience", "-"),
            candidate.get("overseas_experience", "-"),
            candidate.get("current_employer", "-"),
            formatted_ctc,
            candidate.get("expected_ctc", "-"),
            candidate.get("location", "-"),
            candidate.get("notice_period_months", "-"),
            candidate.get("remarks_1", "-"),
        ])

    # Define table headers
    headers = [
        "Candidate ID", "PP Number", "Candidate Name", "Qualification", 
        "Total Yrs of Exp", "Overseas Exp", "Current Employer", 
        "Current Salary", "Exp. Salary", "Current Location", 
        "Notice Period", "Remarks"
    ]

    # Add data position-wise to the HTML
    for position, candidates in grouped_candidates.items():
        # Add position header with custom color
        html += f"""
        <table>
        <tr>
        <td class="position" colspan="12">{position}</td>
        </tr>
        """
        
        # Add table headers
        html += "<tr>"
        for header in headers:
            html += f"<th>{header}</th>"
        html += "</tr>"

        # Add candidate rows
        for candidate in candidates:
            html += "<tr>"
            for value in candidate:
                html += f"<td>{value}</td>"
            html += "</tr>"
        html += "</table>"

    html += """
    </body>
    </html>
    """

    # Generate PDF from the HTML
    pdf_content = get_pdf(html)
    return pdf_content

def get_data_grouped_by_position_candidate(user_id):
    """
    Fetch candidate data grouped by position using SQL query.
    """
    data = {}
    next_date=today()
    next_dates=datetime.strptime(next_date, '%Y-%m-%d')
    formatted_next_date=next_dates.strftime('%Y-%m-%d')

    # Execute the SQL query to fetch candidates
    candidates = frappe.db.sql(
        """
        SELECT c.name, c.passport_number, c.given_name, c.highest_degree,
               c.total_experience, c.overseas_experience, c.current_employer,
               c.current_ctc, c.expected_ctc, c.location, c.notice_period_months,
               c.remarks_1, c.position, c.currency_ctc
        FROM `tabCandidate` c
        INNER JOIN `tabCandidate status` cs ON c.name = cs.parent
        WHERE c.candidate_created_by = %s
        AND cs.status = %s
        AND DATE(cs.sourced_date) = %s
        """,
        (user_id, "Submitted(Internal)", formatted_next_date),
        as_dict=True
    )

    # Group candidates by position
    for candidate in candidates:
        position = candidate.get("position", "")
        currency = candidate.get("currency_ctc", "")  # Default to SAR if not specified
        current_ctc = candidate.get("current_ctc", 0)  # Default to 0 if not specified
        formatted_ctc = f"{currency} {current_ctc}" if current_ctc else " "

        if position not in data:
            data[position] = []
        data[position].append([
            candidate.name, candidate.passport_number, candidate.given_name,
            candidate.highest_degree, candidate.total_experience, 
            candidate.overseas_experience, candidate.current_employer,
            formatted_ctc, candidate.expected_ctc, candidate.location, 
            candidate.notice_period_months, candidate.remarks_1
        ])

    return data


# Daily DPR Mail Trigger # 

import frappe
from datetime import datetime
from collections import defaultdict

# @frappe.whitelist()
# def dpr_mail():
#     current_date = datetime.now().strftime("%d-%m-%Y")
    
    
#     table_style = 'style="width: 100%; border-collapse: collapse;"'
#     th_style = 'style="background-color:#063970; color:white; text-align:center; padding: 5px;"'
#     td_style = 'style="text-align:center; padding: 5px;"'
    
    
#     dpr_data_template = '''
#     <table {0} border="1">
#         <thead>
#             <tr>
#                 <th {1} colspan="12">DPR - {2}</th>
#             </tr>
#             <tr>
#                 <th {1}>S.NO</th>
#                 <th {1}>Task ID</th>
#                 <th {1}>Project Name</th>
#                 <th {1}>Subject</th>
#                 <th {1}>CB</th>
#                 <th {1}>Priority</th>
#                 <th {1}>Status</th>
#                 <th {1}>Revisions</th>
#                 <th {1}>AT</th>
#                 <th {1}>ET</th>
#                 <th {1}>RT</th>
#                 <th {1}>Allocated On</th>
#             </tr>
#         </thead>
#         <tbody>
#     '''.format(table_style, th_style, current_date)

#     employees = frappe.db.get_all("Employee", filters={'status': 'Active', 'department': 'ITS - THIS'}, fields=['*'])
#     for emp in employees:
#         dpr_data = dpr_data_template
#         tasks = frappe.db.get_all("Task", filters={'status': 'Working', 'service': 'IT-SW'}, 
#                                   fields=["name", "project_name", "subject", "cb", "priority", "status", "revisions", "actual_time", "expected_time", "rt", "custom_allocated_on"])
        
#         tasks_sorted = sorted(tasks, key=lambda x: (x.get('cb', ''), x.get('project_name', ''), x.get('priority', '')))
        
#         for idx, task in enumerate(tasks_sorted, start=1):
#             actual_time = task.get('actual_time', 0)
#             rounded_actual_time = round(actual_time, 2) if actual_time else 0
#             custom_allocated_on = task.get('custom_allocated_on')
#             formatted_allocated_on = datetime.strftime(custom_allocated_on, '%d-%m-%Y') if custom_allocated_on else '-'
#             dpr_data += '''
#                 <tr>
#                     <td {0}>{1}</td>
#                     <td {0}>{2}</td>
#                     <td {0}>{3}</td>
#                     <td {0}>{4}</td>
#                     <td {0}>{5}</td>
#                     <td {0}>{6}</td>
#                     <td {0}>{7}</td>
#                     <td {0}>{8}</td>
#                     <td {0}>{9}</td>
#                     <td {0}>{10}</td>
#                     <td {0}>{11}</td>
#                     <td {0}>{12}</td>
#                 </tr>
#             '''.format(td_style, idx, task.get('name', ''), task.get('project_name', ''), task.get('subject', ''), task.get('cb', ''), 
#                        task.get('priority', ''), task.get('status', ''), task.get('revisions', ''), rounded_actual_time, 
#                        task.get('expected_time', ''), task.get('rt', ''), formatted_allocated_on)
        
#         dpr_data += '''
#                 </tbody>
#             </table>
#             <br><br>
#         '''

#         frappe.sendmail(
#             recipients=[emp.user_id],
#             subject='DPR Report - {}'.format(current_date),
#             message=dpr_data
#         )

# @frappe.whitelist()
# def create_mail_for_dpr():
#     job = frappe.db.exists('Scheduled Job Type', 'dpr_mail')
#     if not job:
#         sjt = frappe.new_doc("Scheduled Job Type")
#         sjt.update({
#             "method": 'checkpro.custom.dpr_mail',
#             "frequency": 'Cron',
#             "cron_format": "0 1 * * * "
#         })
#         sjt.save(ignore_permissions=True) 

@frappe.whitelist()
def task_mail():
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    
    table_style = 'style="width: 100%; border-collapse: collapse;"'
    th_style = 'style="background-color:#063970; color:white; text-align:center; padding: 5px;"'
    td_style = 'style="text-align:center; padding: 5px;"'    
    open_issues_data_template = '''

    <table {0} border="1">
        <thead>
            <tr>
                <th {1} colspan="5">Open Issues - {2}</th>
            </tr>
            <tr>
                <th {1}>S.NO</th>
                <th {1}>Subject</th>
                <th {1}>Customer</th>
                <th {1}>Project</th>
                <th {1}>Count</th>
            </tr>
        </thead>
        <tbody>
    '''.format(table_style, th_style, current_date)

    assigned_to_list = frappe.db.sql("""
        SELECT project, subject, customer
        FROM `tabIssue`
        WHERE status = 'Open'
    """, as_dict=True)

    issue_counts = {}
    for issue in assigned_to_list:
        project = issue['project']
        if project not in issue_counts:
            issue_counts[project] = {'count': 0, 'subject': issue['subject'], 'customer': issue['customer']}
        issue_counts[project]['count'] += 1

    total_count = 0
    for idx, (project, data) in enumerate(issue_counts.items(), start=1):
        total_count += data['count']
        open_issues_data_template += '''
        <tr>
             <td {0}>{1}</td>
             <td {0}>{2}</td>
             <td {0}>{3}</td>
             <td {0}>{4}</td>
             <td {0}>{5}</td>
        </tr>'''.format(td_style, idx, data['subject'], data['customer'], project, data['count'])

    open_issues_data_template += '''
        <tr>
            <td {0} colspan="4"><strong>Total</strong></td>
            <td {0}><strong>{1}</strong></td>
        </tr>'''.format(td_style, total_count)

    open_issues_data_template += '''
            </tbody>
        </table>
        <br><br>
    '''
    
    
    open_meetings_data_template = '''
    <table {0} border="1">
        <thead>
            <tr>
                <th {1} colspan="3">Open Meetings - {2}</th>
            </tr>
            <tr>
                <th {1}>S.NO</th>
                <th {1}>Project</th>
                <th {1}>Count</th>
            </tr>
        </thead>
        <tbody>
    '''.format(table_style, th_style, current_date)

    assigned_to_list = frappe.db.get_all('Meeting', 
        filters={'status': ['not in', ['Completed', 'Cancelled']], 'custom_department': 'ITS - THIS'}, 
        fields=['project'])

    meeting_counts = {
        item['project']: frappe.db.count('Meeting', 
            filters={'status': ['not in', ['Completed', 'Cancelled']],'custom_department': 'ITS - THIS', 'project': item['project']})
        for item in assigned_to_list
    }

    total_count = 0
    for idx, (project, count) in enumerate(meeting_counts.items(), start=1):
        total_count += count
        open_meetings_data_template += '''
        <tr>
             <td {0}>{1}</td>
             <td {0}>{2}</td>
             <td {0}>{3}</td>
        </tr>'''.format(td_style, idx, project, count)

    open_meetings_data_template += '''
        <tr>
            <td {0} colspan="2"><strong>Total</strong></td>
            <td {0}><strong>{1}</strong></td>
        </tr>'''.format(td_style, total_count)

    open_meetings_data_template += '''
            </tbody>
        </table>
        <br><br>
    '''
    
    
    task_rt_data_template = '''
    <table {0} border="1">
        <thead>
            <tr>
                <th {1} colspan="3">Task Available RT - {2}</th>
            </tr>
            <tr>
                <th {1}>S.NO</th>
                <th {1}>CB</th>
                <th {1}>Count</th>
            </tr>
        </thead>
        <tbody>
    '''.format(table_style, th_style, current_date)
    
    tasks = frappe.db.get_all("Task", filters={'status': ['in', ['Open', 'Overdue', 'Working']], 'cb': ['not in', ['SM', 'JA']], 'service': 'IT-SW'}, fields=["cb", "rt"])
    
    cb_summary = defaultdict(lambda: {'total_rt': 0})
    
    for task in tasks:
        cb = task.get('cb', '')
        rt = task.get('rt', 0)
        
        cb_summary[cb]['total_rt'] += rt
    
    total_rt_overall = 0
    data_rows = ''
    
    for idx, (cb, summary) in enumerate(sorted(cb_summary.items()), start=1):
        total_rt = summary['total_rt']
        total_rt_overall += total_rt
        data_rows += '''
            <tr>
                <td {0}>{1}</td>
                <td {0}>{2}</td>
                <td {0}>{3}</td>
            </tr>
        '''.format(td_style, idx, cb, total_rt)
    
    task_rt_data_template += data_rows
    
    task_rt_data_template += '''
            <tr>
                <td {0} colspan="2"><strong>Total</strong></td>
                <td {0}><strong>{1}</strong></td>
            </tr>
            </tbody>
        </table>
        <br><br>
    '''.format(td_style, total_rt_overall)
    
    
    combined_data = '''
    <html>
    <body>
    '''
    
    combined_data += open_issues_data_template + open_meetings_data_template + task_rt_data_template
    
    combined_data += '''
    </body>
    </html>
    '''
    
    frappe.sendmail(
            recipients=['siva.m@groupteampro.com','abdulla.pi@groupteampro.com','dineshbabu.k@groupteampro.com','anil.p@groupteampro.com'],
            subject='Task-Issue-Meeting - {}'.format(current_date),
            message=combined_data
        )

@frappe.whitelist()
def rename_case(doc, method):
    # Split batch parts
    batch_parts = doc.batch.split('-')
    batch_suffix = "-".join(batch_parts[1:])
    date_ddmmyy = batch_suffix[:6]
    batch_part = doc.batch.split('-')
    batch_suff ="-".join(batch_parts[2:])
    date_dd =  batch_suff[:5]
    # Create prefix for search
    case_prefix = f"{doc.customer_short_code}-{date_ddmmyy}-{date_dd}"
    # Query to get the highest series number for the given prefix
    highest_case = frappe.db.sql("""
        SELECT name FROM `tabCase`
        WHERE name LIKE %s
        ORDER BY name DESC
        LIMIT 1
    """, (case_prefix + '%'), as_dict=True)

    if highest_case:
        highest_series = int(highest_case[0]['name'].split('-')[-1]) 
        new_series = highest_series + 1
    else:
        new_series = 1

    series_str = str(new_series).zfill(5)
    case_id = f"{doc.customer_short_code}-{date_ddmmyy}-{date_dd}-{series_str}"
    frappe.rename_doc("Case", doc.name, case_id, force=1)


@frappe.whitelist()
def total_wh_appointment(in_time, name):
    current_datetime_str = frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S')
    wh = total_appointment(current_datetime_str, in_time)
    
    data_list = [{'wh': wh, 'current_datetime_str': current_datetime_str}]
    
    return data_list

def total_appointment(out_time_str, in_time_str):
    out_time = datetime.strptime(out_time_str, '%Y-%m-%d %H:%M:%S')
    in_time = datetime.strptime(in_time_str, '%Y-%m-%d %H:%M:%S')
    time_difference = out_time - in_time
    
    hours = int(time_difference.total_seconds() // 3600)
    minutes = int((time_difference.total_seconds() % 3600) // 60)
    seconds = int(time_difference.total_seconds() % 60)
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    return formatted_time

@frappe.whitelist()
def total_wh_hrs(in_time, out_time):
    if in_time and out_time:
        wh = time_diff_in_hours(out_time, in_time)
        return wh

def time_diff_in_hours(out_time_str, in_time_str):
    out_time = datetime.strptime(out_time_str, '%Y-%m-%d %H:%M:%S')
    in_time = datetime.strptime(in_time_str, '%Y-%m-%d %H:%M:%S')
    time_difference = out_time - in_time
    
    hours = time_difference.total_seconds() / 3600
    return round(hours, 2)


@frappe.whitelist()
def closure_mail_issue(subject,id,live,created_by,priority,assigned=None,project=None,action_taken=None,proof=None,domain=None):
    project_spoc=''
    reports_to=''
    report=''
    if project:
        project_spoc=frappe.db.get_value("Project",{'name':project},['spoc'])
        reports_to_mail=frappe.db.get_value("Employee",{'user_id':project_spoc},['reports_to'])
        reports_to=frappe.db.get_value("Employee",{'name':reports_to_mail},['user_id'])
    if assigned:
        report_mail=frappe.db.get_value("Employee",{'user_id':assigned},['reports_to'])
        report=frappe.db.get_value("Employee",{'name':report_mail},['user_id'])
    data = ''
    data += f"<table width='100%' style='border-collapse: collapse; border: 1px solid black; text-align: center;'>\
    <tr><td colspan='2' style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black;'><b>Issue Closure Review</b></td></tr>\
    <tr style='text-align: left;'><td width='25%'style='border: 1px solid black;'><b>Issue ID</b></td><td style='border: 1px solid black;'>{id}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Issue Statement</b></td><td style='border: 1px solid black;'>{subject}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Issue Raised By</b></td><td style='border: 1px solid black;'>{created_by}</td></tr>\
    <tr style='text-align: left;'><td width='25%'style='border: 1px solid black;'><b>Project</b></td><td style='border: 1px solid black;'>{project}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Priority</b></td><td style='border: 1px solid black;'>{priority}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Action Taken</b></td><td style='border: 1px solid black;'>{action_taken}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Live At</b></td><td style='border: 1px solid black;'>{live}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Domain</b></td><td style='border: 1px solid black;'>{domain}</td></tr>\
    <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Proof</b></td><td style='border: 1px solid black;'><a href='https://erp.teamproit.com/{proof}' target='_blank'>Link to Proof</a></td></tr></table>"


    frappe.sendmail(
        sender=assigned,
        # recipients='divya.p@groupteampro.com',  
        recipients=project_spoc,
        cc=[reports_to,report,assigned],
        subject='Issue : %s Closure Review Document' % id,
        message = """
        <b>Dear Patron,<br><br>Greeting !!!</b><br><br>
           The attached Issue has been completed by Development and forwarded for your kind review, please confirm if it satisfies all your requirement and Mark the Issue Status as Client Review / Completed or if you feel it is still pending for some action please change the status as “OPEN”<br><br>
        {}<br><br>
        Thanks & Regards,<br>TEAM ERP<br>
        
        <i>This email has been automatically generated. Please do not reply</i>
        """.format(data)
    )
    

@frappe.whitelist()
def task_mail_notification():
    projects=frappe.get_all("Project",{'status':'Open','service':('in',['REC-D','REC-I'])},['*'])
    table = '<table text-align="center" border="1" width="100%" style="border-collapse: collapse;text-align: left;">'
    row=0
    for project in projects:
        tasks = frappe.get_all("Task", {'status': ('in', ['Open', 'Working','Overdue','Pending Review']),'project':project.name,'service':('in',['REC-D','REC-I'])},['*'])
        candidate_count=frappe.db.count("Candidate", {'project':project.name,'pending_for':('not in',['IDB','Sourced','Proposed PSL'])})
        if candidate_count>0:
            if row>0:
                table += """<tr><td style="border: none; border-left: hidden; border-right: hidden; height: 40px;" colspan=6></td></tr>"""
            # table+="""<tr><td style="border-left: hidden; border-right: hidden; border-top:hidden; border-bottom:hidden;"colspan=6></td></tr>"""
            table+="""<tr><td style="border-left: none; border-right: none;text-align: left;"colspan=2>Customer Name</td><td style="text-align: left;" colspan=4>%s</td></tr>"""%(project.customer)
            table+="""<tr><td style="border-left: none; border-right: none;text-align: left;"colspan=2>Spoc</td><td style="text-align: left;"colspan=4>%s</td></tr>"""%(project.spoc)
            table+="""<tr><td style="border-left: none; border-right: none;text-align: left;"colspan=2>Account Manager</td><td style="text-align: left;"colspan=4>%s</td></tr>"""%(project.account_manager)
            table += '<tr style="background-color: #0f1568"><td style="width: 2%; font-weight: bold;color: white;text-align: left;">ID</td><td style="width: 1%; font-weight: bold;color: white;text-align: left;">Status</td><td style="width: 5%; font-weight: bold; color: white;text-align: left;">Given Name</td><td style="width:3%; font-weight: bold; color: white;text-align: left;">Position</td><td style="width: 3%; font-weight: bold;color: white;text-align: left;">Passport Number</td><td style="width: 2%; font-weight: bold;color: white;text-align: left;">Project</td></tr>'
        for j in tasks:
            candidate=frappe.get_all("Candidate",{'pending_for':('not in',['IDB','Sourced','Proposed PSL']),'task':j.name},['name','pending_for','given_name','position','passport_number','project'])
            for ca in candidate:
                table+="""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" % (ca.name,ca.pending_for,ca.given_name,ca.position,ca.passport_number or '-',ca.project)
                row+=1
    table += '</table>'
    frappe.sendmail(
        recipients=['sangeetha.a@groupteampro.com','lokeshkumar.a@groupteampro.com','ponkamaleshwari.i@groupteampro.com','rama.a@groupteampro.com'],
        cc=['sangeetha.s@groupteampro.com','dineshbabu.k@groupteampro.com'],
        subject='Candidate Feedback Pending Report',
        message=f"""
        <br>
         <p>As per the mail, Profile feedback pending list.</p>
        
        
          {table}<br><br>
        "This email has been automatically generated. PLEASE DONOT REPLY, Initiate further action and intimate your direct manager through email."
            <br><br>
            "With Best Wishes & Regards "
            <br><br>
            <span style="color:#203ed5;">
            "TEN – Auto Mail "
            </span>
            <br><br>
            <span style="color:#203ed5;">
                "Disclaimers:<br>
                This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you have received this email in error please notify the system manager. Please note that any views or opinions presented in this email are solely those of the author and do not necessarily represent those of the company. Finally, the recipient should check this email and any attachments for the presence of viruses. The company accepts no liability for any damage caused by any virus transmitted by this email."
            </span>
        """
    )

# @frappe.whitelist()
# def update_case_st():
    # frappe.db.sql("""update `tabEmployment` set check_status = 'Draft' where name = 'Employment-3741'""")
    # frappe.db.sql("""update `tabEmployment` set workflow_state = 'Draft' where name = 'Employment-3741'""")
    # frappe.db.sql("""update `tabEmployment` set report_status = 'YTS' where name = 'Employment-3741'""")
    # frappe.db.sql("""update `tabEmployment` set na = 1 where name = 'Employment-3741'""")
    # frappe.db.sql("""update `tabCase` set case_status = 'Case Completed' where name = 'KBL-180724-14306-00002'""")
    # frappe.db.sql("""update `tabCase` set dropped = 0 where name = 'CS-013494'""")
    # frappe.db.sql("""update `tabCase` set reason_of_drop = '' where name = 'CS-013494'""")
    # frappe.db.set_value("Case",{"name":"CYM-020924-14756-00001"},"case_status","SO Created")


@frappe.whitelist()
def update_case_so_sta():
    cases=frappe.get_all("Case",{'case_status':'SO Created','check_package':('in',['CP_TMPL_3659'])},['*'])
    i=0
    for c in cases:
        i+=1
        # print(c.name)
        frappe.db.sql("""update `tabCase` set case_status = 'To be Billed' where name = %s""",c.name)
    print(i)

@frappe.whitelist()
def create_appointment_from_sfu_lead(lead):
    data = frappe.db.get_value("Lead", {"name":lead}, ["email_id", "mobile_no"])
    return data
@frappe.whitelist()
def create_appointment_from_sfu_customer(customer):
    contact_name = frappe.db.get_value("Dynamic Link", {
        "link_doctype": "Customer",
        "link_name": customer,
        "parenttype": "Contact"
    }, "parent")
    if contact_name:
        email, mobile_no = frappe.db.get_value("Contact", contact_name, ["email_id", "mobile_no"])
        return {
            "email": email,
            "mobile_no": mobile_no
        }
    else:
        return {
            "email": None,
            "mobile_no": None
        }
        
@frappe.whitelist()
def update_appointment_in_sfu(name, customer_name):
    app = frappe.get_doc("Appointment", name)
    sfu = frappe.get_doc("Sales Follow Up", {"organization_name":customer_name})
    sfu.appointment = name
    sfu.appointment_status = app.status
    sfu.sheduled_time = app.scheduled_time
    sfu.appointment_with = app.appointment_with
    sfu.name1 = app.customer_name
    sfu.party = app.party
    sfu.phone_no = app.customer_phone_number
    sfu.details = app.customer_details
    sfu.skype_id = app.customer_skype
    sfu.email = app.customer_email
    sfu.calendar_event = app.calendar_event
    sfu.appointment_remarks = app.custom_remarks
    sfu.save()
    



@frappe.whitelist()
def create_exp_claim(doc, name):
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ['name'])
    approval_status = 'Draft'
    return employee, approval_status

@frappe.whitelist()
def retrieve_expenses(app):
    km = frappe.get_value("Appointment", {'name': app}, ['custom_distance'])
    km = int(km)
    a = 0
    return km, a


@frappe.whitelist()
def validate_expense(app):
    frappe.set_value("Appointment", app, "custom_expense_claimed", 1)

# @frappe.whitelist()
# def update_st_test():
    # frappe.db.set_value("Social Media",{"name":"Social Media-240"},"check_status","Draft")
    # frappe.db.set_value("Education Checks",{"name":"Education Checks-20662"},"dropped_date","")
    # frappe.db.set_value("Criminal",{"name":"Criminal-2092"},"check_status","Report Completed")
    # frappe.db.set_value("Criminal",{"name":"Criminal-2092"},"workflow_state","Report Completed")
    # frappe.db.set_value("Education Checks",{"name":"Education Checks-20988"},"report_status","Not Applicable")
    # frappe.db.set_value("Case",{"name":"PMM-211124-15169-00010"},"case_status","SO Created")
   



@frappe.whitelist()
def update_doc_in_sfu(doc, method):
    # appointment = frappe.db.sql("""select name from `tabAppointment` where customer_name = '%s'""" %(doc.organization_name), as_dict=1)
    # frappe.log_error(message=appointment, title="Appointment")
    # doc.appointment_clone = appointment[0]['name']
    # doc.save()
    if doc.appointment_with == 'Lead':
        lead = frappe.db.get_value("Lead", {"company_name": doc.customer_name}, "name")
        if not doc.party:
            if not lead:
                new_lead = frappe.get_doc({
                    "doctype": "Lead",
                    "company_name": doc.customer_name,
                    "status": "Lead",
                    "lead_owner": frappe.session.user,
                    "email_id": doc.customer_email,
                    "mobile_no": doc.customer_phone_number
                })
                new_lead.insert(ignore_permissions=True)
                frappe.msgprint("Lead Created Successfully")
            else:
                frappe.msgprint("Lead Exists")
        sfu = frappe.db.get_value("Sales Follow Up", {"organization_name": doc.customer_name}, "name")
        
        if not sfu:
            new_sfu = frappe.get_doc({
                "doctype": "Sales Follow Up",
                "organization_name": doc.customer_name,
                "follow_up_to": "Appointment",
                "account_manager": frappe.session.user,
                "lead_owner": frappe.session.user,
                "appointment_clone": doc.name,
                "appointments":doc.name,
                "appointment_date":doc.scheduled_time
            })
            new_sfu.insert(ignore_permissions=True)
            frappe.msgprint("Sales Follow Up Created Successfully")
        else:
            frappe.msgprint("Sales Follow Up Exists")


# @frappe.whitelist()
# def case_status_update_exisiting():
#     filename='06cc110038Case Status.csv'
#     from frappe.utils.file_manager import get_file
#     filepath = get_file(filename)
#     pps = read_csv_content(filepath[1])
#     ind=0
#     for pp in pps:
#         frappe.db.set_value("Case",{"name":pp[0]},"case_status",pp[1])
#         ind+=1
#         print(pp[0])
#         print(pp[1])
#     print(ind)

#For downloading Timesheet status as excel
@frappe.whitelist()
def make_time_sheet():
    args = frappe.local.form_dict
    filename = args.name
    test = build_xlsx_response(filename)

def make_xlsx_timesheet(data, sheet_name=None, wb=None, column_widths=None):
    args = frappe.local.form_dict
    column_widths = column_widths or []
    if wb is None:
        wb = openpyxl.Workbook()
    ws = wb.create_sheet(sheet_name, 0)
    doc = frappe.get_doc("Timesheet",args.name)
    
    if doc:
        ws.append(["Document Name","Document ID","Subject","Project Name","CB","Status","ET","AT"])
        cb=''
        for i in doc.timesheet_summary:
            if i.document=="Task":
                cb = frappe.db.get_value("Task",{"name":i.id},["cb"])
                status =frappe.db.get_value("Task",{"name":i.id},["status"])
                type =frappe.db.get_value("Employee",{"name":doc.employee},["custom_dept_type"])
                if type == "OPS":
                    et = frappe.db.get_value("Task",{"name":i.id},["expected_time"])
                elif type == "CS":
                    et = frappe.db.get_value("Task",{"name":i.id},["pr_expected_time"])
                else:
                    et = 0
            else:
                status = frappe.db.get_value("Issue",{"name":i.id},["custom_issue_status"])
                et = 0
            ws.append([i.document,i.id,i.subject,i.project,cb,status,round(et,2),round(i.tu,2)])
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    return xlsx_file

def build_xlsx_response(filename):
    xlsx_file =make_xlsx_timesheet(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary' 


@frappe.whitelist()
def update_sfp_type():
    sales=frappe.db.get_all("Sales Follow Up",{'account_manager':['!=',''],'lead_owner':['!=','']},["*"])
    count=0
    for i in sales:
        # owner=frappe.db.get_value("Customer",{'name':i.customer},['account_manager'])
        # frappe.db.set_value("Sales Follow Up",i.name,'account_manager_lead_owner',owner)
        # frappe.db.set_value("Sales Follow Up",i.name,'party_from',"Customer")
        frappe.db.set_value("Sales Follow Up",i.name,'account_manager_lead_owner',i.account_manager)
        count+=1
    print(count)

# @frappe.whitelist()
# def batch_status_update_exisiting():
#     filename='36d1fb5d397f410Case Update.csv'
#     from frappe.utils.file_manager import get_file
#     filepath = get_file(filename)
#     pps = read_csv_content(filepath[1])
#     ind=0
#     for pp in pps:
#         frappe.db.set_value("Case",{"name":pp[0]},"case_status",pp[1])
#         ind+=1
#         print(pp[0])
#         print(pp[1])
#     print(ind)


# @frappe.whitelist()
# def batch_status_update_exisiting():
#     filename='5493e09f59Custom Field (2).csv'
#     from frappe.utils.file_manager import get_file
#     filepath = get_file(filename)
#     pps = read_csv_content(filepath[1])
#     ind=0
#     for pp in pps:
#         invoice = frappe.new_doc("Custom Field")
#         invoice.dt = pp[0]
#         invoice.fieldname = pp[1]
#         invoice.fieldtype = pp[2]
#         invoice.options = pp[3]
#         invoice.insert_after = pp[4]
#         invoice.label =pp[5]
#         invoice.save()
#         # frappe.db.set_value("",{"name":pp[0]},"batch_status",pp[1])
#         ind+=1
#         # print(pp[0])
#         # print(pp[1])
#     print(ind)

@frappe.whitelist()
def batch_status_update_in_batch(doc,method):
    cases=frappe.db.get_all("Case",{"batch":doc.batch},["*"])
    case_sts=[]
    tat_status=[]
    batch_status=''
    for i in cases:
        case_sts.append(i.case_status)
        tat_status.append(i.tat_monitor)
        if any(status == "Draft" for status in case_sts):
            if any(tat=="In TAT" for tat in tat_status):
                batch_status="Open"
            elif any(tat=="Out TAT" for tat in tat_status):
                batch_status="Overdue"
            else:
                batch_status="Open"
        elif  any(status == "Entry-Insuff" for status in case_sts):
            if any(tat=="Out TAT" for tat in tat_status):
                batch_status="Overdue with Insuff"
            elif any(tat=="In TAT" for tat in tat_status):
                batch_status="Open with Insuff"
        elif any(status == "Execution-Insuff" for status in case_sts):
            if any(tat=="In TAT" for tat in tat_status):
                batch_status="Open with Insuff"
            elif any(tat=="Out TAT" for tat in tat_status):
                batch_status="Overdue with Insuff"
        elif any(status == "Entry-QC" for status in case_sts):
            if any(tat=="In TAT" for tat in tat_status):
                batch_status="Open"
            elif any(tat=="Out TAT" for tat in tat_status):
                batch_status="Overdue"
        elif any(status == "Entry Completed" for status in case_sts):
            if any(tat=="Out TAT" for tat in tat_status):
                batch_status="Overdue"
            elif any(tat=="In TAT" for tat in tat_status):
                batch_status="Open"
        elif any(status == "Execution" for status in case_sts):
            if any(tat=="Out TAT" for tat in tat_status):
                batch_status="Overdue"
            elif any(tat=="In TAT" for tat in tat_status):
                batch_status="Open"
        elif any(status == "Case Report Completed" or status == "Case Completed" or status == "To be Billed" or status == "SO Created" or status == "Drop" or status=="Generate Report" for status in case_sts):
            batch_status="Completed"
    frappe.db.set_value("Batch",doc.batch,"batch_status",batch_status)

# @frappe.whitelist()
# def update_case_status_today():
#     frappe.db.set_value("Case",{"name":"SHF-100924-14784-00035"},"case_status","SO Created")

@frappe.whitelist()
def send_mail_for_nc(cause, id, allocated, subject, project, revision, service, spoc, domain, live,dev_spoc=None):
    if service == 'IT-SW':
        reports = frappe.db.get_value("Employee", {'user_id': allocated}, ['reports_to'])
        reports_to = frappe.db.get_value("Employee", {'name': reports}, ['user_id'])
        tl=frappe.db.get_value("Employee",{'user_id':allocated},["custom_tl"])
        if tl:
            tl_mail=frappe.db.get_value("Employee",{'name':tl},['user_id'])
        data = f"""
        <table width='100%' style='border-collapse: collapse; border: 1px solid black; text-align: center;'>
            <tr>
                <td colspan='2' style='text-align: center; background-color: #0f1568; color: white; font-size: 17px; border: 1px solid black;'>
                    <b>Task Re-Open Note</b>
                </td>
            </tr>
            <tr style='text-align: left;'>
                <td width='25%'style='border: 1px solid black;'><b>Task ID</b></td>
                <td style='border: 1px solid black;'><a href='https://erp.teamproit.com/app/task/{id}' target='_blank'>{id}</a></td>
            </tr>

            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Task Statement</b></td>
                <td style='border: 1px solid black;'>{subject}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Project</b></td>
                <td style='border: 1px solid black;'>{project}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Task Raised By</b></td>
                <td style='border: 1px solid black;'>{reports_to}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Task Developed By</b></td>
                <td style='border: 1px solid black;'>{allocated}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Live At</b></td>
                <td style='border: 1px solid black;'>{live}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Domain</b></td>
                <td style='border: 1px solid black;'>{domain}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Re-Open Count</b></td>
                <td style='border: 1px solid black;'>{revision}</td>
            </tr>
            <tr style='text-align: left;'>
                <td style='border: 1px solid black;'><b>Re-Open Remarks</b></td>
                <td style='border: 1px solid black;'>{cause}</td>
            </tr>
        </table>
        """
        
        frappe.sendmail(
            sender=frappe.session.user,
            # recipients='divya.p@groupteampro.com',
            recipients=spoc,
            cc=[reports_to,allocated,'anil.p@groupteampro.com',dev_spoc,"dineshbabu.k@groupteampro.com",tl_mail],
            subject=f'Task : {id} Re-open: Forward for Re-Open',
            message=f"""
                <b>Dear Patron,<br><br>Greeting !!!</b><br><br>
                The attached Task has been re-opened and forwarded for your kind reference<br><br>
                {data}<br><br>
                Thanks & Regards,<br>TEAM ERP<br>
                <i>This email has been automatically generated. Please do not reply</i>
            """
        )


import frappe

@frappe.whitelist()
def update_case_status_in_batch(doc, method):
    batch = frappe.get_doc("Batch", {"name": doc.batch})
    batch.casewise_status = []
    cases = frappe.db.get_all("Case", filters={"batch": doc.batch}, fields=["name", "case_status"])
    completed = 0
    insuff = 0
    pending = 0
    drop=0
    for case in cases:
        batch.append("casewise_status", {
            "case_id": case["name"],
            "case_status": case["case_status"]
        })
        if case["case_status"] in ["Case Completed","To be Billed","SO Created","Case Report Completed","Generate Report"]:
            completed += 1
        elif case["case_status"] in ["Entry-Insuff","Execution-Insuff"]:
            insuff += 1
        elif case["case_status"] in ["Drop"]:
            drop+=1
        else:
            pending += 1
        batch.comp=completed
        batch.insuff=insuff
        batch.pending=pending
        batch.custom_drop=drop
    batch.save()
    frappe.db.commit()


@frappe.whitelist()
def update_case_status_existing_batch():
    batches = frappe.get_all(
        "Batch", 
       filters={"batch_status": "Completed", "pending": [">", 0]},
        fields=["name"]
    )
    ind=0
    for batch_data in batches:
        ind+=1
        print(batch_data)
        batch = frappe.get_doc("Batch", batch_data["name"])
        batch.casewise_status = []
        cases = frappe.db.get_all(
            "Case", 
            filters={"batch": batch.name}, 
            fields=["name", "case_status"]
        )
        completed = 0
        insuff = 0
        pending = 0
        case=0
        drop=0
        for case in cases:
            if case.case_status in ["Case Completed","To be Billed","SO Created","Case Report Completed","Generate Report"]:
                completed += 1
            elif case.case_status in ["Entry-Insuff","Execution-Insuff"]:
                insuff += 1
            elif case["case_status"] in ["Drop"]:
                drop+=1
            else:
                pending += 1
            batch.append("casewise_status", {
                "case_id": case["name"],
                "case_status": case["case_status"]
            })
            batch.comp=completed
            batch.insuff=insuff
            batch.pending=pending
            batch.custom_drop=drop

            print(completed)
            print(insuff)
            print(pending)
        batch.save()
    frappe.db.commit()

# @frappe.whitelist()
# def task_mail_notification_status ():
#     job = frappe.db.exists('Scheduled Job Type','update_case_status_existing_batch')
#     if not job:
#         task = frappe.new_doc("Scheduled Job Type")
#         task.update({
#             "method": 'checkpro.custom.update_case_status_existing_batch',
#             "frequency": 'Cron',
#             "cron_format": '0 0 * * *'
#         })
#         task.save(ignore_permissions=True)

# @frappe.whitelist()
# def batch_status_update_in_test():
#     batch=frappe.db.get_all("Batch",{"batch_status":"Open"},["*"])
#     for j in batch:
#         cases=frappe.db.get_all("Case",{"batch":j.name},["*"])
#         case_sts=[]
#         tat_status=[]
#         batch_status=''
#         for i in cases:
#             case_sts.append(i.case_status)
#             tat_status.append(i.tat_monitor)
#             if any(status == "Draft" for status in case_sts):
#                 batch_status="Open"
#             elif any(status == "Entry-Insuff" for status in case_sts):
#                 batch_status="Open with Insuff"
#             elif any(status == "Execution-Insuff" for status in case_sts):
#                 batch_status="Open with Insuff"
#             elif any(status == "Entry-QC" for status in case_sts):
#                 batch_status="Open"
#             elif any(status == "Execution" for status in case_sts):
#                 batch_status="Open"
#             elif any(status == "Entry Completed" for status in case_sts):
#                 batch_status="Open"
#             elif  any(status == "Entry-Insuff" or status == "Execution-Insuff"  for status in case_sts):
#                 if any(tat=="Out TAT" for tat in tat_status):
#                     batch_status="Overdue with Insuff"
#             elif any(status == "Entry-Insuff" or status == "Execution-Insuff"  for status in case_sts):
#                 if any(tat=="In TAT" for tat in tat_status):
#                     batch_status="Open with Insuff"
#             elif any(status == "Entry Completed" or status == "Execution" or status == "Draft"  for status in case_sts):
#                 if any(tat=="In TAT" for tat in tat_status):
#                     batch_status="Open"
#             elif any(status == "Entry Completed" or status == "Execution" or status == "Draft"  for status in case_sts):
#                 if any(tat=="Out TAT" for tat in tat_status):
#                     batch_status="Overdue"
#             elif any(status == "Case Report Completed" or status == "Case Completed" or status == "To be Billed" or status == "SO Created" or status == "Drop" for status in case_sts):
#                 batch_status="Completed"
#         frappe.db.set_value("Batch",j.name,"batch_status",batch_status)


@frappe.whitelist()
def download_excel():
    filename = "Candidate Details"
    build_xlsx_response_new(filename)

def build_xlsx_response_new(filename):
    xlsx_file = make_xlsx_new(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'

def make_xlsx_new(data, sheet_name="Candidates", wb=None, column_widths=None):
    args = frappe.local.form_dict
    column_widths = column_widths or []
    
    if wb is None:
        wb = Workbook()
    ws = wb.create_sheet(sheet_name, 0)

    # Set column widths
    for col in range(ord('A'), ord('M')):  # Columns A to L
        ws.column_dimensions[chr(col)].width = 20

    # Define headers
    headers = ["Candidate ID", "PP Number", "Candidate Name", "Qualification", 
               "Total Yrs of Exp", "Overseas Exp", "Current Employer", 
               "Current Salary", "Exp. Salary", "Current Location", 
               "Notice Period", "Remarks"]

    # Define styles
    position_fill = PatternFill(start_color="0F1568", end_color="0F1568", fill_type="solid")
    position_font = Font(color="FFFFFF", bold=True)
    header_fill = PatternFill(start_color="98D7F5", end_color="98D7F5", fill_type="solid")
    header_font = Font(bold=True)
    black_border = Border(
        left=Side(border_style="thin", color="000000"),
        right=Side(border_style="thin", color="000000"),
        top=Side(border_style="thin", color="000000"),
        bottom=Side(border_style="thin", color="000000")
    )
    # Fetch candidate data grouped by positions
    position_candidates = get_data_new(args)

    for position, candidates in position_candidates.items():
        # Add position row
        position_row = ws.max_row + 1
        ws.merge_cells(start_row=position_row, start_column=1, end_row=position_row, end_column=12)
        cell = ws.cell(row=position_row, column=1)
        cell.value = f"{position}"
        cell.fill = position_fill
        cell.font = position_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = black_border

        # Add headers
        header_row = ws.max_row + 1
        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=header_row, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = black_border

        # Add details for the position
        for candidate in candidates:
            # ws.append(candidate)
            row_num = ws.max_row + 1
            for col_num, value in enumerate(candidate, start=1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
                cell.border = black_border  # Apply border to each cell

        # Add an empty row for separation
        ws.append([])

    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)
    return xlsx_file

import json
import frappe

def get_data_new(args):
    if args is None:
        args = {}

    if isinstance(args.get('args'), str):
        try:
            args['filters'] = json.loads(args['args'])
        except json.JSONDecodeError as e:
            frappe.log_error(title='JSON Decode Error', message=str(e))
            return []
    
    args['filters'] = args.get('filters', {})

    data = []
    date_filter = args['filters'].get('custom_date_filter')
    candidate_created_by_filter = args['filters'].get('custom_candidate_status_filter')
    candidate_status = args['filters'].get('custom_status_filter')
    # print(candidate_created_by_filter)
    # print(date_filter)
    if not date_filter or not candidate_created_by_filter:
        frappe.log_error(title='Missing filters', message='Date filter or candidate_created_by filter is missing.')
        return data

    filters = {}

    candidate_condition = candidate_created_by_filter.get('condition')
    candidate_value = candidate_created_by_filter.get('value')

    if candidate_condition in ('!=', '=',):
        filters['candidate_created_by'] = [candidate_condition, candidate_value]
    elif candidate_condition in ('like', 'not like') and isinstance(candidate_value, str):
        filters['candidate_created_by'] = [candidate_condition, candidate_value]
    elif candidate_condition == 'is' and candidate_value == 'set':
        filters['candidate_created_by'] = ["is", "set"]
    elif candidate_condition == 'is' and candidate_value == 'not set':
        filters['candidate_created_by'] = ["is", "not set"]
    elif candidate_condition in ('in', 'not in') and isinstance(candidate_value, list):
        filters['candidate_created_by'] = [candidate_condition, candidate_value]
    else:
        return data

    date_condition = date_filter.get('condition')
    date_value = date_filter.get('value')

    if date_condition == 'Between' and isinstance(date_value, list) and len(date_value) == 2:
        filters['submitted_date'] = ['between', [date_value[0], date_value[1]]]
    elif date_condition == 'in' and isinstance(date_value, list):
        filters['submitted_date'] = ['in', date_value]
    elif date_condition == 'not in' and isinstance(date_value, list):
        filters['submitted_date'] = ['not in', date_value]
    elif date_condition == 'is' and date_value == 'set':
        filters['submitted_date'] = ['is', 'set'] 
    elif date_condition == 'is' and date_value == 'not set':
        filters['submitted_date'] = ['is', 'not set'] 
    elif date_condition in ('<', '<=', '>', '>=') and isinstance(date_value, str):
        filters['submitted_date'] = [date_condition, date_value]
    elif date_condition in ('=', '!=') and isinstance(date_value, str):
        filters['submitted_date'] = [date_condition, date_value]  
    elif date_condition == 'Timespan' and isinstance(date_value, str):
        # print(date_value)
        from_date, to_date = get_timespan_custom(date_value)
        filters['submitted_date'] = ['between', [from_date, to_date]]
    elif date_condition == 'fiscal year' and isinstance(date_value, str):
        fiscal_year_start, fiscal_year_end = get_fiscal_year_custom(date_value)
        filters['submitted_date'] = ['between', [fiscal_year_start, fiscal_year_end]]
    else:
        # frappe.log_error(title='Invalid Date Filter', message='Date filter is not set properly.')
        return data
    
    if candidate_status:
        status_condition = candidate_status.get('condition')
        status_value = candidate_status.get('value')
        if status_condition and status_value:
            if status_value =="Submit(SPOC)" or status_value == "Submitted(Client)":
                filters['pending_for'] = [status_condition, status_value]
    
    data = {}
    candidates = frappe.get_all(
        "Candidate",
        filters=filters,
        fields=["name", "passport_number", "given_name", "highest_degree",
                "total_experience", "overseas_experience", "current_employer",
                "current_ctc", "expected_ctc", "location", "notice_period_months",
                "remarks_1", "position","currency_ctc"]
    )
    for candidate in candidates:
        position = candidate.get("position", "")
        currency=candidate.currency_ctc
        formatted_ctc = f"{currency} {candidate.current_ctc}" if candidate.current_ctc else "0"
        if position not in data:
            data[position] = []
        data[position].append([
            candidate.name, candidate.passport_number, candidate.given_name,
            candidate.highest_degree, candidate.total_experience, 
            candidate.overseas_experience, candidate.current_employer,
            formatted_ctc, candidate.expected_ctc, candidate.location, 
            candidate.notice_period_months, candidate.remarks_1
        ])

    return data



def get_timespan_custom(timespan):
    print(nowdate())
    today = nowdate()
    if timespan == "last week":
        start_date = add_days(today, -7)
        end_date = today
    elif timespan == "last month":
        start_date = add_months(today, -1)
        end_date = today
    elif timespan == "last quarter":
        start_date = add_months(today, -3)
        end_date = today
    elif timespan == "last year":
        start_date = add_months(today, -12)
        end_date = today
    elif timespan == "last 6 months":
        start_date = add_months(today, -6)
        end_date = today
    elif timespan == "today":
        start_date = end_date = today
    elif timespan == "yesterday":
        start_date = end_date = add_days(today, -1)
    elif timespan == "tomorrow":
        start_date = end_date = add_days(today, 1)
    elif timespan == "next month":
        start_date = add_months(today, 1)
        end_date = add_days(add_months(today, 1), -1)
    elif timespan == "next week":
        start_date = today
        end_date = add_days(today, 7)
    elif timespan == "next quarter":
        start_date = today
        end_date = add_months(today, 3)
    elif timespan == "next year":
        start_date = today
        end_date = add_months(today, 12)
    elif timespan == "next 6 months":
        start_date = today
        end_date = add_months(today, 6)
    elif timespan == "this week":
        start_date = get_first_day(today, "week")  
        end_date = add_days(start_date, 6) 
    elif timespan == "this month":
        start_date = get_first_day(today, "month")  
        end_date = get_last_day(today, "month")  
    elif timespan == "last month":
        start_date = add_months(today, -1)
        end_date = today
    elif timespan == "this quarter":
        start_date = get_first_day(today, "quarter")  
        end_date = get_last_day(today, "quarter")  
    elif timespan == "this year":
        start_date = get_first_day(today, "year")  
        end_date = get_last_day(today, "year")
    else:
        raise ValueError(f"Unsupported timespan: {timespan}")
    
    return start_date, end_date

def get_fiscal_year_custom(fiscal_year):
    fiscal_year_split = fiscal_year.split('-')
    start_year = fiscal_year_split[0]
    end_year = fiscal_year_split[1]

    start_date = date(int(start_year), 1, 1) 
    end_date = date(int(end_year), 12, 31)    

    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


# @frappe.whitelist()
# def update_tat_existing():
#     batches=frappe.db.get_all("Batch",{"expected_start_date": ["between", ["2025-01-15", "2025-01-20"]]},["name"])
#     ind=0
#     for i in batches:
#         cases=frappe.db.get_all("Case",{"batch":i.name},["name"])
#         for j in cases:
#             doc=frappe.get_doc("Case",j.name)
#             if doc.insufficiency_closed:
#                 from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
#                 holiday_list_name = 'TEAMPRO 2023 - Checkpro'
#                 start_date = doc.insufficiency_closed
#                 working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
#                 current_date = start_date
#                 holiday = []
#                 while working_days > 0:
#                     if not is_holiday(holiday_list_name, current_date):
#                         holiday.append(current_date)
#                         working_days -= 1
#                     current_date = add_days(current_date, 1)
#                 frappe.db.set_value("Case",doc.name,"end_date",holiday[-1])



@frappe.whitelist()
def check_holidays(date1, date2,name):
    doc=frappe.get_doc("Case",name)
    if doc.date_of_initiating:
        from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
        holiday_list_name = 'TEAMPRO 2023 - Checkpro'
        start_date = doc.date_of_initiating
        working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
        current_date = start_date
        holiday = []
        while working_days > 0:
            if not is_holiday(holiday_list_name, current_date):
                holiday.append(current_date)
                working_days -= 1
            current_date = add_days(current_date, 1)
        sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{date1}' AND '{date2}'
        """

        count = frappe.db.sql(sql_query, as_list=True)[0][0]

        # return count
        return holiday[-1],count
    
# @frappe.whitelist()
# def case_status_report():
#     data = '<table border="1" style="border-collapse: collapse; width: 100%;">'
#     data += '<tr style="background-color: #002060; color: white;">' \
#         '<td style="text-align:center; font-weight:bold; color:white;">Customer</td>' \
#         '<td style="text-align:center; font-weight:bold; color:white;">Batch</td>' \
#         '<td style="text-align:center; font-weight:bold; color:white;">Case Name</td>' \
#         '<td style="text-align:center; font-weight:bold; color:white;">Case Status</td>' \
#         '<td style="text-align:center; font-weight:bold; color:white;">Age (Days)</td>' \
#         '</tr>'

#     # Fetch all batches with batch_status not "Completed"
#     batches = frappe.db.get_all("Batch", {"batch_status": ("!=", "Completed")}, ["name", "customer"])

#     for batch in batches:
#         # Get cases for the current batch
#         cases = frappe.db.get_all("Case", {"batch": batch.name}, ["name", "case_status", "actual_tat"])
#         # Add customer row only once
#         first_row = True
#         second_row=True
#         for case in cases:
#             data += f'<tr>'
#             if first_row:
#                 data += f'<td style="text-align:center;" rowspan="{len(cases)}">{batch.customer}</td>'
#                 first_row = False
#             if second_row:
#                 data+=f'<td style="text-align:center;" rowspan="{len(cases)}">{batch.name}</td>'
#                 second_row=False
#             data += f'<td style="text-align:center;">{case.name}</td>' \
#                     f'<td style="text-align:center;">{case.case_status}</td>' \
#                     f'<td style="text-align:center;">{case.actual_tat}</td>' \
#                     '</tr>'

#     data += '</table>'

#     frappe.sendmail(
#         recipients="divya.p@groupteampro.com",
#         subject=_("Case Status Report"),
#         message=f"""
#             Dear Sir/Madam,<br><br>
#             Kindly find the below list of Case Status Reports:<br>{data}<br>
#             Thanks & Regards,<br>
#             TEAM ERP<br>
#             <i>This email has been automatically generated. Please do not reply.</i>
#         """
#     )
@frappe.whitelist()
def case_status_report_excel():
    next_date=today()
    next_dates=datetime.strptime(next_date, '%Y-%m-%d')
    filename = "Case_Status_Report" + today() + ".xlsx"
    xlsx_file = make_xlsx_case_status(filename)
    case_status_report(filename, xlsx_file.getvalue())

def make_xlsx_case_status(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Case Status Report"
    text_wrap_left = Alignment(vertical="center", horizontal="center")
    # Setting column widths
    for col in range(ord('A'), ord('M') + 1):  # Adjust for header range
        ws.column_dimensions[chr(col)].width = 20

    # Adding headers
    headers = [
        "Sr.no", "ID", "Employee Name", "Customer", "Check Package", "Batch", 
        "Case Status", "Case Report", "Client Employee Code", "Initiation Date",
        "Entry Allocated To", "Case Completion Date", "TAT Completion Date",
        "Insufficiency Closed", "Insufficiency Reported", "Actual Age",
        "0 to 5", "6 to 10", "11 to 15", ">15"
    ]
    ws.append(headers)  # Adding headers to the sheet

    # Formatting headers
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")  # White font color for better visibility
        cell.fill = PatternFill(start_color="FF002060", end_color="FF002060", fill_type="solid")  # aRGB format
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        cell.alignment=text_wrap_left

    # Fetching case details
    case_details = get_case_report_detaiils()

    sr_no = 1
    for case in case_details:
        tat_counts = {
            "0 to 5": "",
            "6 to 10": "",
            "11 to 15": "",
            ">15": ""
        }
        # Determine the age range for `actual_tat`
        tat_range = {
            "0 to 5": 0 <= case["actual_tat"] <= 5,
            "6 to 10": 6 <= case["actual_tat"] <= 10,
            "11 to 15": 11 <= case["actual_tat"] <= 15,
            ">15": case["actual_tat"] > 15
        }

        tat_counts = {key: 1 if condition else 0 for key, condition in tat_range.items()}

        # Append data row
        ws.append([
            sr_no,
            case.get("name"),
            case.get("case_name"),
            case.get("customer"),
            case.get("check_package"),
            case.get("batch"),
            case.get("case_status"),
            case.get("case_report"),
            case.get("client_employee_code"),
            case.get("date_of_initiating"),
            case.get("allocated_to"),
            case.get("case_completion_date"),
            case.get("end_date"),
            case.get("insufficiency_closed"),
            case.get("insufficiency_reported"),
            case.get("actual_tat"),
            tat_counts["0 to 5"] or "",
            tat_counts["6 to 10"] or "",
            tat_counts["11 to 15"] or "",
            tat_counts[">15"] or ""
        ])
        sr_no += 1
        for cell in ws[ws.max_row]:
            cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    # Save to BytesIO object
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)
    return xlsx_file


def get_case_report_detaiils():
    cases=frappe.db.get_all("Case",{"case_status":("not in",["Final-QC","Generate Report","Case Report Completed","Case Completed","To be Billed","SO Created","Drop"])},["*"])
    return cases

@frappe.whitelist()
def case_status_report(filename, file_content):
    data = '<table border="1" style="border-collapse: collapse; width: 100%;">'
    data += '<tr style="background-color: #002060; color: white;">' \
        '<td style="text-align:center; font-weight:bold; color:white;">Customer</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">0-5</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">6-10</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">11-15</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">>15</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">Entry Grand Total</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">Entry-Insuff</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">Execution-Insuff</td>' \
        '<td style="text-align:center; font-weight:bold; color:white;">Grand Total</td>' \
        '</tr>'

    # Fetch all batches with batch_status not "Completed"
    batches = frappe.db.get_all("Batch", {"batch_status": ("!=", "Completed")}, ["name", "customer"])

    customer_data = {}
    grand_totals = {
        "0-5": 0,
        "6-10": 0,
        "11-15": 0,
        ">15": 0,
        "Entry-Insuff": 0,
        "Execution-Insuff": 0
    }

    for batch in batches:
        customer = batch.customer
        if customer not in customer_data:
            customer_data[customer] = {
                "0-5": 0,
                "6-10": 0,
                "11-15": 0,
                ">15": 0,
                "Entry-Insuff": 0,
                "Execution-Insuff": 0
            }

        # Get cases for the current batch
        cases = frappe.db.get_all("Case", {"batch": batch.name}, ["name", "case_status", "actual_tat"])

        for case in cases:
            if case["case_status"] in ["Draft", "Entry Completed", "Entry-QC", "Execution"]:
                if 0 <= case["actual_tat"] <= 5:
                    customer_data[customer]["0-5"] += 1
                elif 6 <= case["actual_tat"] <= 10:
                    customer_data[customer]["6-10"] += 1
                elif 11 <= case["actual_tat"] <= 15:
                    customer_data[customer]["11-15"] += 1
                elif case["actual_tat"] > 15:
                    customer_data[customer][">15"] += 1

            if case["case_status"] == "Entry-Insuff":
                customer_data[customer]["Entry-Insuff"] += 1
            if case["case_status"] == "Execution-Insuff":
                customer_data[customer]["Execution-Insuff"] += 1

    # Populate the table with customer data
    for customer, counts in customer_data.items():
        # Calculate row-level totals
        entry_grand_total = counts["0-5"] + counts["6-10"] + counts["11-15"] + counts[">15"]
        grand_total = counts["Entry-Insuff"] + counts["Execution-Insuff"]

        # Update grand totals
        for key in grand_totals:
            grand_totals[key] += counts[key]

        # Append row data
        data += f'<tr>' \
            f'<td style="text-align:center;">{customer}</td>' \
            f'<td style="text-align:center;">{counts["0-5"] or ""}</td>' \
            f'<td style="text-align:center;">{counts["6-10"] or ""}</td>' \
            f'<td style="text-align:center;">{counts["11-15"] or ""}</td>' \
            f'<td style="text-align:center;">{counts[">15"] or ""}</td>' \
            f'<td style="text-align:center;">{entry_grand_total or ""}</td>' \
            f'<td style="text-align:center;">{counts["Entry-Insuff"] or ""}</td>' \
            f'<td style="text-align:center;">{counts["Execution-Insuff"] or ""}</td>' \
            f'<td style="text-align:center;">{grand_total or ""}</td>' \
            f'</tr>'

    # Append grand total row
    overall_grand_total = grand_totals["Entry-Insuff"] + grand_totals["Execution-Insuff"]
    entry_grand_total_sum = grand_totals["0-5"] + grand_totals["6-10"] + grand_totals["11-15"] + grand_totals[">15"]

    data += f'<tr style="font-weight: bold; background-color: #f2f2f2;">' \
        f'<td style="text-align:center;">Grand Total</td>' \
        f'<td style="text-align:center;">{grand_totals["0-5"] or ""}</td>' \
        f'<td style="text-align:center;">{grand_totals["6-10"] or ""}</td>' \
        f'<td style="text-align:center;">{grand_totals["11-15"] or ""}</td>' \
        f'<td style="text-align:center;">{grand_totals[">15"] or ""}</td>' \
        f'<td style="text-align:center;">{entry_grand_total_sum or ""}</td>' \
        f'<td style="text-align:center;">{grand_totals["Entry-Insuff"] or ""}</td>' \
        f'<td style="text-align:center;">{grand_totals["Execution-Insuff"] or ""}</td>' \
        f'<td style="text-align:center;">{overall_grand_total or ""}</td>' \
        f'</tr>'

    data += '</table>'

    frappe.sendmail(
        recipients=["sangeetha.a@groupteampro.com","sangeetha.s@groupteampro.com","dineshbabu.k@groupteampro.com","keerthana.b@groupteampro.com"],
        subject=_("Case Status Report"),
        message=f"""
            Dear Sir/Madam,<br><br>
            Kindly find the below list of Case Status Report:<br>{data}<br>
            Thanks & Regards,<br>
            TEAM ERP<br>
            <i>This email has been automatically generated. Please do not reply.</i>
        """,
        attachments=[
            {"fname": filename, "fcontent": file_content},
        ]
    )

# Add entry allocated to and allocated date in case in list view
@frappe.whitelist()
def update_entry_allocated_to(case_id,allocated_to,allocated_date):
    doc_name = json.loads(case_id)
    for i in doc_name:
        frappe.set_value("Case",i,"allocated_to",allocated_to)
        frappe.set_value("Case",i,"custom_allocation_date",allocated_date)
            
@frappe.whitelist()
def update_tat_case():
    frappe.enqueue(
        update_tat_completion_date_daily, 
        queue="long",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Tat Updation',
        enqueue_after_commit=False,
    )
# Daily cron update
@frappe.whitelist()
def update_tat_completion_date_daily():
    cases=frappe.db.get_all("Case",{"case_status":("not in",["Case Completed","To be Billed","SO Created"])},["name"])
    for i in cases:
        doc=frappe.get_doc("Case",i.name)
        if doc.insufficiency_closed:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insufficiency_closed
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            sql_query = f"""
                SELECT COUNT(*) 
                FROM `tabHoliday` 
                WHERE parent = 'TEAMPRO 2023 - Checkpro' 
                AND holiday_date BETWEEN '{doc.insufficiency_closed}' AND '{holiday[-1]}'
            """
            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Case",doc.name,"end_date",holiday[-1])
            frappe.db.set_value("Case",doc.name,"holidays",count)
            # doc.end_date=holiday[-1]
            # doc.holidays=count
            # doc.save(ignore_permissions=True)
            # frappe.db.commit()
# @frappe.whitelist()
# def task_mail_notification_status ():
#     job = frappe.db.exists('Scheduled Job Type','update_holiday_tat_case')
#     if not job:
#         task = frappe.new_doc("Scheduled Job Type")
#         task.update({
#             "method": 'checkpro.custom.update_holiday_tat_case',
#             "frequency": 'Cron',
#             "cron_format": '0 0 * * *'
#         })
#         task.save(ignore_permissions=True)

@frappe.whitelist()
def update_holiday_tat_case():
    frappe.enqueue(
        check_holidays_not_insuff, 
        queue="long",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Tat Holiday Updation',
        enqueue_after_commit=False,
    )

@frappe.whitelist()
def check_holidays_not_insuff():
    cases=frappe.db.get_all("Case",{"case_status":("not in",["Case Completed","To be Billed","SO Created"])},["*"])
    for i in cases:
        doc=frappe.get_doc("Case",i.name)
        if doc.date_of_initiating and not doc.insufficiency_closed:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.date_of_initiating
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            sql_query = f"""
                SELECT COUNT(*) 
                FROM `tabHoliday` 
                WHERE parent = 'TEAMPRO 2023 - Checkpro' 
                AND holiday_date BETWEEN '{doc.date_of_initiating}' AND '{doc.end_date}'
            """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Case",doc.name,"end_date",holiday[-1])
            frappe.db.set_value("Case",doc.name,"holidays",count)
            # doc.end_date=holiday[-1]
            # doc.holidays=count
            # doc.save(ignore_permissions=True)
            # frappe.db.commit()


@frappe.whitelist()
def insuff_tat_daily():
    list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
    cases=frappe.db.get_all("Case",{"case_status":("not in",["Case Completed","To be Billed","SO Created"])},["*"])
    for j in cases:
        mini=[]
        maxi=[]
        for i in list:
            doc=frappe.get_all(i,{"case_id":j.name},["name","insufficiency_date","workflow_state","insuff_closed"])
            for j in doc:
                if j.insufficiency_date:
                    mini.append(j.insufficiency_date)
                if j.insuff_closed and j.workflow_state!="Insufficient Data":
                    maxi.append(j.insuff_closed)
        first_date= min(mini) if mini else None
        last_time = max(maxi) if maxi else None
        # frappe.db.set_value("Case",j.name,"insufficiency_reported",first_date)
        # frappe.db.set_value("Case",j.name,"insufficiency_closed",last_time)

@frappe.whitelist()
def update_insuff_days_daily():
    cases=frappe.db.get_all("Case",{"case_status":("not in",["Case Completed","To be Billed","SO Created"])},["*"])
    for i in cases:
        doc=frappe.get_doc("Case",i.name)
        if doc.insufficiency_reported and doc.insufficiency_closed:
            date=(date_diff(doc.insufficiency_reported,doc.insufficiency_closed))
            sql_query = f"""
                SELECT COUNT(*) 
                FROM `tabHoliday` 
                WHERE parent = 'TEAMPRO 2023 - Checkpro' 
                AND holiday_date BETWEEN '{doc.insufficiency_reported}' AND '{doc.insufficiency_closed}'
            """
            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            date1 = (date-count)+1
            # doc.insufficiency_days=date1
            # doc.save(ignore_permissions=True)
            # frappe.db.commit()

@frappe.whitelist()
def update_tat_completion_date_ed_daily():
    checks=frappe.db.get_all("Education Checks",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Education Checks",i.name)
        if doc.clear_insufficiency:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.clear_insufficiency
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            # doc.tat_completion_date=holiday[-1]
            frappe.db.set_value("Education Checks",doc.name,"tat_completion_date",holiday[-1])
        elif not doc.clear_insufficiency and doc.check_creation_date:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            # doc.tat_completion_date=holiday[-1]
            frappe.db.set_value("Education Checks",doc.name,"tat_completion_date",holiday[-1])

@frappe.whitelist()
def update_holidays_daily_edu():
    checks=frappe.db.get_all("Education Checks",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Education Checks",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Education Checks",doc.name,"holidays",count)

@frappe.whitelist()
def update_tat_completion_date_employment_daily():
    checks=frappe.db.get_all("Employment",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Employment",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.tat_completion_date = holiday[-1]
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.tat_completion_date = holiday[-1]

@frappe.whitelist()
def update_holidays_daily_emp():
    checks=frappe.db.get_all("Employment",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Employment",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Employment",doc.name,"holidays",count)


@frappe.whitelist()
def update_tat_completion_date_address_daily():
    checks=frappe.db.get_all("Address Check",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Address Check",i.name)
        if doc.clear_insufficiency:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.clear_insufficiency
            if doc.check_package:
                working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.custom_tat_completion_date=holiday[-1]
        elif doc.check_creation_date and not doc.clear_insufficiency:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            if doc.check_package:
                working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.custom_tat_completion_date=holiday[-1]

@frappe.whitelist()
def update_holidays_daily_add():
    checks=frappe.db.get_all("Address Check",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Address Check",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Address Check",doc.name,"holidays",count)


@frappe.whitelist()
def update_tat_completion_date_inchecks_daily():
    checks=frappe.db.get_all("Criminal",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Criminal",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.tat_completion_date=holiday[-1]
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.tat_completion_date=holiday[-1]

@frappe.whitelist()
def update_holidays_daily_criminal():
    checks=frappe.db.get_all("Criminal",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Criminal",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Criminal",doc.name,"holidays",count)

@frappe.whitelist()
def update_tat_completion_date_court_daily():
    checks=frappe.db.get_all("Court",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Court",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            if doc.check_package:
                working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.tat_completion_date=holiday[-1]
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            if doc.check_package:
                working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            doc.tat_completion_date=holiday[-1]

@frappe.whitelist()
def update_holidays_daily_court():
    checks=frappe.db.get_all("Court",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Court",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Court",doc.name,"holidays",count)


@frappe.whitelist()
def update_tat_completion_date_reference_daily():
    checks=frappe.db.get_all("Reference Check",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Reference Check",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Reference Check",doc.name,"tat_completion_date",holiday[-1])
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            if doc.check_package:
                working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Reference Check",doc.name,"tat_completion_date",holiday[-1])

@frappe.whitelist()
def update_holidays_daily_ref():
    checks=frappe.db.get_all("Reference Check",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Reference Check",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Reference Check",doc.name,"holidays",count)

@frappe.whitelist()
def update_tat_completion_date_id_daily():
    checks=frappe.db.get_all("Identity Aadhar",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Identity Aadhar",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Identity Aadhar",doc.name,"tat_completion_date",holiday[-1])
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Identity Aadhar",doc.name,"tat_completion_date",holiday[-1])

@frappe.whitelist()
def update_holidays_daily_iden():
    checks=frappe.db.get_all("Identity Aadhar",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Identity Aadhar",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Identity Aadhar",doc.name,"holidays",count)


@frappe.whitelist()
def update_tat_completion_date_sm_daily():
    checks=frappe.db.get_all("Social Media",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Social Media",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Social Media",doc.name,"tat_completion_date",holiday[-1])
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Social Media",doc.name,"tat_completion_date",holiday[-1])

@frappe.whitelist()
def update_holidays_daily_soc():
    checks=frappe.db.get_all("Social Media",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Social Media",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Social Media",doc.name,"holidays",count)


@frappe.whitelist()
def update_tat_completion_date_family_daily():
    checks=frappe.db.get_all("Family",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Family",i.name)
        if doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.insuff_cleared_on
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Family",doc.name,"tat_completion_date",holiday[-1])
        elif doc.check_creation_date and not doc.insuff_cleared_on:
            from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
            holiday_list_name = 'TEAMPRO 2023 - Checkpro'
            start_date = doc.check_creation_date
            working_days = int(frappe.db.get_value("Check Package",{'name':doc.check_package},['package_tat']))
            current_date = start_date
            holiday = []
            while working_days > 0:
                if not is_holiday(holiday_list_name, current_date):
                    holiday.append(current_date)
                    working_days -= 1
                current_date = add_days(current_date, 1)
            frappe.db.set_value("Family",doc.name,"tat_completion_date",holiday[-1])

@frappe.whitelist()
def update_holidays_daily_fam():
    checks=frappe.db.get_all("Family",{"check_status":("!=",["Report Completed"])},["*"])
    for i in checks:
        doc=frappe.get_doc("Family",i.name)  
        if doc.check_creation_date and doc.check_completion_date:
            sql_query = f"""
            SELECT COUNT(*) 
            FROM `tabHoliday` 
            WHERE parent = 'TEAMPRO 2023 - Checkpro' 
            AND holiday_date BETWEEN '{doc.check_creation_date}' AND '{doc.check_completion_date}'
        """

            count = frappe.db.sql(sql_query, as_list=True)[0][0]
            frappe.db.set_value("Family",doc.name,"holidays",count)

@frappe.whitelist()
def update_actual_tat_daily():
    list = ["Education Checks","Family","Reference Check","Court","Social Media","Criminal","Employment","Identity Aadhar","Address Check"]
    actual_tat=0
    tat = 0
    tat_monitor = ''
    date = 0
    dat = 0
    variation = 0
    for i in list:
        doc=frappe.db.get_list(i,["name","workflow_state","check_completion_date","check_creation_date","insufficiency_days","holidays","package_tat"])
        for j in doc:
            if(j.check_completion_date and j.workflow_state=="Report Completed"):
                date=(date_diff(doc.check_completion_date,doc.check_creation_date))+1
                dat=(sum([int(doc.insufficiency_days),int(doc.holidays)]))
                actual_tat=date - dat
                variation = int(actual_tat)-int(doc.package_tat)

                if variation < 0:
                    tat=0
                    tat_monitor = "In TAT"
                else:
                    tat=variation
                    tat_monitor = "Out TAT"
            # frappe.db.set_value(i,j.name,"actual_tat",actual_tat)
            # frappe.db.set_value(i,j.name,"tat_variation",tat)
            # frappe.db.set_value(i,j.name,"tat_monitor",tat_monitor)

@frappe.whitelist()
def nc_for_check_reject(name=None,id=None,allocated=None,class_proposed=None,reason=None):
    if allocated:
        emp_id=frappe.db.get_value("Employee",{'user_id':allocated},['name'])
        reopen_cause='(%s) Check :(%s) Rejected .Reason(%s)' % (name,id,reason)
        nc = frappe.new_doc('Energy Point And Non Conformity')
        nc.emp = emp_id
        nc.action='Non Conformity(NC)'
        nc.class_proposed = class_proposed
        nc.reason_of_ep = reopen_cause
        nc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Energy Point And Non Conformity", nc.name, "workflow_state", "Explanation")
        frappe.db.commit()
        return {"status": "success", "message": "NC created"}

@frappe.whitelist()
def send_mail_nc_for_check_reject(name=None,id=None,allocated=None,class_proposed=None,reason=None):
    if allocated:
        emp_id=frappe.db.get_value("Employee",{'user_id':allocated},['name'])
        subject = _("{} - {} Rejected").format(name, id)
        message = """
            <p>Dear {},</p>
            <p><b>{} - {}</b> has been rejected.</p>
            <p><b>Reason:</b> {}</p>
            <p><b>NC Class:</b>{}</p>
            <p>Kindly review and take the necessary action.</p>
            <p>Best Regards,<br>TEAMPRO</p>
            """.format(emp_id,name, id, reason,class_proposed)

        frappe.sendmail(
            recipients=allocated,
            subject=subject,
            message=message
        )

import frappe
import os
import requests
from frappe.utils import get_files_path
from pdf2image import convert_from_path

@frappe.whitelist()
def convert_pdf_to_images(file_url):
    if not file_url:
        frappe.throw("No file URL provided")

    # Construct full PDF URL
    pdf_url = f"https://erp.teamproit.com{file_url}"
    
    # Debugging: Log the resolved PDF URL
    frappe.logger().error(f"Fetching PDF from: {pdf_url}")

    # Download the PDF file
    output_dir = get_files_path("pdf_images", is_private=False)
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_filename = os.path.basename(file_url).replace(' ', '_')
    pdf_path = os.path.join(output_dir, pdf_filename)

    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        # Save the downloaded PDF file
        with open(pdf_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

    except requests.exceptions.RequestException as e:
        frappe.throw(f"Failed to download PDF: {str(e)}")

    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=150)
    except Exception as e:
        frappe.throw(f"PDF conversion error: {str(e)}")

    image_urls = []
    for i, img in enumerate(images):
        img_filename = f"{pdf_filename}_page_{i + 1}.png"
        img_path = os.path.join(output_dir, img_filename)
        img.save(img_path, "PNG")

        # Generate public URL for the image
        image_urls.append(f"/files/pdf_images/{img_filename}")

    return image_urls

import frappe

@frappe.whitelist()
def send_task_creation_email(doc,method):
    task_doc = frappe.get_doc("Task", doc.name)
    
    if task_doc.service == "IT-SW" and task_doc.type == "OPS":
        subject = f"New Task Created: {task_doc.name}"
        sub=task_doc.subject
        customer = task_doc.customer
        project = task_doc.project
        status = task_doc.status
        priority = task_doc.priority
        production_date = task_doc.custom_production_date.strftime("%d-%m-%Y") if task_doc.custom_production_date else ""
        allocation_date = task_doc.custom_allocated_on.strftime("%d-%m-%Y") if task_doc.custom_allocated_on else ""
        user = task_doc.custom_allocated_to

        recipients = []
        if task_doc.custom_development_spoc:
            recipients.append(task_doc.custom_development_spoc)
        # if task_doc.spoc:
        #     recipients.append(task_doc.spoc)
        if task_doc.project_manager:
            recipients.append(task_doc.project_manager)
        
        # Prepare HTML content with table
        email_body = f"""
        <p><strong>New Task Details:</strong></p>
        <table width='100%' style='border-collapse: collapse; border: 1px solid black; text-align: center;'>
            <thead>
                <tr style="background-color: #0f1568; color: white;">
                    <th colspan='2' style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black;'><b>Details</b></th>
                </tr>
            </thead>
            <tbody>
                <tr style='text-align: left;'><td width='25%'style='border: 1px solid black;'><b>Task ID</b></td><td style='border: 1px solid black;'>{task_doc.name}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Subject</b></td><td style='border: 1px solid black;'>{sub}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Customer</b></td><td style='border: 1px solid black;'>{customer}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Project</b></td><td style='border: 1px solid black;'>{project}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Status</b></td><td style='border: 1px solid black;'>{status}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Priority</b></td><td style='border: 1px solid black;'>{priority}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Production Date</b></td><td style='border: 1px solid black;'>{production_date}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>Allocation Date</b></td><td style='border: 1px solid black;'>{allocation_date}</td></tr>
                <tr style='text-align: left;'><td style='border: 1px solid black;'><b>User</b></td><td style='border: 1px solid black;'>{user}</td></tr>
            </tbody>
        </table>
        """
        
        # Send email to recipients
        if recipients:
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=email_body
            )


import frappe
from frappe.utils import nowdate

from frappe.utils import nowdate
@frappe.whitelist()
def kt_email():
    
    tasks = frappe.get_all("Task", filters={"kt_confirmed": False, "service": "IT-SW", "type": "OPS", "status": "Working"}, fields=["name", "subject", "customer", "project", "status", "priority", "custom_production_date", "custom_allocated_on", "custom_allocated_to", "project_manager"])

    
    task_details = []
    serial_no = 1  # Initialize serial number

    for task_doc in tasks:
        task = frappe.get_doc("Task", task_doc.name)

      
        if task.service == "IT-SW" and task.type == "OPS" and task.status == "Working":
            production_date = task.custom_production_date.strftime("%d-%m-%Y") if task.custom_production_date else ""
            allocation_date = task.custom_allocated_on.strftime("%d-%m-%Y") if task.custom_allocated_on else ""
            user = task.custom_allocated_to

            # Append task details to the list with a serial number in columns
            task_details.append(f"""
            <tr style='text-align: left;'>
                <td style='border: 1px solid black; text-align: center; padding: 8px;'>{serial_no}</td>
                <td style='border: 1px solid black; text-align: left; padding: 8px;'>{task.name}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.subject}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.customer}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.project}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.status}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.priority}</td>
                <td style='border: 1px solid black; padding: 8px;'>{production_date}</td>
                <td style='border: 1px solid black; padding: 8px;'>{allocation_date}</td>
                <td style='border: 1px solid black; padding: 8px;'>{user}</td>
            </tr>
            """)

            serial_no += 1  # Increment serial number for the next task

    # If we have any tasks, send an email
    if task_details:
        # Email Subject
        subject = "KT Not Confirmed Tasks"

        # Prepare HTML content with all task details
        email_body = f"""
        <p><strong>KT Not Confirmed Tasks</strong></p>
        <table width='100%' style='border-collapse: collapse; border: 1px solid black; text-align: center;'>
            <thead>
                <tr style="background-color: #0f1568; color: white;">
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>S.No</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Task ID</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Subject</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Customer</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Project</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Status</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Priority</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Production Date</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Allocation Date</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Allocated To</b></th>
                </tr>
            </thead>
            <tbody>
                {''.join(task_details)}
            </tbody>
        </table>
        """
        

        
        frappe.sendmail(
            recipients=["abdulla.pi@groupteampro.com","siva.m@groupteampro.com","giftyp@groupteampro.com","jenisha.p@groupteampro.com"],
            subject=subject,
            message=email_body
        )


from frappe.utils import nowdate

@frappe.whitelist()
def sprint_task():
    # Get all tasks where the checkbox is unchecked (disabled)
    tasks = frappe.get_all("Task", filters={"service": "IT-SW", "type": "OPS", "status": "Working"}, fields=["name", "subject", "customer", "project", "status", "priority", "custom_production_date", "custom_allocated_on", "custom_allocated_to", "project_manager","custom_sprint","custom_dev_team"])
    
    task_details = []
    serial_no = 1  # Initialize serial number

    for task_doc in tasks:
        task = frappe.get_doc("Task", task_doc.name)

        # Get the active sprint for the task
        sprint = frappe.get_all('Task Sprint', filters={'Active': True, 'name': task.custom_sprint})
        
        if sprint:
            # Sprint exists for this task
            production_date = task.custom_production_date.strftime("%d-%m-%Y") if task.custom_production_date else ""
            allocation_date = task.custom_allocated_on.strftime("%d-%m-%Y") if task.custom_allocated_on else ""
            user = task.custom_allocated_to

            # Append task details to the list with a serial number in columns
            task_details.append(f"""
            <tr style='text-align: left;'>
                <td style='border: 1px solid black; text-align: center; padding: 8px;'>{serial_no}</td>
                <td style='border: 1px solid black; text-align: left; padding: 8px;'>{task.name}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.subject}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.customer}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.project}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.status}</td>
                <td style='border: 1px solid black; padding: 8px;'>{task.priority}</td>
                <td style='border: 1px solid black; padding: 8px;'>{production_date}</td>
                <td style='border: 1px solid black; padding: 8px;'>{allocation_date}</td>
                <td style='border: 1px solid black; padding: 8px;'>{user}</td>
            </tr>
            """)

            serial_no += 1  # Increment serial number for the next task

    # If we have any tasks, send an email
    if task_details:
        # Email Subject
        subject = "Sprint Active Tasks"

        # Prepare HTML content with all task details
        email_body = f"""
        <p><strong>Sprint Active Tasks</strong></p>
        <table width='100%' style='border-collapse: collapse; border: 1px solid black; text-align: center;'>
            <thead>
                <tr style="background-color: #0f1568; color: white;">
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>S.No</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Task ID</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Subject</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Customer</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Project</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Status</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Priority</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Production Date</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Allocation Date</b></th>
                    <th style='text-align: center; background-color: #0f1568;color: white; font-size: 17px; border: 1px solid black; padding: 8px;'><b>Allocated To</b></th>
                </tr>
            </thead>
            <tbody>
                {''.join(task_details)}
            </tbody>
        </table>
        """

        # Send email to the recipients (example recipient is hardcoded here)
        frappe.sendmail(
            recipients=["abdulla.pi@groupteampro.com","siva.m@groupteampro.com"],
            subject=subject,
            message=email_body
        )


# @frappe.whitelist()
# def task_sprint_mail():
#     job = frappe.db.exists('Scheduled Job Type','sprint_task')
#     if not job:
#         task = frappe.new_doc("Scheduled Job Type")
#         task.update({
#             "method": 'checkpro.custom.sprint_task',
#             "frequency": 'Cron',
#             "cron_format": '00 7 * * *'
#         })
#         task.save(ignore_permissions=True)

# @frappe.whitelist()
# def task_sprint_mail_1():
#     job = frappe.db.exists('Scheduled Job Type','kt_email')
#     if not job:
#         task = frappe.new_doc("Scheduled Job Type")
#         task.update({
#             "method": 'checkpro.custom.kt_email',
#             "frequency": 'Cron',
#             "cron_format": '00 7 * * *'
#         })
#         task.save(ignore_permissions=True)



import frappe

@frappe.whitelist()
def dev_team(user):
    emp = frappe.db.get_value(
        'Employee',
        {'status': 'Active', 'user_id': user},
        'custom_dev_team'
    )

    return emp if emp else None


# @frappe.whitelist()
# def sprint_task():
    
#     tasks = frappe.get_all("Task", filters={"service": "IT-SW", "type": "OPS"}, fields=["name", "status","custom_sprint","custom_dev_team"])
    
#     for task_doc in tasks:
#         task = frappe.get_doc("Task", task_doc.name)

#         sprint = frappe.get_all('Task Sprint', filters={'Active': True, 'name': task.custom_sprint})

#         return sprint if sprint else None


# import frappe
# from frappe.utils.file_manager import get_file_path
# from frappe.utils.csvutils import read_csv_content

# @frappe.whitelist()
# def update_sales_follow_up_territory():
#     filename = "e7000bb087territory.csv"  # Ensure correct file name

#     try:
#         # Get full file path (supports private & public files)
#         filepath = get_file_path(filename)
        
#         # Read CSV content
#         csv_data = read_csv_content(filepath)
        
#         updated_count = 0  # Counter for updated records

#         for row in csv_data:
#             # Ensure the CSV has valid data (columns: Doc Name, Territory)
#             if len(row) < 2:
#                 frappe.log_error(f"Invalid data in row: {row}", "CSV Processing Error")
#                 continue

#             doc_name, territory = row[0], row[1]  # Extract values

#             try:
#                 # Update 'Sales Follow Up' document
#                 frappe.db.set_value("Sales Follow Up", {"name": doc_name}, "territory", territory)
#                 updated_count += 1
#             except Exception as e:
#                 frappe.log_error(f"Error updating Sales Follow Up {doc_name}: {str(e)}", "Sales Follow Up Update")

#         # Commit all updates at once for better performance
#         frappe.db.commit()
#         frappe.msgprint(f"{updated_count} records updated successfully.")

#     except Exception as e:
#         frappe.log_error(f"File error: {str(e)}", "Sales Follow Up File Error")
#         frappe.throw("Error processing the file. Please check the file name and format.")


# @frappe.whitelist()
# def emp_checkin_update():
#     filename = 'e7000bb087territory.csv'
#     from frappe.utils.file_manager import get_file
#     from frappe.utils.csvutils import read_csv_content
#     import frappe

#     # Get the file path
#     filepath = get_file(filename)[1]

#     # Read CSV content
#     pps = read_csv_content(filepath)
    
#     ind = 0  # Counter for updated records

#     for pp in pps:
#         # Ensure the CSV has valid data in expected columns
#         if len(pp) < 2:  # Adjusted to match the number of used fields
#             frappe.log_error(f"Invalid data in row: {pp}", "CSV Processing Error")
#             continue
        
#         try:
#             # Update the 'Sales Follow Up' document in one call
#             frappe.db.set_value("Sales Follow Up", {"name": pp[0]}, {
#                 "name": pp[0],
#                 "territory": pp[1]
#             })
#             ind += 1
#         except Exception as e:
#             # Log any errors during the update
#             frappe.log_error(f"Error updating Sales Follow Up {pp[0]}: {str(e)}", "Sales Follow Up Update Error")

#     frappe.db.commit()  # Commit the changes to the database
#     frappe.msgprint(f"{ind} records updated successfully.")




import frappe

def after_insert_employee_onboarding(doc, method):
    frappe.msgprint(f"Employee Onboarding Created for {doc.employee}")

    if doc.employee_onboarding_template:
        activities = frappe.get_all(
            "Employee Boarding Activity",
            fields=[
                "activity_name", "role", "user", "required_for_employee_creation",
                "description", "task_weight", "begin_on", "duration"
            ],
            filters={"parent": doc.employee_onboarding_template, "parenttype": "Employee Onboarding Template"},
            order_by="idx",
        )
        chc=frappe.get_all(
            "Employee Boarding Activity",
            fields=[
                "activity_name", "role", "user", "required_for_employee_creation",
                "description", "task_weight", "begin_on", "duration"
            ],
            filters={"parent": doc.custom_employee_chc_template, "parenttype": "Employee Onboarding Template"},
            order_by="idx",
        )
        for activity in activities:
            new_activity = doc.append("activities", {})
            new_activity.update(activity)
        for i in chc:
            new_chc=doc.append("custom_employee_chc", {})
            new_chc.update(i)
        job_offer=frappe.db.get_value("Job Offer",{"job_applicant":doc.job_applicant},["name"])
        doc.job_offer=job_offer
        doc.save()
        # frappe.msgprint(f"Activities added from template {doc.employee_onboarding_template}")


import frappe

def on_submit_employee_onboarding(doc, method):
    pending_activities = [i.activity_name for i in doc.activities if i.status == "Pending"]
    pending_custom_activities = [j.activity_name for j in doc.custom_employee_chc if j.status == "Pending"]
    if pending_activities or pending_custom_activities:
        pending_list = pending_activities + pending_custom_activities
        frappe.throw(f"The following activities are pending: {', '.join(pending_list)}. Kindly complete them before submission.")
    if frappe.db.exists("Employee Onboarding",{"employee": doc.employee,"docstatus": 1}):
        employee = frappe.get_doc("Employee", doc.employee)
        employee.workflow_state = "Joined"
        employee.save(ignore_permissions=True)
        frappe.msgprint(f"Employee {doc.employee} has been successfully set as active.")

@frappe.whitelist()
def update_case_status_billed(doc,method):
    if doc.services=="BCS" and doc.items:
        for i in doc.items:
            if i.item_code:
                if frappe.db.exists("Case",{"name":i.item_code}):
                    frappe.db.set_value("Case",i.item_code,"case_status","Billed")
                    frappe.db.set_value("Case",i.item_code,"billed_date",today())

@frappe.whitelist()
def update_po_st(doctype,docname):
    frappe.log_error(title="PO",message=docname)
    frappe.db.sql("""
    UPDATE `tabPurchase Order`
    SET docstatus = 0 , workflow_state = 'Pending for CEO'
    WHERE name = %s
""", (docname))

def send_closure_report_with_table():
    filename = "Closure_" + today()
    xlsx_file = build_xlsx_response_closure(filename)
    html_table, total_count = closure_next_action()
    if total_count > 0:
        send_mail_with_attachment_and_html(filename, xlsx_file.getvalue(), html_table)

def send_mail_with_attachment_and_html(filename, file_content, html_table):
    subject = "DND DPR - %s" % nowdate()
    message = (
        "Dear Sir/Madam,<br>"
        "Please find attached the attached Report based on Next Action.<br><br>"
        + html_table +
        "<br>Thanks & Regards,<br>TEAM ERP<br>"
        "This email has been automatically generated. Please do not reply"
    )
    attachments = [{"fname": filename + '.xlsx', "fcontent": file_content}]
    frappe.sendmail(
        # recipients=['jeniba.a@groupteampro.com'],
        recipients=['dc@groupteampro.com'],
        cc=['sangeetha.a@groupteampro.com','sangeetha.s@groupteampro.com','dineshbabu.k@groupteampro.com'],
        sender=None,
        subject=subject,
        message=message,
        attachments=attachments,
    )

def build_xlsx_response_closure(filename):
    return make_xlsx_closure(filename)

def make_xlsx_closure(filename, sheet_name=None, wb=None, column_widths=None):
    action = add_days(nowdate(), 1)
    if wb is None:
        wb = openpyxl.Workbook()
    ws = wb.create_sheet(sheet_name or filename, 0)  
    default_column_widths = [15, 25, 25, 15, 25, 20]
    column_widths = column_widths or default_column_widths    
    for i, width in enumerate(column_widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width  
    header_fill = PatternFill(start_color="87CEFA", end_color="87CEFA", fill_type="solid")
    ws.append(["ID", "Candidate Name", "Customer", "Status", "Next Action", "Remark", "Next Action Date"])
    for cell in ws[1]: 
        cell.fill = header_fill
    closures = frappe.get_all("Closure", {"custom_next_follow_up_on":action,'status':["Not In", ['Onboarded','Dropped']]}, ['*'])
    if closures:
        for closure in closures:
            ws.append([closure.name, closure.given_name, closure.customer, closure.status, closure.std_remarks, closure.remark, closure.custom_next_follow_up_on])
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    xlsx_file.seek(0)    
    return xlsx_file

def closure_next_action():
    action_date = add_days(nowdate(), 1)
    closures = frappe.get_all("Closure", {"custom_next_follow_up_on": action_date,'status':("Not In", ['Onboarded','Dropped'])}, ["customer", "status"])
    customer_status_count = {}
    for closure in closures:
        customer = closure.customer
        status = closure.status
        if customer not in customer_status_count:
            customer_status_count[customer] = {}
        if status not in customer_status_count[customer]:
            customer_status_count[customer][status] = 0
        customer_status_count[customer][status] += 1
    table = '<table text-align="center" border="1" width="100%" style="border-collapse: collapse;text-align: center;">'
    table += '<tr style="background-color: #87CEFA"><td style="width: 45%; font-weight: bold; text-align: center;">Customer</td><td style="width: 30%; font-weight: bold; text-align: center;">Status</td><td style="width: 25%; font-weight: bold; text-align: center;">Count</td></tr>'
    for customer, statuses in customer_status_count.items():
        total_counts = sum(statuses.values())
        table += '<tr><td><b>%s</b></td><td></td><td><b>%s</b></td></tr>' % (customer, total_counts)        
        for status, count in statuses.items():
            table += '<tr><td></td><td>%s</td><td>%s</td></tr>' % (status, count)
    table += '</table>'
    total_count = sum(sum(status.values()) for status in customer_status_count.values())
    return table, total_count


@frappe.whitelist()
def get_vpi_details(name, ins):
    unique_details = set()
    result = []

    edu_checks = frappe.get_all('Education Checks', 
        filters={'custom_institute': ins, 'name': ['!=', name]},
        fields=['name']
    )
    frappe.errprint('HIII')
    frappe.errprint(edu_checks)
    for edu in edu_checks:
        vpi_details = frappe.get_all('Institute Details',
            filters={'parent': edu.name, 'parenttype': 'Education Checks'},
            fields=['verified_by', 'name1', 'designation', 'contact']
        )
        for vpi in vpi_details:
            frappe.errprint(vpi_details)
            detail_tuple = (
                vpi.verified_by or '',
                vpi.name1 or '',
                vpi.designation or '',
                vpi.contact or ''
            )

            if any(detail_tuple): 
                if detail_tuple not in unique_details:
                    unique_details.add(detail_tuple)
                    result.append({
                        'verified_by': vpi.verified_by,
                        'name1': vpi.name1,
                        'designation': vpi.designation,
                        'contact': vpi.contact
                    })

    return result
