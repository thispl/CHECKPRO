// Copyright (c) 2023, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Family', {
	refresh(frm) {
		if(frappe.session.user=='sangeetha.s@groupteampro.com' || frappe.session.user=='chitra.g@groupteampro.com' ||frappe.session.user=='divya.p@groupteampro.com' ){
		frm.add_custom_button(__("Reject"), function () {
			let d = new frappe.ui.Dialog({
				title: 'Reason to Reject',
				fields: [
					{
						label: 'Reason for Reject',
						fieldname: 'rejected_reason',
						fieldtype: 'Small Text',
					},
					{
						label:'NC Class Proposed',
						fieldname:'nc_class_proposed',
						fieldtype:'Select',
						options:'\nMinor\nMajor\nCritical',
					}
				],
				primary_action_label: __('Save'),
				primary_action: () => {
					let values = d.get_values();
					frm.set_value("nc_class_proposed",values.nc_class_proposed)
					frm.set_value("rejected_reason",values.rejected_reason)
					// frm.set_df_property("nc_class_proposed", "read_only", 1)
					// frm.set_df_property("rejected_reason", "read_only", 1)
				d.hide();
				frm.save()
				frappe.call({
					method:"checkpro.custom.nc_for_check_reject",
					args:{
						name:frm.doctype,
						id:frm.doc.name,
						allocated:frm.doc.allocated_to,
						class_proposed:frm.doc.nc_class_proposed,
						reason:frm.doc.rejected_reason
					},
				callback(){
					}
				})
				frappe.call({
					method:"checkpro.custom.send_mail_nc_for_check_reject",
					args:{
						name:frm.doctype,
						id:frm.doc.name,
						allocated:frm.doc.allocated_to,
						class_proposed:frm.doc.nc_class_proposed,
						reason:frm.doc.rejected_reason
					},
				callback(){
					}
				})
				},
			});
			d.show();
		})
	}
		if (frm.doc.workflow_state=="Report Completed"){
			frm.fields.forEach(function(field) {
				frm.set_df_property(field.df.fieldname, "read_only", 1);
			});
			frappe.db.get_value("Batch",{'name':frm.doc.batch},['batch_manager'])
			.then(r => {
				if(frappe.session.user=='sangeetha.s@groupteampro.com' || frappe.session.user=='chitra.g@groupteampro.com' || frappe.session.user==r.message.batch_manager){
					if(frm.doc.custom_reopened==0){
						frm.add_custom_button(__("Re-Open"), function () {
							let d = new frappe.ui.Dialog({
								title: 'Reason to Reopen',
								fields: [
									{
										label: 'Reason for Reopen',
										fieldname: 'custom_reason_for_reopen',
										fieldtype: 'Small Text',
									},
								],
								primary_action_label: __('Save'),
								primary_action: () => {
									let values = d.get_values();
									
									frm.set_value("workflow_state","Execution Pending")
									frm.set_value("check_status","Execution Pending")
									frm.set_value('custom_reopened',1)
									frm.set_value("custom_reopen_date",frappe.datetime.nowdate())
									frm.set_value("custom_reason_for_reopen",values.custom_reason_for_reopen)
									frm.set_df_property("custom_reopen_date", "read_only", 1);
									frm.set_df_property("custom_reason_for_reopen", "read_only", 1);
								d.hide();
								frm.save()
								},
							});
							d.show();
							frm.fields.forEach(function(field) {
								frm.set_df_property(field.df.fieldname, "read_only", 0);
							});
					
						})
					}	
					if(frm.doc.custom_reopened==1){
						frm.add_custom_button(__("Submit"), function () {
							frm.set_value('custom_reopened',0)
							frm.fields.forEach(function(field) {
								frm.set_df_property(field.df.fieldname, "read_only", 1);
							});
						
						})
					}
					
	
				}
			})
		}
		if(frm.doc.workflow_state in ["Final QC Completed","Final QC Pending","Report Completed"]){
			if (!frappe.user.has_role("Report Manager")){
				frm.fields.forEach(function(field) {
					frm.set_df_property(field.df.fieldname, "read_only", 1);
					
				});
			}
		}
	if (frm.doc.workflow_state=="Draft"){

		frm.add_custom_button(__("Entry Completed"), function () {
			// if(!frm.doc.entered_by){
			// 	frappe.throw("Entered By - Not Allocated")
			// }
			// else{
			
			frm.set_value("entered_by",frappe.session.user)
            // frm.set_value("workflow_state","Entry Completed")
			frm.set_value("date_of_entry_completion",frappe.datetime.nowdate())
			frm.set_value("custom_date_of_entry_completion", frappe.datetime.now_datetime());
			frm.set_value("workflow_state","Entry QC Completed")
			frm.set_value('custom_allocation_date',frappe.datetime.nowdate());
			frm.set_value("entry_completed_date",frappe.datetime.nowdate())
			frm.set_value("date_of_qc_completion",frappe.datetime.nowdate())
			frm.set_value("custom_date_of_qc_completion", frappe.datetime.now_datetime());
			frm.set_value("custom_date_of_execution_initiated",frappe.datetime.nowdate())
			frm.set_value("entered_by_qc",frappe.session.user)
			frm.save()
			frappe.confirm(__("Are you sure you want to Move to Next State?"), function () {
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
		
		},
	function(){
		frm.set_value("entered_by",'')
		// frm.set_value("workflow_state","Entry Completed")
		frm.set_value("date_of_entry_completion",'')
		frm.set_value("custom_date_of_entry_completion", '');
		frm.set_value("workflow_state","Draft")
		frm.set_value("entry_completed_date",'')
		frm.set_value("date_of_qc_completion",'')
		frm.set_value("custom_date_of_qc_completion", '');
		frm.set_value('custom_allocation_date','');
		frm.set_value("custom_date_of_execution_initiated",'')
		frm.set_value("entered_by_qc",'')
		frm.save()
	})
    
	    }, __("Send To"));  
	}


	if (frm.doc.workflow_state=="Entry Completed"){
		frm.add_custom_button(__("Entry-QC"), function () {
			// if(!frm.doc.entered_by_qc){
			// 	frappe.throw("Entry QC Pending - Not Allocated")
			// }
			// else{
            frm.set_value("workflow_state","Entry QC Pending")
			frm.set_value("entry_completed_date",frappe.datetime.nowdate())
			frm.save()
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			
			// }
	    }, __("Send To"));  
	}
	if (frm.doc.workflow_state=="Entry QC Pending"){
		frm.add_custom_button(__("Entry-QC Completed"), function () {
			frm.set_value("entered_by_qc",frappe.session.user)
            frm.set_value("workflow_state","Entry QC Completed")
			// frm.set_df_property("given_by", "reqd", 1)
			// frm.set_df_property("given_by_status", "reqd", 1)
			// frm.set_df_property("given_by_designation", "reqd", 1)
			// frm.set_df_property("given_by_contact_no", "reqd", 1)
			frm.set_value("date_of_qc_completion",frappe.datetime.nowdate())
			frm.set_value("custom_date_of_qc_completion", frappe.datetime.now_datetime());
			frm.save()
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			frm.save()

	    }, __("Send To"));  
	}
	// if (frm.doc.workflow_state=="Entry QC Completed"){
	// 	frm.add_custom_button(__("Execution"), function () {
	// 		// if(!frm.doc.execution_by){
	// 		// 	frappe.throw("Execution Pending - Not Allocated")
	// 		// }
	// 		// else{
    //         frm.set_value("workflow_state","Execution Pending")
	// 		frm.set_value("execution_allocation_date",frappe.datetime.nowdate())
	// 		frm.save()
	// 		frappe.call({
	// 			method: "teampro.custom.update_case_status",
	// 			args: {
	// 					"case": frm.doc.case_id,
						
	// 				},
	// 			callback: function (r) {
	// 				console.log("Hi")
	// 			}
	// 		})
	// 		frm.save()
	// 		// }
	//     }, __("Send To"));
	// }
	if (frm.doc.workflow_state=="Entry QC Completed"){
		frm.add_custom_button(__("Execution Initiation"), function () {
            frm.set_value("workflow_state","Execution Initiated")
			// frm.set_value("custom_date_of_execution_initiated",frappe.datetime.nowdate())
			frm.set_value("execution_allocation_date",frappe.datetime.nowdate())
			frm.set_value("custom_execution_initiated_by",frappe.session.user)
			frm.save()
			frappe.confirm(__("Are you sure you want to Move to Next State?"), function () {
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			frm.save()
		},
	function(){
		frm.set_value("workflow_state","Entry QC Completed")
		frm.set_value("execution_allocation_date",'')
		// frm.set_value("custom_date_of_execution_initiated",'')
		frm.set_value("execution_by",'')
		// frm.set_df_property("given_by", "reqd", 1)
		// frm.set_df_property("given_by_status", "reqd", 1)
		// frm.set_df_property("given_by_designation", "reqd", 1)
		// frm.set_df_property("given_by_contact_no", "reqd", 1)
		frm.save()
	})
	    }, __("Send To"));
	}
	if (frm.doc.workflow_state=="Execution Initiated"){
		frm.add_custom_button(__("Execution Pending"), function () {
            frm.set_value("workflow_state","Execution Pending")
			frm.set_value("custom_date_of_initiation_completion",frappe.datetime.nowdate())
			// frm.set_value("execution_allocation_date",frappe.datetime.nowdate())
			frm.set_value("execution_by",frappe.session.user)
			frm.save()
			frappe.confirm(__("Are you sure you want to Move to Next State?"), function () {
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			frm.save()
		},
	function(){
		frm.set_value("workflow_state","Execution Initiated")
		frm.set_value("custom_date_of_initiation_completion",'')
		// frm.set_value("execution_allocation_date",'')
		frm.set_value("execution_by",'')
		frm.save()
	})
	    }, __("Send To"));
	}
	if (frm.doc.workflow_state=="Execution Pending"){
		frm.add_custom_button(__("Execution Completed"), function () {
			if(frm.doc.report_status=="YTS"||frm.doc.report_status=="Pending"){
				frappe.throw("Check Report should be Positive, Negative or Dilemma")
			}
			else{
			
			frm.set_value("execution_by",frappe.session.user)
            // frm.set_value("workflow_state","Execution Completed")
			frm.set_value("final_qc_by",frappe.session.user)
			frm.set_value("workflow_state","Report Completed")
			frm.set_value("date_of_execution_completion",frappe.datetime.nowdate())
			frm.set_value("execution_completed_date",frappe.datetime.nowdate())
			frm.set_value("date_of_final_qc_completion",frappe.datetime.nowdate())
			frm.set_value("check_completion_date",frappe.datetime.nowdate())
			// frm.set_value("date_of_execution_completion",frappe.datetime.nowdate())
			frm.save()
			frappe.confirm(__("Are you sure you want to Mark Report Completed?"), function () {
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
		},
	function(){
		frm.set_value("execution_by",'')
		// frm.set_value("workflow_state","Execution Completed")
		frm.set_value("final_qc_by",'')
		frm.set_value("workflow_state","Execution Pending")
		frm.set_value("date_of_execution_completion",'')
		frm.set_value("execution_completed_date",'')
		frm.set_value("date_of_final_qc_completion",'')
		frm.set_value("check_completion_date",'')
		// frm.set_value("date_of_execution_completion",frappe.datetime.nowdate())
		frm.save()
	})
	}
			frm.save()
	    }, __("Send To"));  
	}
	if (frm.doc.workflow_state=="Execution Completed"){
		frm.add_custom_button(__("Final-QC"), function () {
			if(frm.doc.report_status=="YTS"||frm.doc.report_status=="Pending"){
				frappe.throw("Check Report should be Positive, Negative or Dilemma")
			}
			// else if(!frm.doc.final_qc_by){
			// 	frappe.throw("Final QC Pending - Not Allocated")
			// }
			else{
            frm.set_value("workflow_state","Final QC Pending")
			frm.set_value("execution_completed_date",frappe.datetime.nowdate())
			frm.save()
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			frm.save()
			}
	    }, __("Send To"));  
	}
	if (frm.doc.workflow_state=="Final QC Pending"){
		frm.add_custom_button(__("Final-QC Completed"), function () {
			frm.set_value("final_qc_by",frappe.session.user)
            frm.set_value("workflow_state","Final QC Completed")
			frm.set_value("date_of_final_qc_completion",frappe.datetime.nowdate())
			frm.save()
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			frm.save()
	    }, __("Send To")
	); 
		 
	}
	if (frm.doc.workflow_state=="Final QC Completed"){
		frm.add_custom_button(__("Mark Report Completed"), function () {
			frappe.confirm(__("Are you sure you want to Mark Report Completed?"), function () {
            frm.set_value("workflow_state","Report Completed")
			frm.set_value("check_completion_date",frappe.datetime.nowdate())
			frm.save()
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
			frm.save()
			})
			frm.save();	
	    }, __("Send To")); 
	}
	if(frm.doc.check_creation_date && frm.doc.check_completion_date){
		frappe.call({
			method: "teampro.custom.holidays",
			args: {
					"date1": frm.doc.check_creation_date,
					"date2":frm.doc.check_completion_date
				},
			callback: function (r) {
				 
				frm.set_value("holidays",r.message)
				frappe.call({
					method: "teampro.custom.update_actual_tat",
					args: {
							"date1": frm.doc.check_creation_date,
							"date2":frm.doc.check_completion_date,
							"date3":frm.doc.insufficiency_days,
							"date4":frm.doc.holidays,
							"pac_tat":frm.doc.package_tat
							
						},
					callback: function (r) {
						
						 if(r.message){
							 frm.set_value("actual_tat",r.message[0])
							 frm.set_value("tat_variation",r.message[1])
							 frm.set_value("tat_monitor",r.message[2])
							 
						 }
					}
				})
			}
		})
	}
	
	if(frm.doc.workflow_state=="Draft"||frm.doc.workflow_state=="Entry Completed"||frm.doc.workflow_state=="Entry QC Pending"||frm.doc.workflow_state=="Entry QC Completed"||frm.doc.workflow_state=="Execution Initiated"||frm.doc.workflow_state=="Execution Pending"){
		frm.add_custom_button(__("Not Applicable"), function () {
		let d = new frappe.ui.Dialog({
		title: 'feedback form',
		fields: [
			{
				label: 'Mark (NA) On',
				fieldname: 'mark_na_on',
				fieldtype: 'Date',
				default: frappe.datetime.nowdate(),
			},
			{
				label: 'Not Applicable Remarks',
				fieldname: 'remarks2',
				fieldtype: 'Small Text',
				reqd: 1,
			},
			
		],
		primary_action_label: __('Save'),
		primary_action: () => {
			let values = d.get_values();
			
			frappe.call({
				method:"teampro.custom.report_check",
				args:{
					'name':frm.doc.name,
					'date':values.mark_na_on,
					'remark':values.remarks2
				},
			})
			d.hide();
			frm.save()
			
		},
	});
	d.show();
	
	
	
	}, __("Send To"));  
	}
	
	if(frm.doc.workflow_state=="Draft"||frm.doc.workflow_state=="Execution Pending"||frm.doc.workflow_state=="Final QC Pending"){
	frm.add_custom_button(__("Report Insuff"), function () {
	frm.set_value('insuff', 1);
	frm.set_value("workflow_state","Insufficient Data")
	frm.set_value("custom_insufficiency_reported_by",frappe.session.user)
		
	let d = new frappe.ui.Dialog({
	title: 'feedback form',
	fields: [
		{
			label: 'Insufficiency Date',
			fieldname: 'insufficiency_date',
			fieldtype: 'Date',
			default: frappe.datetime.nowdate(),
		},
		{
			label: 'Details Of Insufficiency',
			fieldname: 'detailsof_insufficiency',
			fieldtype: 'Select',
			options: 'Entry\nExecution',
			reqd: 1,
		},
		{
			label: 'Insufficient Remarks',
			fieldname: 'insufficient_remarks',
			fieldtype: 'Small Text',
			reqd: 1,
		},
		
	],
	primary_action_label: 'Save',
	primary_action(values) {
		d.hide();
		frm.set_value('insufficiency_date', values.insufficiency_date);
		frm.set_value('detailsof_insufficiency', values.detailsof_insufficiency);
		frm.set_value('insufficient_remarks', values.insufficient_remarks);
		frm.save();
				frappe.confirm(__("Are you sure you want to Mark Report insuff?"), function () {
				frappe.call({
					method: "teampro.custom.update_case_status",
					args: {
							"case": frm.doc.case_id,
							
						},
					callback: function (r) {
						console.log("Hi")
					}
				})
			},
		function(){
			frm.set_value('insuff', 0);
			if(values.detailsof_insufficiency=="Entry"){
				frm.set_value("workflow_state","Draft")
				}
			else{
				frm.set_value("workflow_state","Execution Pending")
			}
			frm.set_value("custom_insufficiency_reported_by",'')
			frm.set_value('insufficiency_date', '');
			frm.set_value('detailsof_insufficiency', '');
			frm.set_value('insufficient_remarks', '');
			frm.save();
		})
	}

});

	d.show();
}, __("Send To"));  
}
if(frm.doc.workflow_state=="Insufficient Data"){
	frm.add_custom_button(__("Clear Insufficiency"), function () {
		frappe.call({
			method: "checkpro.checkpro.doctype.family.family.family_check_mail",
			args: {
				id: frm.doc.name
			},
		});
		frm.set_value('workflow_state', "Draft");
	    frm.set_value('insuff', 0);
		if (frm.doc.custom_insufficiency_reported_by){
			frm.set_value('allocated_to',frm.doc.custom_insufficiency_reported_by)
			} 
            
        
		frm.set_value('insuff_cleared_on', frappe.datetime.nowdate());
		frm.set_value('insuff_closed', frappe.datetime.nowdate());
		frm.set_value('custom_allocation_date', frappe.datetime.nowdate());
		frappe.call({
			method: "teampro.custom.update_insuff_days",
			args: {
					"date1": frm.doc.insufficiency_date,
					"date2":frm.doc.insuff_cleared_on
				},
			callback: function (r) {
				 if(r.message){
					 frm.set_value("insufficiency_days",r.message)
				 }
			}
		})
		frm.save()
		frappe.confirm(__("Are you sure you want to Clear Insuff?"), function () {
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
		},
	function(){
		frm.set_value('workflow_state', "Insufficient Data");
	    frm.set_value('insuff', 1);
		frm.set_value('insuff_cleared_on', '');
		frm.set_value('insuff_closed', '');
		frm.set_value('custom_allocation_date','');
		frm.save()
	})
	}, __("Send To"));
	
}
frm.add_custom_button(__("Drop"), function () {
		
	let d = new frappe.ui.Dialog({
		title: 'feedback form',
		fields: [
			{
				label: 'Drop Date',
				fieldname: 'drop_date',
				fieldtype: 'Date',
				default: frappe.datetime.nowdate(),
			},
			{
				label: 'Drop Remarks',
				fieldname: 'remarks3',
				fieldtype: 'Small Text',
				reqd: 1,
			},
			
		],
	primary_action_label: __('Drop'),
	primary_action: () => {
		let values = d.get_values();
		
		frappe.call({
			method:"teampro.custom.doc_mark",
			args:{
				'name':frm.doc.name,
				'date':values.drop_date,
				'remark':values.remarks3
			},
		})
		d.hide();
		frm.save()
		frappe.confirm(__("Are you sure you want to Drop Check?"), function () {
			frappe.call({
				method: "teampro.custom.update_case_status",
				args: {
						"case": frm.doc.case_id,
						
					},
				callback: function (r) {
					console.log("Hi")
				}
			})
		})
	},
});
d.show();
frm.set_value("drop_marked_by",frappe.session.user)
}, __("Send To"));
}
});
