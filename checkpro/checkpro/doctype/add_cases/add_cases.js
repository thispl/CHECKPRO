// Copyright (c) 2020, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Add Cases', {
	refresh: function(frm) {
		frm.disable_save();
	},
	add_demographic_data:function(frm){
		frappe.set_route('List','Case')
	},
	add_bulk_excel:function(frm){
		frappe.set_route('List','Bulk Upload')
	},
	add_attachment:function(frm){
		frappe.set_route('List','Bulk Attachment')
	},


});
