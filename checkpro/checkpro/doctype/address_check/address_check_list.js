frappe.listview_settings["Address Check"] = {
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
        listview.page.add_action_item(__("Next Action"), () => {
            let d = new frappe.ui.Dialog({
                title: 'Next Action',
                fields: [
                    {
                        label: 'Allocated To',
                        fieldname: 'allocated_to',
                        fieldtype: 'Link',
                        options: 'User',
                        reqd: 1,
                    },
                    {
                        label: 'Allocate to Supplier',
                        fieldname: 'allocate_to_supplier',
                        fieldtype: 'Check',
                    },
                    {
                        label: 'Supplier',
                        fieldname: 'supplier',
                        fieldtype: 'Link',
                        options: 'Supplier',
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
                        method: 'checkpro.custom.update_next_action_addrs',
                        args: {
                            'check_id': JSON.stringify(doc_name),
                            'allocated_to': values.allocated_to,
                            'allocate_to_supplier':values.allocate_to_supplier,
                            'supplier':values.supplier
                        },
                        freeze: true,
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint(__('Next Action updated successfully.'));
                                d.hide();
                                listview.refresh();
                            }
                        }
                    });
                }
            });
            d.show();
        });
    }
};
