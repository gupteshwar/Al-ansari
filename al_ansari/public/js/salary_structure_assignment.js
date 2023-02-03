frappe.ui.form.on('Salary Structure Assignment', { 
	base: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	hra: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	transport: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	medical: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	food: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	others: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	living: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	},
	validate: function(frm) {
		frm.set_value('total_monthly_salary',calculate_total_monthly_salary(frm))
	}
})

function calculate_total_monthly_salary(frm) {

	var total_monthly_salary =  frm.doc.base + 
								frm.doc.hra +
								frm.doc.transport +
								frm.doc.medical +
								frm.doc.food +
								frm.doc.others +
								frm.doc.living					
	return total_monthly_salary
}