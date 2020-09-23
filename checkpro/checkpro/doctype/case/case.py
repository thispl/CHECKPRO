# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Case(Document):
    def validate(self):
        check_package = frappe.get_all("Check Package",{"name":self.check_package})
        for ch in check_package:
            check = frappe.get_doc("Check Package",ch)
            check_list = check.checks_list
            for checks in check_list:
                un = int(checks.units)
                for unit in range(un):
                   
                    create_check1 = frappe.new_doc(checks.checks)
                    create_check1.ce_tat = checks.ce_tat
                    create_check1.customer = self.customer
                    create_check1.check_package = self.check_package
                    create_check1.batch = self.batch
                    create_check1.case_id = self.name
                    create_check1.case_name = self.case_name
                    create_check1.date_of_birth = self.date_of_birth
                    create_check1.case_gender = self.case_gender
                    create_check1.father_name = self.father_name
                    create_check1.email_id = self.email_id
                    create_check1.client_employee_code = self.client_employee_code
                    
                    create_check1.insert()
                    create_check1.save(ignore_permissions=True)
                    create_check = frappe.new_doc("Verify"+" "+checks.checks)
                    create_check.epi = create_check1.name
                    create_check.ce_tat = checks.ce_tat
                    create_check.customer = self.customer
                    create_check.check_package = self.check_package
                    create_check.batch = self.batch
                    create_check.case_id = self.name
                    create_check.case_name = self.case_name
                    create_check.date_of_birth = self.date_of_birth
                    create_check.case_gender = self.case_gender
                    create_check.father_name = self.father_name
                    create_check.email_id = self.email_id
                    create_check.client_employee_code = self.client_employee_code
                    create_check.insert()
                    create_check.save(ignore_permissions=True)
@frappe.whitelist()
def get_checks(check_package):
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

            






    

   










    

   


    

   
                    



            



           