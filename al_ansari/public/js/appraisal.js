frappe.ui.form.on('Appraisal', { 

})

frappe.ui.form.on('Appraisal Goal', {
	self_rating: function(frm,cdt,cdn) {
		var row = locals[cdt][cdn]
		if(row.self_rating > 5) {
			frappe.msgprint("Self Rating must be less than or equal to 5")
			row.self_rating = 0
		} else {
			row.score = row.self_rating
			row.score_earned = row.score * flt(row.per_weightage/100)
		}
		frm.refresh_field('goals')
	} 
})