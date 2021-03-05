
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

# @frappe.whitelist()
# def case_count(batch):
#     count = frappe.db.count("Case",{"batch":batch})
#     frappe.errprint(count)
#     b1 = frappe.get_all("Batch",{"name":batch})
#     for b in b1:
#         batch_count = frappe.get_doc("Batch",b)
#         if(batch_count.no_of_cases == count):
#             frappe.throw("Entry not allowed")