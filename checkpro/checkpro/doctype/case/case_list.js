frappe.listview_settings["Case"] = {
    onload: function(listview) {
		listview.page.add_action_item(__("Create SO"), ()=>{
            let checked_items = listview.get_checked_items();
			const doc_name = [];
			checked_items.forEach((Item)=> {
				doc_name.push(Item.name);
			});
			console.log(typeof(doc_name))
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
};