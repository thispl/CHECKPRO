# Copyright (c) 2024, saru and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate,add_days
import datetime
from frappe.utils import date_diff, add_months,today,add_days,nowdate,flt
from datetime import datetime
from frappe import msgprint, _
from calendar import monthrange
from doctest import SKIP
from lzma import FORMAT_RAW
from unittest import skipUnless

import datetime
from datetime import date, datetime
from frappe import msgprint, _
from calendar import monthrange


def execute(filters=None):
    columns = get_columns()
    data = dpr_report(filters)
    return columns, data

def get_columns():
    columns = [
        _("User ID") + ":Data:250",
        _("Employee Name") + ":Data:200",
        _("Allocated") + ":Data:150",
        _("0-6") + ":Data:120",
        _("7-10") + ":Data:120",
        _(">10") + ":Data:120",
    ]
    return columns

def dpr_report(filters):
    user = frappe.get_all("User", filters={"role": "BCS User","enabled":1}, fields=["name", "full_name"])
    data = []
    for u in user:
        case_count = 0
        check_count = 0
        age6 = 0
        age10 = 0
        age11 = 0
        cases = frappe.get_all("Case", {"allocated_to": u.name}, ['name',"case_status" ])
        for c in cases:
            if c.case_status=="Draft":
                case_count += 1
                if c.actual_tat:
                    if c.actual_tat <= 6:
                            age6 += 1
                    elif 6 < c.actual_tat <= 10:
                        age10 += 1
                    elif c.actual_tat > 10:
                        age11 += 1
        checklist = ["Education Checks", "Family", "Reference Check", "Court", "Social Media", "Criminal",
                        "Employment", "Identity Aadhar", "Address Check"]
        for check_type in checklist:
            docs = frappe.get_all(check_type, {"allocated_to": u.name}, ['name', 'check_status', 'actual_tat'])
            for doc in docs:
                if doc.check_status=="Draft" or doc.check_status=="Entry Completed" or doc.check_status=="Execution Pending":
                    check_count += 1
                    if doc.actual_tat <= 6:
                        age6 += 1
                    elif 6 < doc.actual_tat <= 10:
                        age10 += 1
                    elif doc.actual_tat > 10:
                        age11 += 1
        row = [u.name, u.full_name, case_count + check_count, age6, age10, age11]
        data.append(row)
    return data



