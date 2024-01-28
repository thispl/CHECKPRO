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
	
		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				
			});
		}
	}
});
