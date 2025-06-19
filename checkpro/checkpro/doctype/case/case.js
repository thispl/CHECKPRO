// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Case', {
    validate: function (frm) {
        frm.trigger("date_of_birth");
        if (!frm.is_new()) {
            frappe.call({
                method:'checkpro.checkpro.doctype.case.case.update_per_comp',
                args:{
                    'name':frm.doc.name
                    
                },
                callback(r){
                    if(r.message){
                        frm.set_value('custom_per_comp',r.message)
                    }
                }
                
            })
        }
    },
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
            frm.add_custom_button(__("Case Completed"), function () {
                frm.set_value('billing_status', "To be Billed");
                frm.set_value("case_status","Case Completed")
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
            $.each(frm.fields_dict, function(fieldname, field) {
                            frm.set_df_property(fieldname, 'read_only', 1);
                        });
            frm.set_intro(__("This is a root account and cannot be edited."));
        }
       
        if (frm.doc.case_status != "Draft") {
            if (frm.doc.case_status != 'Drop'){
            frm.add_custom_button(__("Verify Check Report - New"), function () {
                var f_name = frm.doc.name
                // var print_format = "Verify Check Report-New3";
                var print_format = "Case Report New";
                window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    + "doctype=" + encodeURIComponent("Case")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1"
                    + "&format=" + print_format
                    + "&no_letterhead=0"
                ));

            })
            frm.add_custom_button(__("Verify Check Report - Old"), function () {
                var f_name = frm.doc.name
                var print_format = "Verify Check Report - Old";
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
            if(frm.doc.case_name && frm.doc.case_gender){
                frm.trigger('make_dashboard');
            }
        }
       



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
        if (frm.doc.check_package && (frm.doc.case_status!='To be Billed' && frm.doc.case_status!='SO Created')) {
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

                    frm.clear_table("checkwise_report")
                    $.each(r.message, function (i, d) {
                        var row = frappe.model.add_child(frm.doc, "Checkwise Report", "checkwise_report")
                        row.checks = d.checks
                        row.unit = d.units
                        row.check_status = d.check_status
                        row.report_status = d.report_status
                        row.check_id = d.check_id

                        s.push(d.check_status)
                        rs.push(d.report_status)
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
                    else if (es.includes("Pending")) {
                        frm.set_value("ca_status", "Pending")
                    }
                    
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
                    else if (rs.includes("YTS")) {
                        frm.set_value("case_report", "Pending")

                    }
                    else if (rs.includes("Negative")) {
                        frm.set_value("case_report", "Negative")
                    }

                    else if (rs.includes("Interim")) {
                        frm.set_value("case_report", "Interim")
                    }

                    else if (rs.includes("Dilemma")) {
                        frm.set_value("case_report", "Dilemma")
                    }

                    else if (rs.includes("Not Applicable")) {
                        frm.set_value("case_report", "Positive")
                    }
                    
                    else if (rs.every(e => e == "Positive")) {
                        frm.set_value("case_report", "Positive")
                    }
                    else if (rs.every(e => e == "Drop")) {
                        frm.set_value("case_report", "Drop")
                    }
                    frm.save();
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
                        // rs.push(d.check_report)
                    })
                    frm.refresh_field("checkwise_status")
                    
                    // if (rs.includes("YTS")) {
                    //     frm.set_value("case_report", "Pending")

                    // }
                    // else if (rs.includes("Negative")) {
                    //     frm.set_value("case_report", "Negative")
                    // }

                    // else if (rs.includes("Interim")) {
                    //     frm.set_value("case_report", "Interim")
                    // }

                    // else if (rs.includes("Dilemma")) {
                    //     frm.set_value("case_report", "Dilemma")
                    // }

                    // else if (rs.includes("Not Applicable")) {
                    //     frm.set_value("case_report", "Positive")
                    // }
                    
                    // else if (rs.every(e => e == "Positive")) {
                    //     frm.set_value("case_report", "Positive")
                    // }
                    // else if (rs.every(e => e == "Drop")) {
                    //     frm.set_value("case_report", "Drop")
                    // }
                    // frm.save();
                }
            })
        }
        

    },
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
let calculate_age = function (birth) {
    let ageMS = Date.parse(Date()) - Date.parse(birth);
    let age = new Date();
    age.setTime(ageMS);
    let years = age.getFullYear() - 1970;
    return years
};
