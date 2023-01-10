frappe.ui.form.on('Salary Slip', { 
	refresh: function(frm) {
		frm.fields_dict.earnings.grid.grid_buttons.addClass('hidden');
		frm.fields_dict.deductions.grid.grid_buttons.addClass('hidden');
	},
	earnings_on_form_rendered:function(frm, cdt, cdn){
		frm.fields_dict["earnings"].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict["earnings"].grid.wrapper.find('.grid-duplicate-row').hide();
		frm.fields_dict["earnings"].grid.wrapper.find('.grid-move-row').hide();
		frm.fields_dict["earnings"].grid.wrapper.find('.grid-append-row').hide();
		frm.fields_dict["earnings"].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict["earnings"].grid.wrapper.find('.grid-insert-row').hide();
	},
	deductions_on_form_rendered:function(frm, cdt, cdn){
		frm.fields_dict["deductions"].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict["deductions"].grid.wrapper.find('.grid-duplicate-row').hide();
		frm.fields_dict["deductions"].grid.wrapper.find('.grid-move-row').hide();
		frm.fields_dict["deductions"].grid.wrapper.find('.grid-append-row').hide();
		frm.fields_dict["deductions"].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict["deductions"].grid.wrapper.find('.grid-insert-row').hide();
	}
})

