// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Batch", {
	after_save:function(frm){
		// frm.doc.table_visible=1
		frappe.call({
			"method": "checkpro.checkpro.doctype.batch.batch.get_cases",
			args: {
				"batch":frm.doc.name,
				"no_of_case":frm.doc.no_of_cases,
				"expected_start_date":frm.doc.expected_start_date
			},
			callback: function (r) {
				if (!r.exc && r.message) {
					console.log(r.message)
				}
			}
			
	})
},
	refresh: (frm) => {
		if (!frm.is_new()) {
			frm.trigger('make_dashboard');
		}
	},
	customer: function (frm) {
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Check Package",
				"customer": frm.doc.customer,
				// "fields": ["name"]
			},
			callback: function (r) {
				$.each(r.message, function (i, d) {
					frm.set_query("check_package", function () {
						return {
							"filters": {
								"customer": frm.doc.customer
							}
						};
					});

				})


			}
		})
	},
	make_dashboard: function (frm) {
		var checks = [];
		if (frm.doc.check_package) {
			frappe.call({
				method: "checkpro.checkpro.doctype.batch.batch.get_checks",
				async: false,
				args: {
					check_package: frm.doc.check_package,
				},
				callback: function (r) {
					if (!r.exc && r.message) {
						$.each(r.message, function (i, d) {
							checks.push([d.check_name,d.units])
							// console.log(checks)
						})
					}
				}

			});
			
			let section = frm.dashboard.add_section(

				frappe.render_template('batch_dashboard', {
					data: [checks,frm.doc.no_of_cases]
					
				})
			);


			// section.on('click', '.check-link', function () {
			// 	let doctype = $(this).attr('data-type');
			// 	console.log(doctype)
			// 	frappe.set_route('List', doctype, { 'batch': frm.doc.name });

			// });
			section.on('click', '.case-link', function () {
				let doctype = $(this).attr('data-type');
				frappe.set_route('List', doctype, { 'batch': frm.doc.name});
				// // console.log(doctype)
				// // let cases = $(this).attr(frm.doc.no_of_cases);
				// // console.log(cases)
				// var nc =frm.doc.no_of_cases
				// var units;
				// // console.log(nc)
				
					
			});

			frm.dashboard.show();
		}
	},
	onload: function (frm) {
		if (frm.doc.check_package) {
			// if((frm.doc.checkwise_report).length==0){
			frappe.call({
				"method": "checkpro.checkpro.doctype.batch.batch.check_status",
				args: {
					"name": frm.doc.name,
					"check_package": frm.doc.check_package
				},
				callback: function (r) {
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
					})
				}
			})
		}
	},
	check_package(frm){
		frappe.call({
			"method":"checkpro.checkpro.doctype.batch.batch.get_check_list",
			args: {
				"check_package": frm.doc.check_package,
				},
			callback: function (r) {
				frm.clear_table("check_list");
				$.each(r.message, function (i, d) {
					var row = frappe.model.add_child(frm.doc, "List of checks", "check_list")
					row.checks = d.check_name
					row.units = d.units
				})
				refresh_field("check_list")
			}
		})
		frappe.call({
			"method": "checkpro.checkpro.doctype.batch.batch.get_end_date",
			args: {
				"name": frm.doc.name,
				"check_package": frm.doc.check_package,
				"expected_start_date":frm.doc.expected_start_date
				},
			callback: function (r) {
				console.log(r.message)
				frm.set_value("expected_end_date",r.message)
			}
			
	})
	}
	// check_package: function (frm) {
	// 	frappe.call({
	// 		"method": "frappe.client.get",
	// 		args: {
	// 			"doctype": "Check Package",
	// 			"name": frm.doc.check_package

	// 		},
	// 		callback: function (r) {

	// 			$.each(r.message.checks_list, function (i, d) {
	// 				var row = frappe.model.add_child(frm.doc,"Checks","check_batch")
	// 				row.checks = d.checks
	// 				row.units = d.units
	// 				row.ca_tat = d.ca_tat
	// 				row.ce_tat = d.ce_tat
	// 				row.pricing_model = d.pricing_model
	// 				row.check_price = d.check_price
	// 				row.check_selling_price = d.check_selling_price
	// 				row.tcsp = d.tcsp


	// 			})
	// 			refresh_field("check_batch")

	// 		}
	// 	})

	// }


});