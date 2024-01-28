// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Batch", {
	validate(frm){
		if(frm.doc.__islocal){
		frappe.call({
			"method": "checkpro.checkpro.doctype.batch.batch.calculate_end_date",
			args: {
				"check_package": frm.doc.check_package,
				"posting_date":frm.doc.expected_start_date
				},
			callback: function (r) {
				frm.set_value("expected_end_date",r.message)
			}
			
		})
	}
	},
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.trigger('make_dashboard');
		}
		// frm.disable_save()
		$('*[data-fieldname="pending_for_billing"]').find('.grid-remove-all-rows').hide();  
		frm.fields_dict["pending_for_billing"].grid.add_custom_button(__('Create SO'),
		function () {
			frm.clear_table("pending_for_billing");
				$.each(frm.doc.pending_for_billing, function (i, d) {
					if(frm.doc.pending_for_billing && d.case_id && d.batch){
					if (d.__checked == 1) {
						frappe.call({
							method:'teampro.custom.create_so',
							args:{
								'doctype':"Pending for Billing",
								'case_id':d.case_id,
								'batch':d.batch
								
							},
							callback(r){
								if(r.message){
									frappe.msgprint("Sales Order Created"+" "+"-<b> "+ r.message+"</b>");
									frm.refresh_field('pending_for_billing')
									frm.get_field("pending_for_billing").grid.grid_rows[d.idx - 1].remove();
								}
							}
						})
					}
				frm.save()
				}
			
			})
		}).css({'color':'white','background-color':"#009E60","margin-left": "10px", "margin-right": "10px"});
	},
	after_save:function(frm){
		// frm.doc.table_visible=1
		frappe.call({
			"method": "checkpro.checkpro.doctype.batch.batch.get_cases",
			args: {
				"batch":frm.doc.name,
				"no_of_case":frm.doc.no_of_cases,
				"expected_start_date":frm.doc.expected_start_date,
				"check_package":frm.doc.check_package
				// "customer":frm.doc.customer,
				// "no_of_cases":frm.doc.no_of_cases,
				// "name":frm.doc.name,
				// "expected_start_date":frm.doc.expected_start_date,
				// "expected_end_date":frm.doc.expected_end_date,
				// "case":frm.doc.case,
				// "pending":frm.doc.pending,
				// "comp":frm.doc.comp,
				// "insuff":frm.doc.insuff,
				// "Project_name":frm.doc.project_name
				


			},
			callback: function (r) {
				if (!r.exc && r.message) {
					console.log(r)
				}
			}
	})
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
								"customer": frm.doc.customer ,
								"status" : "Active"
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
				method: "checkpro.checkpro.doctype.batch.batch.check_status",
				args: {
					"name": frm.doc.name,
					"check_package": frm.doc.check_package
				},
				callback: function (r) {
					var s = [];
					var es = [];
					var rs = [];
					frm.clear_table("checkwise_report");
					$.each(r.message, function (i, d) {
						frm.add_child('checkwise_report',{
							'checks' : d.checks,
							'unit' : d.unit,
							'check_status' : d.check_status,
							'verification_status' : d.verification_status,
							'report_status' : d.report_status,
							'check_id' : d.check_id
						})
						frm.refresh_field('checkwise_report')
					// 	// console.log(d)

						// var row = frappe.model.add_child(frm.doc, "Checkwise Report", "checkwise_report")
						// row.checks = d.checks
						// row.units = d.units
						// row.check_status = d.check_status
						// row.verification_status = d.c
						// row.report_status = d.report_status
						// row.check_id = d.check_id
						s.push(d.check_status)
						es.push(d.verification_status)
						rs.push(d.report_status)
					})
				}
			})
			frappe.call({
				"method": "checkpro.checkpro.doctype.batch.batch.case_status",
				args: {
					"name": frm.doc.name,
					"check_package": frm.doc.check_package
				},
				callback: function (r) {
					var s = [];
					var es = [];
					var bs = [];

					frm.clear_table("casewise_status")
					$.each(r.message, function (i, d) {
						var row = frappe.model.add_child(frm.doc, "Casewise Status", "casewise_status")
						row.case_status = d.case_status
						row.case_id = d.case_id

						s.push(d.case_status)
						es.push(d.tat_monitor)
						bs.push(d.billing_status)
						
					})
					frm.refresh_field("casewise_status")
					if (s.includes("Draft")) {
						frm.set_value("batch_status", "Open")
					}
					else if (s.includes("Entry-QC")) {
						frm.set_value("batch_status", "Open")
					}
					else if (s.includes("Execution")) {
						frm.set_value("batch_status", "Open")
					}
					else if (s.includes("Final-QC")) {
						frm.set_value("batch_status", "Open")
					}
					else if (es.includes("In TAT")) {
						frm.set_value("batch_status", "Open")
					}
					else if (s.includes("Draft with Insuff")) {
						frm.set_value("batch_status", "Open with Insuff")
					}
					else if (s.includes("Entry-QC with Insuff")) {
						frm.set_value("batch_status", "Open with Insuff")
					}
					else if (s.includes("Execution with Insuff")) {
						frm.set_value("batch_status", "Open with Insuff")
					}
					else if (s.includes("Final-QC with Insuff")) {
						frm.set_value("batch_status", "Open with Insuff")
					}
					else if (es.includes("In TAT")) {
						frm.set_value("batch_status", "Open with Insuff")
					}
					else if (s.includes("Draft")) {
						frm.set_value("batch_status", "Overdue")
					}
					else if (s.includes("Entry-QC")) {
						frm.set_value("batch_status", "Overdue")
					}
					else if (s.includes("Execution")) {
						frm.set_value("batch_status", "Overdue")
					}
					else if (s.includes("Final-QC")) {
						frm.set_value("batch_status", "Overdue")
					}
					else if (es.includes("Out TAT")) {
						frm.set_value("batch_status", "Overdue")
					}
					else if (s.includes("Draft with Insuff")) {
						frm.set_value("batch_status", "Overdue with Insuff")
					}
					else if (s.includes("Entry-QC with Insuff")) {
						frm.set_value("batch_status", "Overdue with Insuff")
					}
					else if (s.includes("Execution with Insuff")) {
						frm.set_value("batch_status", "Overdue with Insuff")
					}
					else if (s.includes("Final-QC with Insuff")) {
						frm.set_value("batch_status", "Overdue with Insuff")
					}
					else if (es.includes("Out TAT")) {
						frm.set_value("batch_status", "Overdue with Insuff")
					}
					else if (s.includes("Completed")) {
						frm.set_value("batch_status", "Complected")
					}
					else if (bs.includes("Billed")) {
						frm.set_value("batch_status", "Complected")
					}
					else if (s.includes("Completed with Insuff")) {
						frm.set_value("batch_status", "Completed with Insuff")
					}
					else if (bs.includes("Billed")) {
						frm.set_value("batch_status", "Completed with Insuff")
					}
					else if (bs.includes("Partially Billed")) {
						frm.set_value("batch_status", "Completed with Insuff")
					}
					
					
					
					// else if (s.every(e => e == "Pending for Execution")) {
					// 	frm.set_value("case_status", "Generate Report with Execution")
					// }
				
					
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
		
	},
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