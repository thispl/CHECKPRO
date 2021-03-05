// Copyright (c) 2020, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Court Record Check', {
	// refresh: function(frm) {

	// }
	after_save:function(frm){
		console.log("call")
		frappe.call({
			method:'checkpro.checkpro.doctype.court_record_check.court_record_check.set_epi',
			args:{
				'name': frm.doc.name,
				"case_id": frm.doc.case_id
			},
			callback: function (r) {
				console.log("hi")
			}
		})
	}
});
