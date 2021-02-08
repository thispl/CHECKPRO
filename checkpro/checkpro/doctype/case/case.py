# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Case(Document):
    def validate(self):
        if not self.checks_created:
            cp = frappe.get_doc("Check Package",self.check_package)
            cp_checks = cp.checks_list
            for cp_check in cp_checks:
                frappe.errprint(cp_check)
                for unit in range(int(cp_check.units)):
                    # create_entry_check = frappe.new_doc(cp_check.checks)
                    # create_entry_check.flags.ignore_permissions  = True
                    # create_entry_check.update({
                    #     "ce_tat": cp_check.ce_tat,
                    #     "customer" : self.customer,
                    #     "check_package" : self.check_package,
                    #     "batch" : self.batch,
                    #     "case_id" : self.name,
                    #     "case_name" : self.case_name,
                    #     "date_of_birth" : self.date_of_birth,
                    #     "case_gender" : self.case_gender,
                    #     "father_name" :self.father_name,
                    #     "email_id" : self.email_id,
                    #     "client_employee_code" : self.client_employee_code
                    # }).save()
                    # entry_check = frappe.get_value(cp_check.checks,{'case_id':self.name},['name'])
                    # frappe.errprint(entry_check)
                    check =frappe.get_value("Checks",cp_check.checks,["ce_tat"])
                    sh =frappe.get_value("Customer",self.customer,["short_code"])
                    create_verify_check = frappe.new_doc(cp_check.checks)
                    create_verify_check.flags.ignore_permissions  = True
                    frappe.errprint(create_verify_check)
                    create_verify_check.update({
                        "ce_tatdays": check,
                        "customer" : self.customer,
                        "customer_shortcode": sh,
                        "check_package" : self.check_package,
                        "batch" : self.batch,
                        "case_id" : self.name,
                        "name1" : self.case_name,
                        "date_of_birth" : self.date_of_birth,
                        "age":self.age,
                        "gender" : self.case_gender,
                        "father_name" :self.father_name,
                        "email_id" : self.email_id,
                        "client_employee_code" : self.client_employee_code,
                        "contact_number":self.contact
                        # "entry_id": entry_check
                    }).save()
            self.checks_created = 1

@frappe.whitelist()
def get_checks(check_package):
    check_list = {}
    checks = frappe.get_all('Checks List',{'parent':check_package},['checks'])
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
        frappe.errprint(c.checks)
        checks = frappe.get_all(c.checks,{"case_id":name},['entry_status','report_status','execution_status','name'])
        # ch=frappe.get_doc("Case",name)
        # frappe.errprint(checks)
        
        for cs in checks:
            cj=cs["name"]
            sep=cj.split("-")
            
            ch.append({
                "checks":sep[0],
                "check_id":cs["name"],
                "check_status":cs["entry_status"],
                "execution_status":cs["execution_status"],
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