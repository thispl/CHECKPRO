// Copyright (c) 2020, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('All Checks', {
	refresh: function(frm) {

	},
	// onload: function (frm) {
	// 	frappe.call({
	// 		"method": "frappe.client.get_list",
	// 		args: {
	// 			"doctype": "Checks",
	// 			"fields": ["check_name", "ce_tat", "check_price"]

	// 		},
	// 		callback: function (r) {
	// 			// if(frm.doc.description!=1){
    //             $.each(r.message, function (i, d) {
    //                 check_name.push(d.check_name)
    //                 ce_tat.push(d.ce_tat)
    //                 check_price.push(d.check_price)
        
	// 			refresh_field("checks_list")
	// 		}
	// 	})
	// },
});
