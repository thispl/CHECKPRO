// Copyright (c) 2023, saru and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
	download: function (frm) {
		if (frm.doc.report == 'Batch') {
			console.log("HI")
			var path = "checkpro.checkpro.doctype.report_dashboard.batch1.download"
		}
		if (frm.doc.report == 'Checks Status Report') {
			console.log("HI")
			var path = "checkpro.checkpro.doctype.report_dashboard.check_status.download"
		}
		if(frm.doc.report=="DPR and DSR Automated Report"){
            frappe.call({
                method: "checkpro.checkpro.doctype.report_dashboard.dpr_dsr_report.download_excel",
				args: {
                    date:frm.doc.production_date,
                    
                },
                freeze:true,
                freeze_message:"Processing......",
                callback: function (r) {
                    if (r.message) {
                        let blob = new Blob([new Uint8Array(r.message.content)], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
                        let link = document.createElement("a");
                        link.href = window.URL.createObjectURL(blob);
                        link.download = r.message.filename;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }
                }
            });
        }
		if(frm.doc.report=="DSR Automated Report"){
            frappe.call({
                method: "checkpro.checkpro.doctype.report_dashboard.dsr_report.download_excel",
				args: {
                    date:frm.doc.production_date,
                    
                },
                freeze:true,
                freeze_message:"Processing......",
                callback: function (r) {
                    if (r.message) {
                        let blob = new Blob([new Uint8Array(r.message.content)], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
                        let link = document.createElement("a");
                        link.href = window.URL.createObjectURL(blob);
                        link.download = r.message.filename;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }
                }
            });
        }
	
		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				
			});
		}
	}
});
