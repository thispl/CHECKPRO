// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Case', {
	validate: function (frm) {
		frm.trigger("date_of_birth");
		// if ((frm.doc.contact).length < 10) {
		// 			frappe.throw("Contact No should be 10 digits")
		// 			frappe.validated = false;
		// 		}
	},
	before_submit: function (frm) {
		if (frm.doc.entry_status != "Completed" || frm.doc.ca_status != "Completed" || frm.doc.case_report != "Completed") {
			frappe.throw("Status is pending,Cannot Submit")
		}

	},
	// contact(frm) {
	// 	if ((frm.doc.contact).length < 10) {
	// 		frappe.throw("Contact No should be 10 digits")
	// 		frappe.validated = false;
	// 	}
	// },
	date_of_birth(frm) {
		var age = calculate_age(frm.doc.date_of_birth)
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
		if(frm.doc.case_status=="Case Report Completed"){
			frm.add_custom_button(__("Create SO"), function () {
				frappe.call({
					method:'checkpro.custom.create_so',
					args:{
						'case_id':frm.doc.name  
						
					},
				})
			})
		}
		if(!frm.doc.tat){
			refresh_field("Batch")
		}
		if(frm.doc.case_status=="Generate Report"){
			frm.add_custom_button(__("Case Report Completed"), function () {
				frm.set_value('billing_status', "To be Billed");
				frm.set_value("case_status","Case Report Completed")
				frm.set_value('case_completion_date', frappe.datetime.nowdate());
				frm.save()
			}, __("Case Completion"))
			frm.add_custom_button(__("Drop"), function () {
				frappe.call({
					method:"teampro.custom.drop_case",
					args: {
						"case_id":frm.doc.name
					},
				})
				// frm.set_value('billing_status', "To be Billed");
				frm.set_value("case_status","Drop")
				frm.set_value('dropped_date', frappe.datetime.nowdate());
				frm.save()
			}, __("Case Completion"))
			
		}
		if(frm.doc.case_status=="Case Report Completed"){
			frm.set_read_only();
			frm.set_intro(__("This is a root account and cannot be edited."));
		}
		if(frm.doc.date_of_initiating && frm.doc.case_completion_date){
			frappe.call({
				method: "teampro.custom.holidays",
				args: {
						"date1": frm.doc.date_of_initiating,
						"date2":frm.doc.case_completion_date
					},
				callback: function (r) {
					 //if(r.message){
						 frm.set_value("holidays",r.message)
						 frm.save()
						 frappe.call({
							method: "teampro.custom.tat_calculation",
							args: {
									"date1": frm.doc.date_of_initiating,
									"date2":frm.doc.case_completion_date,
									"date3":frm.doc.insufficiency_days,
									"date4":frm.doc.holidays,
									"pac_tat":frm.doc.package_tat
									
								},
							callback: function (r) {
								console.log(r.message)
								 if(r.message){
									 frm.set_value("actual_tat",r.message[0])
									 frm.set_value("tat_variation",r.message[1])
									 frm.set_value("tat_monitor",r.message[2])
									 
								 }
							}
						})
					 //}
				}
			})

		}
		
		
		// console.log(frm.doc.entry_status)
		if (frm.doc.entry_status != "Draft") {
		if (frm.doc.entry_status != "Pending") {
			frm.add_custom_button(__("Verify Check Report"), function () {
				var f_name = frm.doc.name
				var print_format = "Verify Check Report1";
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
		frm.add_custom_button(__("Drop"), function () {
		
			let d = new frappe.ui.Dialog({
				title: 'Reason of Drop',
				fields: [
					{
						label: 'Reason of Drop',
						fieldname: 'reason_of_drop',
						fieldtype: 'Small Text',
						reqd: 1,
					},					
				],
			primary_action_label: __('Drop'),
			primary_action: () => {
				let values = d.get_values();
				frappe.call({
					method:"teampro.custom.case_drop_status",
					args:{
						'name':frm.doc.name,
						'remark':values.reason_of_drop
					},
				})
				d.hide();
				frm.save()
			},
		});
		d.show();
		frm.set_value("drop_marked_by",frappe.session.user)
		})
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
					var s = [];
					var es = [];
					var rs = [];
					// console.log(r)

					frm.clear_table("checkwise_report")
					$.each(r.message, function (i, d) {
						// console.log(d)
						var row = frappe.model.add_child(frm.doc, "Checkwise Report", "checkwise_report")
						row.checks = d.checks
						row.unit = d.units
						row.check_status = d.check_status
						row.verification_status = d.verification_status
						row.report_status = d.report_status
						row.check_id = d.check_id

						s.push(d.check_status)
						// console.log(s)
						es.push(d.verification_status)
						rs.push(d.report_status)
						console.log(rs)
					})
					frm.refresh_field("checkwise_report")
					if (s.includes("Insufficient")) {
						frm.set_value("entry_status", "Insufficient")
					}
					else if (s.includes("YTS")) {
						frm.set_value("entry_status", "YTS")
					}
					
					else if (s.includes("Pending")) {
						frm.set_value("entry_status", "Pending")
					}
					else if (s.includes("Not Applicable")) {
						frm.set_value("entry_status", "Completed")
					}
					else if (es.includes("Not Applicable")) {
						frm.set_value("ca_status", "Completed")
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
					// else if (es.includes("YTS")) {
					// 	frm.set_value("ca_status", "YTS")
						
					// }

					
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
					// else if (rs.includes("YTS")) {
					// 	frm.set_value("case_report", "YTS")

					// }
					else if (rs.includes("Negative")) {
						frm.set_value("case_report", "Negative")
					}
					else if (rs.includes("Not Applicable")) {
						frm.set_value("case_report", "Positive")
					}
					
					else if (rs.includes("Interim")) {
						frm.set_value("case_report", "Interim")
					}
					// else if (s.includes("Not Applicable")) {
					// 	frm.set_value("case_report", "Not Applicable")
					// }
					else if (rs.includes("Dilemma")) {
						frm.set_value("case_report", "Dilemma")
					}
					
					else if (rs.every(e => e == "Positive")) {
						frm.set_value("case_report", "Positive")
					}

				}

			})
			frappe.call({
				"method": "checkpro.checkpro.doctype.case.case.case_status",
				args: {
					"name": frm.doc.name,
					"check_package": frm.doc.check_package
				},
				callback: function (r) {
					var s = [];
					var es = [];
					var rs = [];

					frm.clear_table("checkwise_status")
					$.each(r.message, function (i, d) {
						var row = frappe.model.add_child(frm.doc, "Checkwise Status", "checkwise_status")
						row.checks = d.checks
						row.checks_status = d.checks_status
						row.check_id = d.check_id
						row.check_report = d.check_report

						s.push(d.checks_status)
						s.push(d.check_report)
					})
					frm.refresh_field("checkwise_status")
				}
			})
			
					
			// 		if (s.includes("Insufficient Data")) {
			// 			frm.set_value("case_status", "Draft with Insuff")
			// 		}
			// 		else if (s.every(e => e == "Entry QC Pending")) {
			// 			frm.set_value("case_status", "Entry-QC")
			// 			frm.set_value("entry_completed_date", frappe.datetime.nowdate());
			// 		}
			// 		else if (s.includes("Insufficient Data")) {
			// 			frm.set_value("case_status", "Entry-QC with Insuff")
			// 		}
					
			// 		// else if (s.includes("Pending for Entry-QC")) {
			// 		// 	frm.set_value("case_status", "Entry-QC with Insuff")
			// 		// }
			// 		else if (s.every(e => e == "Execution Pending")) {
			// 			frm.set_value("case_status", "Execution")
			// 			frm.set_value("entry_completed_date", frappe.datetime.nowdate());

			// 		}
			// 		else if (s.includes("Insufficient Data")) {
			// 			frm.set_value("case_status", "Execution with Insuff")
			// 		}
			// 		else if (s.includes("Pending for Execution")) {	
			// 			frm.set_value("case_status", "Execution with Insuff")
			// 		}
			// 		else if (s.every(e => e == "Pending for Final-QC")) {
			// 			frm.set_value("case_status", "Final-QC")
			// 			frm.set_value("execution_completed_date", frappe.datetime.nowdate());
			// 		}
			// 		else if (s.includes("Insufficient Data")) {
			// 			frm.set_value("case_status", "Final-QC with Insuff")
			// 		}
					
			// 		else if (s.includes("Pending for Final-QC")) {
			// 			frm.set_value("case_status", "Final-QC with Insuff")
			// 		}
			// 		else if (s.every(e => e == "Draft")) {
			// 			frm.set_value("case_status", "Draft")	
			// 		}
			// 		else if (s.every(e => e == "Report Completed")) {
			// 			frm.set_value("case_status", "Generate Report")
						
			// 		}
			// 		else if (s.includes("Insufficient Data")) {
			// 			frm.set_value("case_status", "Generate Report with Insuff")
			// 		}
			// 		else if (s.includes("Report Completed")) {
			// 			frm.set_value("case_status", "Generate Report with Insuff")
			// 		}
			// 		// else if (s.includes("Draft")) {
			// 		// 	frm.set_value("case_status", "Report Completed")
			// 		// }
					
			// 		// else if (s.every(e => e == "Pending for Execution")) {
			// 		// 	frm.set_value("case_status", "Generate Report with Execution")
			// 		// }
				
					
			// 	}

			// })
			// }
		}
		

	},
	// onload: function(listview) {
	// 	listview.page.add_action_item(__("Create SO"), ()=>{
	// 		let checked_items = listview.get_checked_items();
	// 		const doc_name = [];
	// 		checked_items.forEach((Item)=> {
	// 			doc_name.push(Item.name);
	// 		});
	// 		console.log(typeof(doc_name))

	// 		frappe.call({
    //             method: "teampro.custom.create_so_case",
	// 			args:{
    //                 'name':doc_name
    //             }
    //         });
	// 	});
	// },
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
							var check_id = d.checks
							var checks = d.checks.replace(/\s+/g, '-').toLowerCase();
							verify_checks.push([checks,d.check_id])
							
							
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