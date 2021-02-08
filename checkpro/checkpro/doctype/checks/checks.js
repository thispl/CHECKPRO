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

});
