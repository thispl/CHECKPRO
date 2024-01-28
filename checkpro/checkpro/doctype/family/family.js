// Copyright (c) 2023, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Family', {
	refresh(frm) {
		
	if (frm.doc.workflow_state=="Draft"){

		frm.add_custom_button(__("Entry Completed"), function () {
			// if(!frm.doc.entered_by){
			// 	frappe.throw("Entered By - Not Allocated")
			// }
			// else{
			frm.set_value("entered_by",frappe.session.user)
            frm.set_value("workflow_state","Entry Completed")
			frm.set_value("date_of_entry_completion",frappe.datetime.nowdate())
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
			// }
	    }, __("Check Status"));  
	}
	if (frm.doc.workflow_state=="Entry Completed"){
		frm.add_custom_button(__("Send Entry-QC"), function () {
			// if(!frm.doc.entered_by_qc){
			// 	frappe.throw("Entry QC Pending - Not Allocated")
			// }
			// else{
            frm.set_value("workflow_state","Entry QC Pending")
			frm.set_value("entry_completed_date",frappe.datetime.nowdate())
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
			// }
	    }, __("Check Status"));  
	}
	if (frm.doc.workflow_state=="Entry QC Pending"){
		frm.add_custom_button(__("Entry-QC Completed"), function () {
			frm.set_value("entered_by_qc",frappe.session.user)
            frm.set_value("workflow_state","Entry QC Completed")
			frm.set_value("date_of_qc_completion",frappe.datetime.nowdate())
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

	    }, __("Check Status"));  
	}
	if (frm.doc.workflow_state=="Entry QC Completed"){
		frm.add_custom_button(__("Send to Execution"), function () {
			// if(!frm.doc.execution_by){
			// 	frappe.throw("Execution Pending - Not Allocated")
			// }
			// else{
            frm.set_value("workflow_state","Execution Pending")
			frm.set_value("execution_allocation_date",frappe.datetime.nowdate())
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
			// }
	    }, __("Check Status"));
	}
	if (frm.doc.workflow_state=="Execution Pending"){
		frm.add_custom_button(__("Send to Execution Completed"), function () {
			frm.set_value("execution_by",frappe.session.user)
            frm.set_value("workflow_state","Execution Completed")
			frm.set_value("date_of_execution_completion",frappe.datetime.nowdate())
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
	    }, __("Check Status"));  
	}
	if (frm.doc.workflow_state=="Execution Completed"){
		frm.add_custom_button(__("Send to Final-QC"), function () {
			if(frm.doc.report_status=="YTS"||frm.doc.report_status=="Pending"){
				frappe.throw("Check Report should be Positive, Negative or Dilemma")
			}
			// else if(!frm.doc.final_qc_by){
			// 	frappe.throw("Final QC Pending - Not Allocated")
			// }
			else{
            frm.set_value("workflow_state","Final QC Pending")
			frm.set_value("execution_completed_date",frappe.datetime.nowdate())
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
	    }, __("Check Status"));  
	}
	if (frm.doc.workflow_state=="Final QC Pending"){
		frm.add_custom_button(__("Final-QC Completed"), function () {
			frm.set_value("final_qc_by",frappe.session.user)
            frm.set_value("workflow_state","Final QC Completed")
			frm.set_value("date_of_final_qc_completion",frappe.datetime.nowdate())
			frm.save()
	    }, __("Check Status"));  
	}
	if (frm.doc.workflow_state=="Final QC Completed"){
		frm.add_custom_button(__("Mark Report Completed"), function () {
			frappe.confirm(__("Are you sure you want to Mark Report Completed?"), function () {
            frm.set_value("workflow_state","Report Completed")
			frm.set_value("check_completion_date",frappe.datetime.nowdate())
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
	    }, __("Check Status")); 
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
						console.log(r.message)
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
	
	if(frm.doc.workflow_state=="Draft"||frm.doc.workflow_state=="Entry Completed"||frm.doc.workflow_state=="Entry QC Pending"||frm.doc.workflow_state=="Entry QC Completed"){
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
			console.log("jh")
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
	
	
	
	}, __("Check Status"));  
	}
	
	if(frm.doc.workflow_state=="Entry QC Pending"||frm.doc.workflow_state=="Execution Pending"||frm.doc.workflow_state=="Final QC Pending"){
	frm.add_custom_button(__("Report Insuff"), function () {
	frm.set_value('insuff', 1);
	frm.set_value("workflow_state","Insufficient Data")
		
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
		frm.save();
		d.hide();
		frm.set_value('insufficiency_date', values.insufficiency_date);
		frm.set_value('detailsof_insufficiency', values.detailsof_insufficiency);
		frm.set_value('insufficient_remarks', values.insufficient_remarks);
	}

});

	d.show();
}, __("Check Status"));  
}
if(frm.doc.workflow_state=="Insufficient Data"){
	frm.add_custom_button(__("Clear Insufficiency"), function () {
		frm.set_value('workflow_state', "Draft");
	    frm.set_value('insuff', 0);
            
        
		frm.set_value('insuff_cleared_on', frappe.datetime.nowdate());
		frm.set_value('insuff_closed', frappe.datetime.nowdate());
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
	}, __("Check Status"));
	
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
		console.log("jh")
		frappe.call({
			method:"teampro.custom.doc_mark",
			args:{
				'name':frm.doc.name,
				'date':values.drop_date,
				'remark':values.remarks3
			},
		})
		d.hide();
		
	},
});
d.show();
frm.set_value("drop_marked_by",frappe.session.user)
}, __("Check Status"));
}
});
