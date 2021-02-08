# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.permissions import add_permission, update_permission_property

class Checks(Document):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    def validate(self):
        vcheck = frappe.db.exists("DocType",self.check_name)
        if vcheck:
            frappe.throw(self.check_name + ' ' + "already exists.")
        else:
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
            "in_standard_filter":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Customer Shortcode",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Entry Status",
            "options":"\nPending\nCompleted\nInsufficient\nHold\nDrop",
            "default":"Pending",
            "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Execution Status",
            "options":"\nPending\nCompleted\nInsufficient\nHold\nDrop",
            "default":"Pending",
            "depends_on":"eval:doc.workflow_state==" +'"Pending for Verification"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'+'||'+'doc.workflow_state ==' +'"Pending for QC"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Select",
            "label":"Report Status",
            "options":"\nPending\nGreen\nRed\nAmber\nInterim",
            "default":"Pending",
            "depends_on":"eval:doc.workflow_state==" +'"Pending for QC"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Small Text",
            "label":"Observation",
            "depends_on":"eval:doc.workflow_state==" +'"Pending for QC"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'
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
            "label":"Proof Attachment",
            "fieldtype":"Attach",
            "depends_on":"eval:doc.workflow_state==" +'"Pending for QC"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Attachment",
            "depends_on":"eval:doc.workflow_state==" +'"Pending for QC"'+'||'+'doc.workflow_state ==' +'"Pending for Approval"'
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Entry",
            "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"' +'||'+'doc.workflow_state ==' +'"Pending for Verification"'
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
            "label":"Name",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Birth",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Gender",
            "read_only":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Age",
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
                        "label":'EPI'+" "+c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                        })
                if c.variable_type=="Number":
                    vadd_check.append("fields",{
                        "fieldtype":"Int",
                        "label":'EPI'+" " +c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Description":
                    vadd_check.append("fields",{
                        "fieldtype":"Small Text",
                        "label":'EPI'+ " "+c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Text":
                    vadd_check.append("fields",{
                	    "fieldtype":"Data",
                	    "label":'EPI'+" " +c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Date":
                    vadd_check.append("fields",{
                	    "fieldtype":"Date",
                	    "label":'EPI'+ " "+c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Section":
                    vadd_check.append("fields",{
                	    "fieldtype":"Section Break",
                        "label":'EPI'+ " "+c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Column":
                    vadd_check.append("fields",{
                	    "fieldtype":"Column Break",
                        "label":'EPI'+ " "+c.variable,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
                if c.variable_type=="Link":
                    vadd_check.append("fields",{
                	    "fieldtype":"Link",
                        "label":'EPI'+ " "+c.variable,
                        "options":c.options,
                        "read_only_depends_on":"eval:doc.workflow_state!=" +'"Draft"'
                    })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            })
            

            for c in self.check_variables:
                if c.variable_type=="Select":
                    vadd_check.append("fields",{
                        "fieldtype":"Select",
                        "options":c.options,
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    })
                if c.variable_type=="Number":
                    vadd_check.append("fields",{
                        "fieldtype":"Int",
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    
                    })
                if c.variable_type=="Description":
                    vadd_check.append("fields",{
                        "fieldtype":"Small Text",
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    })
                if c.variable_type=="Text":
                    vadd_check.append("fields",{
                        "fieldtype":"Data",
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    
                    })
                if c.variable_type=="Date":
                    vadd_check.append("fields",{
                        "fieldtype":"Date",
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    
                    })
                if c.variable_type=="Section":
                    vadd_check.append("fields",{
                        "fieldtype":"Section Break",
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                       
                    })
                if c.variable_type=="Column":
                    vadd_check.append("fields",{
                        "fieldtype":"Column Break",
                        "label":'VPD'+ " "+c.variable,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    })
                if c.variable_type=="Link":
                    vadd_check.append("fields",{
                        "fieldtype":"Link",
                        "label":'VPD'+ " "+c.variable,
                        "options":c.options,
                        "permlevel":1,
                        "read_only_depends_on":"eval:doc.workflow_state ==" +'"Pending for QC"' +'||'+'doc.workflow_state ==' +'"Pending for Approval"'
                    })
            vadd_check.append("fields",{
                "fieldtype":"Column Break",
                "permlevel":2
            })
            for c in self.check_variables:
                vadd_check.append("fields",{
                    "fieldtype":"Select",
                    "options": "Positive\nNegative",
                    "label":c.variable +" "+"Line Status",
                    "permlevel":2
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
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Data",
            "label":"Designation",
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Column Break",
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Initiation",
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Date",
            "label":"Date of Completion",
            "permlevel":1
            })
            vadd_check.append("fields",{
            "fieldtype":"Section Break",
            "permlevel":1
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
                "role":"VPI user",
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
            doctype = vadd_check.name
            add_permission(doctype,"VPI user", 1)
            update_permission_property(doctype, "VPI user", 1, 'write', 1)
            add_permission(doctype,"Check Executive", 2)
            update_permission_property(doctype, "Check Executive", 2, 'write', 1)
            if(vadd_check.name):
                wf = frappe.new_doc("Workflow")
                wf.workflow_name=vadd_check.name
                wf.document_type=vadd_check.name
                wf.is_active=1
                wf.append("states",{
                    "state":"Draft",
                    "allow_edit":"System Manager"
                })
                wf.append("states",{
                    "state":"Pending for Verification",
                    "allow_edit":"VPI user"
                })
                wf.append("states",{
                    "state":"Pending for QC",
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
                    "action":"Review",
                    "next_state":"Pending for Verification",
                    "allowed":"System Manager"
                })
                wf.append("transitions",{
                    "state":"Pending for Verification",
                    "action":"Review",
                    "next_state":"Pending for QC",
                    "allowed":"VPI user"
                })
                wf.append("transitions",{
                    "state":"Pending for QC",
                    "action":"Review",
                    "next_state":"Pending for Approval",
                    "allowed":"Check Executive"
                })
                wf.append("transitions",{
                    "state":"Pending for Approval",
                    "action":"Approve",
                    "next_state":"Approved",
                    "allowed":"Approver"
                })
                wf.save(ignore_permissions=True)