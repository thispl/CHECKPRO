// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Case', {
	validate:function(frm){
		frm.trigger("date_of_birth");
	},
	date_of_birth(frm) {
		var age = calculate_age(frm.doc.date_of_birth)
		if (age < 18) {
			frappe.msgprint({
				title: __('Notification'),
				indicator: 'red',
				message: __("Age cannot be lesser than 18")
			});
			validated=false;
		}
	},
	
	
	refresh: function (frm) {
		if (frm.doc.ca_status == "Completed") {

			frm.add_custom_button(__("Verify Check Report"), function () {
				var f_name = frm.doc.name
				var print_format = "Verify Check Report";
				window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
					+ "doctype=" + encodeURIComponent("Case")
					+ "&name=" + encodeURIComponent(f_name)
					+ "&trigger_print=1"
					+ "&format=" + print_format
					+ "&no_letterhead=0"
				));

			})
		}
		if (!frm.is_new()) {
			frm.trigger('make_dashboard');
		}
		// frappe.call({
		// 	"method": "frappe.client.get",
		// 	args: {
		// 		"doctype": "Case",
		// 		"name": frm.doc.name,
		// 	},
		// 	callback: function (r) {
		// 		$.each(r.message.checkwise_report, function (i, d) {
		// 			var list = [d.check_status]
		// 			// console.log(list)
		// 			if (list.includes("Negative")) {
		// 				frm.set_value("case_report", "Red")
		// 			}
		// 			else if (list.every(e => e == "Positive")) {
		// 				frm.set_value("case_report", "Green")
		// 			}
		// 			else if (list.includes("Amber")) {
		// 				frm.set_value("case_report", "Amber")
		// 			}
		// 		})
		// 	}
		// })


	},
	onload: function (frm) {
		if (frm.doc.check_package) {
			frappe.call({
				"method": "frappe.client.get",
				args: {
					"doctype": "Check Package",
					"name": frm.doc.check_package,
				},
				callback: function (r) {
					if (frm.doc.description != 1) {
						console.log(r.message.checks_list)
						$.each(r.message.checks_list, function (i, d) {
							var row = frappe.model.add_child(frm.doc, "Checkwise Report", "checkwise_report")
							row.checks = d.checks
							row.units = d.units
						})

					}
					frm.set_value("description", 1)
					refresh_field("checkwise_report")
				}
			})
		}

		// if (frm.doc.__islocal) {
		// 	frappe.call({
		// 		"method": "veripro.custom.case_count",
		// 		args: {
		// 			"batch": frm.doc.batch
		// 		}
		// 	})

		// }

		// frappe.call({
		// 	"method": "checkpro.checkpro.doctype.case.case.check_status",
		// 	args: {
		// 		name: frm.doc.name,
		// 		check_package: frm.doc.check_package
		// 	},
		// 	callback: function (r) {

		// 	}
		// })


	},
	make_dashboard: function (frm) {
		var entry_checks = [];
		var verify_checks = [];
		if (frm.doc.check_package) {
			frappe.call({
				method: "checkpro.checkpro.doctype.case.case.get_checks",
				async: false,
				args: {
					check_package: frm.doc.check_package,
				},
				callback: function (r) {
					if (!r.exc && r.message) {
						$.each(r.message, function (i, d) {
							entry_checks.push(d.checks)
							verify_checks.push("Verify "+ d.checks)
						})
					}
				}

			});

			let section = frm.dashboard.add_section(
				frappe.render_template('case_dashboard', {
					entry_data : entry_checks,
					verify_data : verify_checks
				})

			);

			section.on('click', '.check-link', function () {
				let doctype = $(this).attr('data-type');
				frappe.set_route('List', doctype,{ 'case_id': frm.doc.name });
			});

			frm.dashboard.show();
		}
	},

});

let calculate_age = function (birth) {
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years = age.getFullYear() - 1970;
	return years
};

