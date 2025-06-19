// Copyright (c) 2024, saru and contributors
// For license information, please see license.txt

frappe.query_reports["DPR Report"] = {
	"filters": [
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
			
		}

	]
};
