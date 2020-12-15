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
                for unit in range(int(cp_check.units)):
                    create_entry_check = frappe.new_doc(cp_check.checks)
                    create_entry_check.flags.ignore_permissions  = True
                    create_entry_check.update({
                        "ce_tat": cp_check.ce_tat,
                        "customer" : self.customer,
                        "check_package" : self.check_package,
                        "batch" : self.batch,
                        "case_id" : self.name,
                        "case_name" : self.case_name,
                        "date_of_birth" : self.date_of_birth,
                        "case_gender" : self.case_gender,
                        "father_name" :self.father_name,
                        "email_id" : self.email_id,
                        "client_employee_code" : self.client_employee_code
                    }).save()
                    entry_check = frappe.get_value(cp_check.checks,{'case_id':self.name},['name'])
                    # frappe.errprint(entry_check)

                    create_verify_check = frappe.new_doc("Verify"+" "+cp_check.checks)
                    create_verify_check.flags.ignore_permissions  = True
                    create_verify_check.update({
                        "ce_tat": cp_check.ce_tat,
                        "customer" : self.customer,
                        "check_package" : self.check_package,
                        "batch" : self.batch,
                        "case_id" : self.name,
                        "case_name" : self.case_name,
                        "date_of_birth" : self.date_of_birth,
                        "case_gender" : self.case_gender,
                        "father_name" :self.father_name,
                        "email_id" : self.email_id,
                        "client_employee_code" : self.client_employee_code,
                        "entry_id": entry_check
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
    checks_list = frappe.get_all('Check Package',{ 'name' : check_package })
    for checks in checks_list:
        checks1 = frappe.get_doc("Check Package",checks)
        for c in checks1.checks_list:
            check_status = frappe.get_all('Verify'+ ' ' +c.checks,{'case_id':name},['status','name'])
            for cs in check_status:
                cstatus = frappe.get_doc('Verify'+ ' ' +c.checks,cs)  
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