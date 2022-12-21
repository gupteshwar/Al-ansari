// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Branch Location', {
	// refresh: function(frm) {

	// }
	map_loc: function(frm) {
		if(frm.doc.map_loc) {
			var loc = JSON.parse(frm.doc.map_loc).features[0].geometry.coordinates
			frm.set_value('from_longitude',loc[0][0][0])
			frm.set_value('to_longitude',loc[0][2][0])
			frm.set_value('from_latitude',loc[0][0][1])
			frm.set_value('to_latitude',loc[0][2][1])
		} else {
			frappe.msgprint("Enter the co-ordinates manually")
		}
	}
});
