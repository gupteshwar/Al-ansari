frappe.ui.form.on('Job Opening', { 
	designation: function(frm) {

		if(frm.doc.designation && frm.doc.department) {
			console.log("1")
			frm.set_value("job_title",frm.doc.designation +" - "+frm.doc.department)
		}
	},
	department: function(frm) {
		if(frm.doc.designation && frm.doc.department) {
			console.log("111")
			frm.set_value("job_title",frm.doc.designation + " - " + frm.doc.department)
		}
	}
})