frappe.listview_settings["Social Media"] = {
    onload: function(listview) {
        // frappe.call({
        //     method:"teampro.custom.get_workflow_state",
        //     args:{
        //         "doctype":"Social Media",
        //     },
        //     callback(r){
        //         console.log(r.message)
        //         if(r.message){
        //     // 		$.each(r.message,function(i,j){
        //     // 			list.push(j.item_code)
        //     // 		})
        //     // 		console.log(list)
        //             frm.set_query("workflow_state", function() {
        //                 return{
        //                     filters: {
        //                         "name": ["in", r.message],
        //                     }
        //                 }
        //             });
        //         }
        //     }
        // })
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
                        method: 'checkpro.custom.update_next_action_sm',
                        args: {
                            'check_id': doc_name,
                            'allocated_to': values.allocated_to
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
