# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.permissions import add_permission, update_permission_property
import json

class Checks(Document):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    def validate(self):
        vcheck = frappe.db.exists("DocType",self.check_name)
        # frappe.errprint("hello")
        if vcheck:
            frappe.throw(self.check_name + ' ' + "already exists.")
        else:
            # frappe.errprint("hi")
            ac=frappe.new_doc("All Checks")
            ac.check_name=self.check_name
            ac.check_price=self.check_price
            ac.ce_tat=self.ce_tat
            ac.save(ignore_permissions=True)
            vadd_check = frappe.new_doc("DocType")
            vadd_check.name = self.check_name
            vadd_check.module = "Checkpro"
            vadd_check.autoname = self.check_name+ '-.###'
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"CE TAT(days)",
            "read_only":1,
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Customer",
            "read_only":1,
            "mandatory_depends_on":"eval:!doc.__islocal",
            "in_standard_filter":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "mandatory_depends_on":"eval:!doc.__islocal",
            "label":"Customer Shortcode",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Entry Status",
            "mandatory_depends_on":"eval:!doc.__islocal",
            "options":"\nPending\nCompleted\nInsufficient\nHold\nDrop",
            "default":"Pending",
            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
            })
            
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Report Status",
            "options":"\nPending\nPositive\nNegative\nDilemma\nInterim",
            "default":"Pending",
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+ "doc.workflow_state ==" +'"Pending for Verification"',
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "depends_on":"eval:doc.workflow_state==" +'"Pending for Verification"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Small Text",
            "label":"Observation",
            "mandatory_depends_on":"eval:!doc.__islocal" +'&&'+ "doc.workflow_state ==" +'"Pending for Verification"',
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "depends_on":"eval:doc.workflow_state==" +'"Pending for Verification"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Check Package",
            "read_only":1,
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "in_standard_filter":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Batch",
            "read_only":1,
            # "mandatory_depends_on":"eval:!doc.__islocal",
            })
            vadd_check.append("fields",{
            "label":"Proof Attachment",
            "fieldtype":"Attach",
            "depends_on":"eval:doc.workflow_state==" +'"Pending for Verification"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Attachment Description",
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+ "doc.workflow_state ==" +'"Pending for Verification"',
            "depends_on":"eval:doc.workflow_state==" +'"Pending for Verification"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Entry",
            "mandatory_depends_on":"eval:!doc.__islocal",
            "default":"Today",
            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Verification Status",
            "options":"\nPending\nCompleted\nInsufficient\nHold\nDrop",
            "default":"Pending",
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
            "depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+'||'+'doc.workflow_state ==' +'"Pending for Verification"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "label":"Case Information",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Case ID",
            "read_only":1,
            # "mandatory_depends_on":"eval:!doc.__islocal",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Name",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Birth",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Gender",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Age",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Father Name",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Contact Number",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Email ID",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Client Employee Code",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Address",
            # "mandatory_depends_on":"eval:!doc.__islocal",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            })
        
            for c in self.check_variables:
                if c.variable_type=="Select":
                    vadd_check.append("fields",{
                        "fieldtype":"Select",
                        "options":'\n'+ c.options,
                        "label":"""EPI :"""+c.variable,
                        "fieldname":"epi_"+c.variable,
                        # "mandatory_depends_on":"eval:!doc.__islocal && doc.workflow_state == 'Draft' """,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+ "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                        })
                if c.variable_type=="Number":
                    vadd_check.append("fields",{
                        "fieldtype":"Int",
                        "label":"""EPI :"""+c.variable,
                        "fieldname":"epi_"+c.variable,
                        "mandatory_depends_on":"eval:!doc.__islocal && doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Description":
                    vadd_check.append("fields",{
                        "fieldtype":"Small Text",
                        "label":'EPI'+ " :"+c.variable,
                        "fieldname":"epi_"+c.variable,
                        "mandatory_depends_on":"eval:!doc.__islocal" + '&&' + "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Text":
                    if c.variable != "Specialization":
                        vadd_check.append("fields",{
                            "fieldtype":"Data",
                            "label":'EPI'+" :" +c.variable,
                            "fieldname":"epi_"+c.variable,
                            "mandatory_depends_on":"eval:!doc.__islocal" + '&&' + "doc.workflow_state ==" +'"Draft"',
                            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                        })
                if c.variable_type=="Date":
                    vadd_check.append("fields",{
                	    "fieldtype":"Date",
                	    "label":'EPI'+ " :"+c.variable,
                        "fieldname":"epi_"+c.variable,
                        "mandatory_depends_on":"eval:!doc.__islocal" + '&&' + "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Section":
                    vadd_check.append("fields",{
                	    "fieldtype":"Section Break",
                        "label":'EPI'+ " :"+c.variable,
                        "fieldname":"epi_"+c.variable,
                        "mandatory_depends_on":"eval:!doc.__islocal" + '&&' + "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Column":
                    vadd_check.append("fields",{
                	    "fieldtype":"Column Break",
                        "label":'EPI'+ " :"+c.variable,
                        "fieldname":"epi_"+c.variable,
                        "mandatory_depends_on":"eval:!doc.__islocal"+ '&&' + "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Link":
                    vadd_check.append("fields",{
                	    "fieldtype":"Link",
                        "label":'EPI'+ ":"+c.variable,
                        "fieldname":"epi_"+c.variable,
                        "options":c.options,
                        "mandatory_depends_on":"eval:!doc.__islocal" + '&&' + "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable=="Specialization":
                    vadd_check.append("fields",{
                        "fieldtype":"Link",
                        "options":"Specialization",
                        "label":"EPI Specialization",
                        "mandatory_depends_on":"eval:!doc.__islocal" + '&&' + "doc.workflow_state ==" +'"Draft"',
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            

            for c in self.check_variables:
                if c.variable_type=="Select":
                    vadd_check.append("fields",{
                        "fieldtype":"Select",
                        "options":'\n'+c.options,
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+ '&&'+"doc.workflow_state ==" +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    })
                if c.variable_type=="Number":
                    vadd_check.append("fields",{
                        "fieldtype":"Int",
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    
                    })
                if c.variable_type=="Description":
                    vadd_check.append("fields",{
                        "fieldtype":"Small Text",
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    })
                if c.variable_type=="Text":
                    if c.variable != "Specialization":
                        vadd_check.append("fields",{
                            "fieldtype":"Data",
                            "label":'VPI'+ ":"+c.variable,
                            "fieldname":"vpi_"+c.variable,
                            "permlevel":1,
                            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                        
                        })
                if c.variable_type=="Date":
                    vadd_check.append("fields",{
                        "fieldtype":"Date",
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state =="+'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    
                    })
                if c.variable_type=="Section":
                    vadd_check.append("fields",{
                        "fieldtype":"Section Break",
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                       
                    })
                if c.variable_type=="Column":
                    vadd_check.append("fields",{
                        "fieldtype":"Column Break",
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    })
                if c.variable_type=="Link":
                    vadd_check.append("fields",{
                        "fieldtype":"Link",
                        "label":'VPI'+ ":"+c.variable,
                        "fieldname":"vpi_"+c.variable,
                        "options":c.options,
                        "permlevel":1,
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    })
                if c.variable=="Specialization":
                    vadd_check.append("fields",{
                        "fieldtype":"Link",
                        "options":"Specialization",
                        "label":"VPD Specialization",
                        "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"'
                    })
            vadd_check.append("fields",{
                "fieldtype":"Column Break",
                "permlevel":1
            })
            for c in self.check_variables:
                vadd_check.append("fields",{
                    "fieldtype":"Select",
                    "options": "\nPositive\nNegative\nDilemma",
                    "label":c.variable +":"+"Line Status",
                    "fieldname":c.variable +"_line_status",
                    "mandatory_depends_on":"eval:!doc.__islocal"+ '&&' + "doc.workflow_state ==" +'"Pending for Verification"',
                    "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
                    "permlevel":1
                })
            vadd_check.append("fields",{
            "fieldtype":"Section Break"
            })
            vadd_check.append("fields",{
            "fieldtype":"Small Text",
            "label":"Remarks"
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Attach",
            "label":"Attachment"
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "label":"Entry Details",
            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
            })
            vadd_check.append("fields",{
            "label":"Entered By",
            "fieldtype":"Link",
            "options":"User",
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Draft"',
            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Designation",
            "fieldname":"entry_designation",
            "fetch_from":"entered_by.first_name",
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Draft"',
            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "label":"Verification Details",
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Link",
            "label":"Verified By",
            "options":"User",
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Designation",
            "fetch_from":"verified_by.first_name",
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Start Date",
            "default":"Today",
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Completion",
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+ '||'+"doc.workflow_state ==" +'"Approved"',
            "mandatory_depends_on":"eval:!doc.__islocal"+'&&'+'doc.workflow_state ==' +'"Pending for Verification"',
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'
            }) 
            vadd_check.append("fields",{
            "fieldtype":"Link",
            "options":"User",
            "label":"Approved By",
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Approved"',
            "depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+'||'+'doc.workflow_state ==' +'"Approved"',
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            "depends_on":"doc.workflow_state =="+'"Pending for Approval"',
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Designation",
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Approved"',
            "fieldname":"approved_designation",
            "fetch_from":"approved_by.first_name",
            "depends_on":"eval:doc.workflow_state ==" +'"Pending for Approval"'+'||'+'doc.workflow_state ==' +'"Approved"',
            })

            vadd_check.append("permissions",{
                "role":"System Manager",
                "read":1,
                "write":1,
                "delete":1
            })
            vadd_check.append("permissions",{
                "role":"VPI user",
                "read":1,
                "write":1,
                "delete":1
            })
            vadd_check.append("permissions",{
                "role":"Check Executive",
                "read":1,
                "write":1,
                "delete":1
            })
            vadd_check.flags.ignore_mandatory=True
            vadd_check.save(ignore_permissions=True)
            doctype = vadd_check.name
            add_permission(doctype,"VPI user", 1)
            update_permission_property(doctype, "VPI user", 1, 'write', 1)
            add_permission(doctype,"Check Executive", 1)
            update_permission_property(doctype, "Check Executive", 1, 'write', 1)
            if(vadd_check.name):
                wf = frappe.new_doc("Workflow")
                wf.workflow_name=vadd_check.name
                wf.document_type=vadd_check.name
                wf.is_active=1
                wf.append("states",{
                    "state":"Draft",
                    "allow_edit":"System Manager"
                })
                # wf.append("states",{
                #     "state":"Pending for Verification",
                #     "allow_edit":"VPI user"
                # })
                wf.append("states",{
                    "state":"Pending for Verification",
                    "allow_edit":"Check Executive"
                })
                wf.append("states",{
                    "state":"Pending for Approval",
                    "allow_edit":"Approver"
                })
                wf.append("states",{
                    "state":"Approved",
                    "allow_edit":"Approver"
                })
                wf.append("transitions",{
                    "state":"Draft",
                    "action":"EPI QC",
                    "next_state":"Pending for Verification",
                    "condition":"doc.entry_status" +"=="+'"Completed"',
                    "allowed":"System Manager"
                })
                # wf.append("transitions",{
                #     "state":"Pending for Verification",
                #     "action":"VPD QC",
                #     "next_state":"Pending for QC",
                #     "condition":"doc.execution_status" +"!="+'"Pending"',
                #     "allowed":"VPI user"
                # })
                wf.append("transitions",{
                    "state":"Pending for Verification",
                    "action":"VPI QC",
                    "next_state":"Pending for Approval",
                    "condition":"""doc.report_status=="Positive" and doc.verification_status=="Completed" """,
                    "allowed":"Check Executive"
                })
                wf.append("transitions",{
                    "state":"Pending for Approval",
                    "action":"Approve",
                    "next_state":"Approved",
                    "allowed":"Approver"
                })
                wf.save(ignore_permissions=True)
            if(vadd_check.name):
                ds = frappe.get_doc("Desk Page","checkPRO")
                for i in ds.cards:
                    # frappe.errprint(i.label)
                    if i.label == "Checks":
                        links="""
                            ,{
                            "label": "%s",
                            "name": "%s",
                            "type": "doctype"
                                }
                            ]"""%(vadd_check.name,vadd_check.name)
                        a = json.dumps(i.links)
                        b = json.loads(a)
                        i.links = b[:-1] + links
                        ds.save(ignore_permissions=True)