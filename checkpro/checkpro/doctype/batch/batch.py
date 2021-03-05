# -*- coding: utf-8 -*-
# Copyright (c) 2020, suganya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class Batch(Document):
    pass
@frappe.whitelist()
def get_end_date(name,check_package,expected_start_date):
    check_package = frappe.get_value('Check Package', {'name': check_package},["package_tat"])
    if expected_start_date:
        end_date = add_days(expected_start_date,check_package)
        frappe.errprint(end_date)
        return end_date
@frappe.whitelist()
def get_check_list(check_package):
    check_list = {}
    checks = frappe.get_all('Checks List', {'parent': check_package}, ['check_name', 'units'])
    return checks

@frappe.whitelist()
def get_cases(batch, no_of_case,expected_start_date):
    nc = {}
    for unit in range(int(no_of_case)):
        if frappe.db.count("Case", {'batch': batch}) < int(no_of_case):
            nc = frappe.new_doc("Case")
            nc.batch = batch
            nc.no_of_cases = str((unit+1))+"/"+no_of_case
            nc.date_of_initiating = expected_start_date
            nc.save(ignore_permissions=True)
    return nc


@frappe.whitelist()
def get_checks(check_package):
    check_list = {}
    checks = frappe.get_all('Checks List', {'parent': check_package}, ['check_name', 'units'])
    return checks


@frappe.whitelist()
def check_status(name, check_package):
    check_package = frappe.get_doc('Check Package', {'name': check_package})
    ch = []
    for c in check_package.checks_list:
        # frappe.errprint(c.check_name)
        checks = frappe.get_all(c.check_name, {"batch": name}, [
                                'entry_status', 'report_status', 'verification_status', 'name'])
        # ch=frappe.get_doc("Case",name)
        # frappe.errprint(checks)

        for cs in checks:
            cj = cs["name"]
            sep = cj.split("-")

            ch.append({
                "checks": sep[0],
                "check_id": cs["name"],
                "check_status": cs["entry_status"],
                "verification_status": cs["verification_status"],
                "report_status": cs["report_status"]
            })
    return ch