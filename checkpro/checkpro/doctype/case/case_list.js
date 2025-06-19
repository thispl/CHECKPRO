frappe.listview_settings["Case"] = {
    // get_indicator: function (doc) {
	// 	if (doc.custom_tat_status=='Regular') {
	// 		return [__(doc.custom_tat_status), "dark grey", "custom_tat_status,=," + doc.custom_tat_status];
	// 	} else if (doc.custom_tat_status=='Critical') {
	// 		return [__(doc.custom_tat_status), "orange", "custom_tat_status,=," + doc.custom_tat_status];
	// 	} else if (doc.custom_tat_status == "Most Critical") {
	// 		return [__(doc.custom_tat_status), "red", "custom_tat_status,=," + doc.custom_tat_status];
	// 	}
	// },
    onload: function(listview) {
		listview.page.add_action_item(__("Assign Allocated TO"), () => {
            let d = new frappe.ui.Dialog({
                title: 'Entry Allocated To',
                fields: [
                    {
                        label: 'Entry Allocated To',
                        fieldname: 'allocated_to',
                        fieldtype: 'Link',
                        options:'User',
                        reqd: 1,
                    },
                    {
                        label: 'Entry Allocated Date',
                        fieldname: 'allocated_date',
                        fieldtype: 'Date',
                        reqd: 1,
                    },
                ],
                primary_action_label: 'Save',
                primary_action(values) {
                    let checked_items = listview.get_checked_items();
                    const doc_name = [];
                    checked_items.forEach((Item) => {
                        doc_name.push(Item.name);
                    });
                    // console.log(doc_name)
                    // console.log(values.allocated_to)
                    // console.log(values.allocated_date)
                    frappe.call({
                        method: 'checkpro.custom.update_entry_allocated_to',
                        args: {
                            'case_id': doc_name,
                            'allocated_to': values.allocated_to,
                            'allocated_date':values.allocated_date
                        },
                        freeze: true,
                        callback: function (r) {
                            // if (!r.exc) {
                                frappe.msgprint(__('Entry Allocated to and Entry Allocated Date has been updated successfully.'));
                                d.hide();
                                listview.refresh();
                            // }
                        }
                    });
                }
            });
            d.show();
        })
        
    listview.page.add_action_item(__("Report Submitted"), () => {
            let d = new frappe.ui.Dialog({
                title: 'Report Submitted',
                fields: [
                    {
                        label: 'Mode of Submission',
                        fieldname: 'mode_of_submission',
                        fieldtype: 'Select',
                        options: ['Mail','Client Cloud','TEAMPRO Cloud','Public Cloud','Physical'],
                        reqd: 1,
                    },
                    {
                        label: 'Proof of Submission',
                        fieldname: 'proof_of_submission',
                        fieldtype: 'Attach',
                        reqd: 1,
                    },
                ],
                primary_action_label: 'Save',
                primary_action(values) {
                    let checked_items = listview.get_checked_items();
                    const doc_name = [];
                    checked_items.forEach((Item) => {
                        doc_name.push(Item.name);
                    });
                    console.log(typeof (doc_name))
                    frappe.call({
                        method: 'checkpro.custom.case_report_submitted',
                        args: {
                            'case_id': doc_name,
                            'mode_of_submission': values.mode_of_submission,
                            'proof_of_submission':values.proof_of_submission
                        },
                        freeze: true,
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint(__('Report Submitted successfully and Case Status has been changed to "To be Billed".'));
                                d.hide();
                                listview.refresh();
                            }
                        }
                    });
                }
            });
            d.show();
        })
    
    listview.page.add_action_item(__("Create SO"), ()=>{
        let checked_items = listview.get_checked_items();
        const doc_name = [];
        checked_items.forEach((Item)=> {
            doc_name.push(Item.name);
        });
        frappe.call({
            method:'checkpro.custom.create_so_case',
            args:{
                'case_id':doc_name  
                
            },
            // callback(r){
            //     if(r.message){
            //         frappe.msgprint("Sales Order Created"+" "+"-<b> "+ r.message+"</b>");
            //     }
            // }
        });
    });
}
}