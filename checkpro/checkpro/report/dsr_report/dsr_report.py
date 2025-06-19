from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = dsr_report(filters)
    return columns, data

def get_columns():
    columns = [
        _("User ID") + ":Data:250",
        _("Employee Name") + ":Data:250",
        _("Total Checks") + ":Int:250",
        _("Completed Checks") + ":Int:250",
        _("Pending Checks") + ":Int:220",
    ]
    return columns

def dsr_report(filters):
    current_date = nowdate()  
    year, month, day = current_date.split('-')
    formatted_date = f"{day}-{month}-{year}"
    user_list = frappe.get_all("User", filters={"role": "BCS User", "enabled": 1}, fields=["name", "full_name"])
    data = []
    for user in user_list:
        total_tasks = 0
        pending_tasks = 0
        completed_tasks = 0
        cases = frappe.get_all("Case", {
            "case_status": ("in", ['Draft', "Entry Completed", "Entry-QC", "Entry-Insuff", "Execution", "Execution-Insuff", "Final-QC"]),
            "allocated_to": user.name
        }, ["*"])

        for case in cases:
            if case.case_status in ["Draft", "Entry Completed"]:
                total_tasks += 1
                pending_tasks += 1
            if case.date_of_execution_completion and case.date_of_execution_completion.strftime("%d-%m-%Y") == formatted_date:
                completed_tasks += 1
                total_tasks += 1
        checklist = ["Education Checks", "Family", "Reference Check", "Court", "Social Media", "Criminal", "Employment", "Identity Aadhar", "Address Check"]
        for item in checklist:
            docs = frappe.get_all(item, {"allocated_to": user.name}, ['*'])
            for doc in docs:
                if doc.check_status in ["Draft","Entry QC Completed","Execution Pending","Execution Initiated"]:
                    total_tasks += 1
                    pending_tasks += 1
                if doc.date_of_entry_completion and doc.date_of_entry_completion.strftime("%d-%m-%Y") == formatted_date and doc.entered_by == user.name:
                    completed_tasks += 1
                    total_tasks += 1
                if doc.date_of_execution_completion and doc.date_of_execution_completion.strftime("%d-%m-%Y") == formatted_date and doc.execution_by == user.name:
                    completed_tasks += 1
                    total_tasks += 1
        row = [user.name, user.full_name, total_tasks, completed_tasks, pending_tasks]
        data.append(row)
    return data

