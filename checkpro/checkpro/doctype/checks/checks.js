// Copyright (c) 2020, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Checks', {
	refresh: function(frm) {

	},
	before_save:function(frm){
		var regex = /[^0-9A-Za-z]+$/g;
		$.each(frm.doc.check_variables,function(i,d){
			if (regex.test(d.variable) === true){
				console.log(d.variable)
				frappe.msgprint(__("variable: Only letters and numbers are allowed."));
				frappe.validated = false;
		}

	})
	},
	// after_workflow_action:(frm)=>{
	// 	console.log("hi")
	// 	if (frm.doc.workflow_state == "Pending for QC") {
	// 		frm.set_value("date_of_initiation",frappe.datetime.nowdate())
	// 		console.log(frm.doc.workflow_state)
	// }

	// }
	// onload(frm){
	// 	"workflow_state": frm => {
	// 		if (frm.doc.workflow_state == "My Target State"){
	// 			frm.set_value("actual_end_date", frappe.datetime.nowdate());
	// 		}
	// 		}
	// }
	
});
