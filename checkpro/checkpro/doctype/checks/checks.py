# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Checks(Document):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    def validate(self):
        check = frappe.db.exists("DocType",self.check_name)
        if check:
            frappe.throw(self.check_name + ' ' + "already exists.")
            # variable = frappe.get_doc("Doctype",self.check_name)
            # frappe.errprint(variable)
        else:
            add_check = frappe.new_doc("DocType")
            add_check.name = self.check_name
            add_check.module = "veriPRO"
            frappe.errprint("hi")
            add_check.autoname = self.check_name + '-.###'
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"CE TAT",
            "read_only":1,
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Customer",
            "read_only":1,
            "in_standard_filter":1
            })
           
            add_check.append("fields",{
            "fieldtype":"Select",
            "label":"Status",
            "options":"Completed\nPending\nInsufficient\nHold\nDrop"
          
            })
            add_check.append("fields",{
            "fieldtype":"Column Break",
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Check Package",
            "read_only":1,
            "in_standard_filter":1
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Batch",
            "read_only":1,
            "in_standard_filter":1
            
            })
            add_check.append("fields",{
            "fieldtype":"Section Break",
            "label":"Case Information",
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case ID",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case Name",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Birth",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case Gender",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Column Break",
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Father Name",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Contact Number",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Email ID",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Client Employee Code",
            "read_only":1
            })
            add_check.append("fields",{
            "fieldtype":"Section Break",
            })
            for c in self.check_variables:
                if c.variable_type=="Select":
                    add_check.append("fields",{
                        "fieldtype":"Select",
                        "options":c.options,
                        "label":c.variable,
                        
                    }) 
                if c.variable_type=="Text":
                    add_check.append("fields",{
                        "fieldtype":"Data",
                        "label":c.variable,
                        
                    })
                if c.variable_type=="Number":
                    add_check.append("fields",{
                        "fieldtype":"Int",
                        "label":c.variable,
                       
                        

                    })
                if c.variable_type=="Date":
                    add_check.append("fields",{
                	    "fieldtype":"Date",
                	    "label":c.variable,
                       
                    })
                if c.variable_type=="Description":
                    add_check.append("fields",{
                	    "fieldtype":"Small Text",
                	    "label":c.variable,
                       
                    })
                if c.variable_type=="Section":
                    add_check.append("fields",{
                	    "fieldtype":"Section Break",
                        "label":c.variable,
                        
                	    
                    })
                if c.variable_type=="Column":
                    add_check.append("fields",{
                	    "fieldtype":"Column Break",
                        "label":c.variable,
                      
                	    
                    })
                if c.variable_type=="Link":
                    add_check.append("fields",{
                	    "fieldtype":"Link",
                        "label":c.variable,
                        "options":c.options
                      
                    })
                if c.variable_type=="Table":
                    add_check.append("fields",{
                	    "fieldtype":"Table",
                        "label":c.variable,
                        "options":c.options
                      
                    })
                
                
              
            add_check.append("fields",{
            "fieldtype":"Section Break",
            }) 
            add_check.append("fields",{
            "fieldtype":"Data",
            "label":"Check Executive",
            "read_only":1
            })

            
            add_check.append("permissions",{
            "role":"System Manager",
            "read":1,
            "write":1,
            "create":1,
            "delete":1
            })
            add_check.append("permissions",{
            "role":"DE Executive",
            "read":1,
            "write":1,
            "create":1,
            "delete":1
            })
            add_check.append("permissions",{
            "role":"Check Executive",
            "read":1,
            })
            add_check.save(ignore_permissions=True)
            
        

        vcheck = frappe.db.exists("DocType",'Verify'+' '+self.check_name)
        if vcheck:
            frappe.erprint("yes")
            frappe.throw('Verify'+' '+self.check_name + ' ' + "already exists.")
        else:
            vadd_check = frappe.new_doc("DocType")
            vadd_check.name = "Verify"+" "+self.check_name
            vadd_check.module = "veriPRO"
            vadd_check.autoname = 'Verify'+' '+self.check_name+ '-.###'
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"CE TAT",
            "read_only":1,
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Customer",
            "read_only":1,
            "in_standard_filter":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Status",
            "options":" \n\Completed\nPending\nInsufficient\nHold\nDrop"
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Check Package",
            "read_only":1,
            "in_standard_filter":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Batch",
            "read_only":1,
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "label":"Case Information",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case ID",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case Name",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Birth",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case Gender",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Father Name",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Contact Number",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Email ID",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Client Employee Code",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            })
        
            for c in self.check_variables:
                if c.variable_type=="Select":
                     vadd_check.append("fields",{
                        "fieldtype":"Select",
                        "options":c.options,
                        "label":c.variable
                    })
                if c.variable_type=="Number":
                    vadd_check.append("fields",{
                        "fieldtype":"Int",
                        "label":c.variable
                    })
                if c.variable_type=="Description":
                    vadd_check.append("fields",{
                        "fieldtype":"Small Text",
                        "label":c.variable
                    })
                if c.variable_type=="Text":
                    vadd_check.append("fields",{
                	    "fieldtype":"Data",
                	    "label":c.variable
                    })
                if c.variable_type=="Date":
                    vadd_check.append("fields",{
                	    "fieldtype":"Date",
                	    "label":c.variable
                    })
                if c.variable_type=="Section":
                    add_check.append("fields",{
                	    "fieldtype":"Section Break",
                        "label":c.variable,
                        
                    })
                if c.variable_type=="Column":
                    add_check.append("fields",{
                	    "fieldtype":"Column Break",
                        "label":c.variable,  
                    })
                if c.variable_type=="Link":
                    add_check.append("fields",{
                	    "fieldtype":"Link",
                        "label":c.variable,
                        "options":c.options
                      
                    })
              
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "label":"Verification Details"
            })
            vadd_check.append("fields",{
            "fieldtype":"Link",
            "label":"Verified By",
            "options":"User"
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Designation",
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Entry",
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Initiation",
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Completion",
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            }) 
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Check Executive",
            "read_only":1
            })

            vadd_check.append("permissions",{
                "role":"System Manager",
                "read":1,
                "write":1,
                "create":1,
                "delete":1
            })
            vadd_check.append("permissions",{
            "role":"Check Executive",
            "read":1,
            "write":1,
            "create":1,
            "delete":1
            })
            
            vadd_check.save(ignore_permissions=True)

        # # vcheck = frappe.db.exists("DocType",'Verify' + ' ' + checks.checks)
        # # if vcheck:
        # # 	frappe.throw("Verify" + '' + self.check_name + ' ' + "already exists")	
        # # else:
        # # 	vadd_check = frappe.new_doc("DocType")
        # #     vadd_check.name = self.check_name
        # #     vadd_check.module = "veriPRO"
        # #     for c in self.check_variables:
        # # 	    if c.variable_type=="Select":
        # # 		    vadd_check.append("fields",{
        # # 			    "fieldtype":"Select",
        # # 			    "options":c.options,
        # # 			    "label":c.variable
        # # 		    })
        # # 	    if c.variable_type=="Number":
        # # 		    vadd_check.append("fields",{
        # # 		    	"fieldtype":"Int",
        # # 			    "label":c.variable
        # # 		    })
        # # 	    if c.variable_type=="Description":
        # # 		    vadd_check.append("fields",{
        # # 			    "fieldtype":"Small Text",
        # # 			    "label":c.variable
        # # 		    })
        # #     vadd_check.append("permissions",{
        # # 	    "role":"System Manager",
        # # 	    "read":1,
        # # 	    "write":1,
        # # 	    "create":1,
        # # 	    "delete":1
        # # 	})
        # #     vadd_check.insert()
        # #     vadd_check.save(ignore_permissions=True)
            
            


            
        # # # # check = frappe.db.exists("DocType",self.check_name)
        # # # # if check:
        # # # # 	c1 = frappe.get_doc(self.check_name)
        # # # else:
        # # # 	add_check = frappe.new_doc("DocType")
        # # # 	for c in self.check_variables:
        # # # 		if 

        
        # # #   add_check.update({
            
        # # # 	add_check.name:self.check_name,
        # # # 	add_check.module:"veriPRO"
        # # # 	for c in self.check_variables:
        # # # 		if c.variable_type=="Select":
        # # # 		   add_check.append("fields",{
        # # # 			   "fieldtype":"Select",
        # # # 			   "options":c.options,
        # # # 			   "label":c.variable
        # # # 		   })
        # # # 		if c.variable_type=="Text":
        # # # 		   add_check.append("fields",{
        # # # 			   "fieldtype":"Data",
        # # # 			   "label":c.variable
        # # # 		   })
        # # # 		if c.variable_type=="Number":
        # # # 			add_check.append("fields",{
        # # # 			   "fieldtype":"Int",
        # # # 			   "label":c.variable
        # # # 			})
        # # # 		if c.variable_type=="Description":
        # # # 		    add_check.append("fields",{
        # # # 			   "fieldtype":"Small Text",
        # # # 			   "label":c.variable
        # # # 		    })
        # # # 	add_check.append("permissions",{
        # # # 	    "role":"System Manager",
        # # # 	    "read":1,
        # # # 	    "write":1,
        # # # 	    "create":1,
        # # # 	    "delete":1
        # # # 	})
        # # # add_check.insert()
        # # # add_check.save(ignore_permissions=True)
        # # # })

                    