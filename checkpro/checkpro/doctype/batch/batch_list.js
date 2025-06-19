// frappe.listview_settings["Batch"] = {

//     get_indicator: function (doc) {
// 		if (doc.custom_tat_status=='Regular') {
// 			return [__(doc.custom_tat_status), "dark grey", "custom_tat_status,=," + doc.custom_tat_status];
// 		} else if (doc.custom_tat_status=='Critical') {
// 			return [__(doc.custom_tat_status), "orange", "custom_tat_status,=," + doc.custom_tat_status];
// 		} else if (doc.custom_tat_status == "Most Critical") {
// 			return [__(doc.custom_tat_status), "red", "custom_tat_status,=," + doc.custom_tat_status];
// 		}
// 	},
// };