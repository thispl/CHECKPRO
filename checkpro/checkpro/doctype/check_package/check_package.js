// Copyright (c) 2020, suganya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Check Package', {
    pricing_model:function(frm, cdt, cdn){
        if(frm.doc.pricing_model=="Lumpsum"){
            var df = frappe.meta.get_docfield("Checks List","check_sp", cur_frm.doc.name);
            df.read_only = 1;
        }
    }
    //  
    //         console.log("hi")
    //         frm.fields_dict["checks_list"].grid.set_column_disp("check_sp", false);
     
    //         // hide_field(['Check SP']);
    //         // var df = frappe.meta.get_docfield("Checks List", fieldname , cur_frm.doc.name);
    //         // df.hidden = 1;
    //  
    
// 	calculate_sub3: function (frm) {
// 		var r10 = frm.doc.checks_list
// 		var a = 0
// 		$.each(frm.doc.checks_list, function (i, d) {
// 			if (d.tcsp) {
// 				a += d.tcsp
// 			}

// 		})
// 		frm.set_value("gsp", a)

// 	},
// 	onload: function (frm) {
// 		frappe.call({
// 			"method": "frappe.client.get_list",
// 			args: {
// 				"doctype": "Checks",
// 				"fields": ["check_name", "ce_tat", "check_price"]

// 			},
// 			callback: function (r) {
// 				// if(frm.doc.description!=1){
//                 $.each(r.message, function (i, d) {
//                     var row = frappe.model.add_child(frm.doc,"Checks List","checks_list")
//                     row.checks = d.check_name
//                     row.ce_tat = d.ce_tat
//                     row.check_price = d.check_price


//                 })
// 				// }
// 				// frm.set_value("description",1)
// 				refresh_field("checks_list")
// 			}
// 		})
// 	},
// // 	pricing_model:function(frm){
// // 		if(frm.doc.pricing_model=="Fixed"){
// // 			$.each(frm.doc.checks_list, function (i, d) {
// // 				eval:parent.fieldname
// // 			})
// // 		}

// // 	}


// // });

// frappe.ui.form.on('Checks List', {
// 	check_selling_price: function (frm, cdt, cdn) {
// 		var child = locals[cdt][cdn]
// 		var total = child.units * child.check_selling_price
// 		frappe.model.set_value(child.doctype, child.name, "tcsp", child.units * child.check_selling_price)

// 		frm.refresh_field("checks_list")
// 		frm.trigger("calculate_sub3")

// 	},
// 	checks: function (frm, cdt, cdn) {
// 		var child = locals[cdt][cdn]
// 		frappe.call({
// 			"method": "frappe.client.get",
// 			args: {
// 				"doctype": "Checks",
// 				"name": child.checks

// 			},
// 			callback: function (r) {
// 				// console.log(r.message.check_variables)
// 				// $.each(r.message.check_variables, function (i, d) {
// 				// 	console.log(d.variable)
// 				// 	wrapper = frm.fields_dict[child.cv_html].grid.grid_rows_by_docname[cdn].fields_dict[child.cv_html].wrapper;
// 				// 	$("<div>Loading...</div>").appendTo(wrapper);


// 				// 	// let e = new frappe.ui.Dialog({
// 				// 	// 	title: 'Check Variables',
// 				// 	// 	fields: [
// 				// 	// 		{
// 				// 	// 			label: d.variable,
// 				// 	// 			fieldname: 'first_name',
// 				// 	// 			fieldtype: 'Check'
// 				// 	// 		},

// 				// 	// 	],
// 				// 	// 	primary_action_label: 'Submit',
// 				// 	// 	primary_action(values) {
// 				// 	// 		console.log(values);

// 				// 	// 	}
// 				// 	// });

// 				// 	// e.show();
// 				// })

// 			}
// 		})


// 	}
})
// frappe.ui.form.on("Checks List", "checks_list", function(frm) {
//     console.log("hi")
//     if ('grid' in cur_frm.fields_dict.checks_list) {
//         var grid =  cur_frm.fields_dict.checks_list.grid;         
//         var interval = setInterval(function () {
//             if ('cur_grid' in grid.frm) {
//                 if(cur_frm.doc.typ != "Check Based"){
//                     grid.frm.cur_grid.fields_dict.check_sp.$wrapper.hide();
//                 }else{
//                     grid.frm.cur_grid.fields_dict.check_sp.$wrapper.show();
//                 }
//                 clearInterval(interval)
//             };
//         })
//     };    
// })
