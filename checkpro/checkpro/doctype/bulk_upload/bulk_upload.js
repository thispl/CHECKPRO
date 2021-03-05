// Copyright (c) 2020, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Upload', {
	// onload: function(frm) {

	// }
	batch:function(frm){
		if (frm.doc.check_package) {
			frappe.call({
				"method": "frappe.client.get",
				args: {
					"doctype": "Check Package",
					"name": frm.doc.check_package,
				},
				callback: function (r) {
						$.each(r.message.checks_list, function (i, d) {
							var row = frappe.model.add_child(frm.doc, "Bulk Upload Checks", "bulk_upload_checks")
							row.check = d.checks
						})
					refresh_field("bulk_upload_checks")
				}
			})
		}
	},
	download_template:function(frm) {
		frappe.require('/assets/js/data_import_tools.min.js', () => {
			frm.data_exporter = new frappe.data_import.DataExporter(
				"Court Record Check",
				"Insert New Records"
			);
		});
	},
});

frappe.ui.form.on('Bulk Upload Checks', {
	download_template:function(frm,cdt,cdn) {
		var row = locals[cdt][cdn];
		frappe.require('/assets/js/data_import_tools.min.js', () => {
			frm.data_exporter = new frappe.data_import.DataExporter(
				row.check,
				"Insert New Records"
			);
		});
	},
});
