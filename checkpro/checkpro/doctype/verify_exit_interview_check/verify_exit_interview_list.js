frappe.listview_settings['Verify Exit Interview Check'] = {

    onload: function (listview) {
        listview.page.add_action_item(__("Allocate Check"), function () {
            let d = new frappe.ui.Dialog({
                title: 'Check Allocation',
                fields: [
                    {
                        label: 'Check Eecutive',
                        fieldname: 'check_exec',
                        fieldtype: 'Link',
                        options: 'User'
                    },

                ],
                primary_action_label: 'Assign',
                primary_action(values) {
                    var method = "veripro.veripro.doctype.verify_exit_interview_check.verify_exit_interview_check.edu_check"
                    var doctype = listview.doctype
                    console.log(values.check_exec)

                    listview.call_for_selected_items(method, { 'exe': values.check_exec, 'doctype': listview.doctype });
                }
            });

            d.show();

        });

    },
};
