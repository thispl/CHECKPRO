// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Case', {
	validate: function (frm) {
		frm.trigger("date_of_birth");
		
	},
	before_submit: function (frm) {
		if (frm.doc.entry_status != "Completed" || frm.doc.ca_status != "Completed" || frm.doc.case_report != "Completed") {
			frappe.throw("Status is pending,Cannot Submit")
		}

	},
	contact(frm) {
		if ((frm.doc.contact).length < 10) {
			frappe.throw("Contact No should be 10 digits")
			frappe.validated = false;
		}
	},
	date_of_birth(frm) {
		var age = calculate_age(frm.doc.date_of_birth)
		// console.log(age)
		frm.set_value("age", age)
		if (age < 18) {
			frappe.msgprint({
				title: __('Notification'),
				indicator: 'red',
				message: __("Age cannot be lesser than 18")
			});
			validated = false;
		}
	},


	refresh: function (frm) {
		if(!frm.doc.tat){
			refresh_field("Batch")
		}
		console.log(frm.doc.entry_status)
		if (frm.doc.entry_status != "Draft") {
		if (frm.doc.entry_status != "Pending") {
			frm.add_custom_button(__("Verify Check Report"), function () {
				var f_name = frm.doc.name
				var print_format = "Final Case Report";
				window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
					+ "doctype=" + encodeURIComponent("Case")
					+ "&name=" + encodeURIComponent(f_name)
					+ "&trigger_print=1"
					+ "&format=" + print_format
					+ "&no_letterhead=0"
				));

			})
			refresh_field("Case")
	}
}
		if (!frm.is_new()) {
			frm.trigger('make_dashboard');
		}
		// frm.add_custom_button('InSufficient', () => {
		// 	frm.set_value("entry_status","InSufficient")
		// 	frm.set_value("ca_status","InSufficient")
		// })
		// frm.add_custom_button('Completed', () => {
		// 	frm.set_value("entry_status","Completed")
		// 	frm.set_value("ca_status","Completed")
		// })




		// if (frm.doc.check_package) {
		// 	// console.log("hi")
		// 	frappe.call({
		// 		"method": "frappe.client.get",
		// 		args: {
		// 			"doctype": "Check Package",
		// 			"name": frm.doc.check_package,
		// 		},
		// 		callback: function (r) {
		// 			if (frm.doc.description != 1) {
		// 				// console.log(r.message.checks_list)
		// 				$.each(r.message.checks_list, function (i, d) {
		// 					var row = frappe.model.add_child(frm.doc, "Checkwise Report", "checkwise_report")
		// 					row.checks = d.checks
		// 					row.units = d.units
		// 					// row.check_status = d.cstatus
		// 					// console.log(d.cstatus)
		// 				})

		// 			}
		// 			frm.set_value("description", 1)
		// 			refresh_field("checkwise_report")
		// 		}
		// 	})
		// }
	},
	onload: function (frm) {
		if (frm.doc.check_package) {
			// if((frm.doc.checkwise_report).length==0){
			frappe.call({
				"method": "checkpro.checkpro.doctype.case.case.check_status",
				args: {
					"name": frm.doc.name,
					"check_package": frm.doc.check_package
				},
				callback: function (r) {
					// console.log(r.message)
					var s = [];
					var es = [];
					var rs = [];

					frm.clear_table("checkwise_report");
					$.each(r.message, function (i, d) {
						// console.log(d)
						var row = frappe.model.add_child(frm.doc, "Checkwise Report", "checkwise_report")
						row.checks = d.checks
						row.units = d.units
						row.check_status = d.check_status
						row.verification_status = d.verification_status
						row.report_status = d.report_status
						row.check_id = d.check_id
						// row.check_html = d.check_id


						s.push(d.check_status)
						// console.log(s)
						es.push(d.verification_status)
						// console.log(es)
						rs.push(d.report_status)
						// console.log(rs)
					})
					refresh_field("checkwise_report")
					if (s.includes("Insufficient")) {
						frm.set_value("entry_status", "Insufficient")
					}
					else if (s.includes("Pending")) {
						frm.set_value("entry_status", "Pending")
					}
					else if (s.includes("Insufficient")) {
						frm.set_value("entry_status", "Insufficient")
					}
					else if (s.includes("Hold")) {
						frm.set_value("entry_status", "Hold")
					}
					else if (s.includes("Drop")) {
						frm.set_value("entry_status", "Drop")
					}
					else if (s.every(e => e == "Completed")) {
						frm.set_value("entry_status", "Completed")
					}
					if (es.includes("Pending")) {
						frm.set_value("ca_status", "Pending")
					}
					else if (es.includes("Insufficient")) {
						frm.set_value("ca_status", "Insufficient")
					}
					else if (es.includes("Hold")) {
						frm.set_value("ca_status", "Hold")
					}
					else if (es.includes("Drop")) {
						frm.set_value("ca_status", "Drop")
					}
					else if (es.every(e => e == "Completed")) {
						frm.set_value("ca_status", "Completed")
					}
					if (rs.includes("Pending")) {
						frm.set_value("case_report", "Pending")
					}
					else if (rs.includes("Interim")) {
						frm.set_value("case_report", "Interim")
					}
					else if (rs.includes("Dilemma")) {
						frm.set_value("case_report", "Dilemma")
					}
					else if (rs.includes("Negative")) {
						frm.set_value("case_report", "Negative")
					}
					else if (rs.every(e => e == "Positive")) {
						frm.set_value("case_report", "Positive")
					}

				}

			})
			// }
		}

	},
	make_dashboard: function (frm) {
		// var entry_checks = [];
		var verify_checks = [];
		if (frm.doc.check_package) {
			frappe.call({
				method: "checkpro.checkpro.doctype.case.case.check_status",
				async: false,
				args: {
					"name": frm.doc.name,
					"check_package": frm.doc.check_package
				},
				callback: function (r) {
					if (!r.exc && r.message) {
						$.each(r.message, function (i, d) {
							verify_checks.push([d.checks,d.check_id])
							// console.log(verify_checks)
						})
					}
				}

			});

			let section = frm.dashboard.add_section(
				frappe.render_template('case_dashboard', {
					verify_data: verify_checks
					
				})
				
			);
			
			
			

			section.on('click', '.check-link', function () {
				let doctype = $(this).attr('doctype');
				let check_id = $(this).attr('check_id');
				window.open(frappe.urllib.get_full_url("/desk#Form/"+doctype+"/"+check_id))
				// frappe.set_route('Form', doctype,check_id);
			});
			frm.dashboard.show();
		}
	},

});
		// if (frm.doc.check_package) {
		// 	frappe.call({
		// 		method: "checkpro.checkpro.doctype.case.case.get_checks",
		// 		async: false,
		// 		args: {
		// 			check_package: frm.doc.check_package,
		// 		},
		// 		callback: function (r) {
		// 			if (!r.exc && r.message) {
		// 				$.each(r.message, function (i, d) {
		// 					// entry_checks.push(d.checks)
		// 					verify_checks.push(d.check_name)
		// 				})
		// 			}
		// 		}

		// 	});

		// 	let section = frm.dashboard.add_section(
		// 		frappe.render_template('case_dashboard', {
		// 			// entry_data : entry_checks,
		// 			verify_data: verify_checks
		// 		})

		// 	);

		// 	section.on('click', '.check-link', function () {
		// 		let doctype = $(this).attr('data-type');
		// 		frappe.set_route('List', doctype, { 'case_id': frm.doc.name });
		// 	});

		

let calculate_age = function (birth) {
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years = age.getFullYear() - 1970;
	return years
};
// frappe.ui.form.on('Checkwise Report', {
// 	open(frm,cdt,cdn) {
// 		var child =locals[cdt][cdn]
// 		window.open(frappe.urllib.get_full_url("/desk#Form/"+child.checks+"/"+child.check_id))

// 	}
// })