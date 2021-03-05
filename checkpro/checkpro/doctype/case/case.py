# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Case(Document):
    def validate(self):
        # if not self.checks_created:
        cp = frappe.get_doc("Check Package",self.check_package)
        cp_checks = cp.checks_list
        # check_package = frappe.get_doc('Check Package',{'name' : check_package })
        # ch =[]
        for c in cp.checks_list:
            checks = frappe.get_all(c.check_name,{"case_id":self.name},['entry_status','name'])
            if not checks:
                for cp_check in cp_checks:
                    # frappe.errprint(cp_check)
                    for unit in range(int(cp_check.units)):
                        check =frappe.get_value("Checks",cp_check.check_name,["ce_tat"])
                        sh =frappe.get_value("Customer",self.customer,["short_code"])
                        create_verify_check = frappe.new_doc(cp_check.check_name)
                        create_verify_check.ce_tatdays= check,
                        create_verify_check.customer=self.customer,
                        create_verify_check.customer_shortcode=sh,
                        create_verify_check.check_package=self.check_package,
                        create_verify_check.batch=self.batch,
                        create_verify_check.case_id=self.name,
                        create_verify_check.name1=self.case_name,
                        create_verify_check.date_of_birth=self.date_of_birth,
                        create_verify_check.age=self.age,
                        create_verify_check.gender=self.case_gender,
                        create_verify_check.father_name=self.father_name,
                        create_verify_check.email_id=self.email_id,
                        create_verify_check.address=self.address,
                        create_verify_check.client_employee_code=self.client_employee_code,
                        create_verify_check.contact_number=self.contact
                        create_verify_check.flags.ignore_mandatory==True
                        create_verify_check.save(ignore_permissions=True)
            else:
                for ch in checks:
                    checks = frappe.get_doc(c.check_name,{"name":ch.name})
                    checks.update({
                        "name1":self.case_name,
                        "date_of_birth":self.date_of_birth,
                        "gender":self.case_gender,
                        "age":self.age,
                        "father_name":self.father_name,
                        "contact_number":self.contact,
                        "address":self.address,
                        "email_id":self.email_id,
                        "client_employee_code":self.client_employee_code,
                    })
                    checks.save(ignore_permissions=True)
                    frappe.db.commit()
        

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