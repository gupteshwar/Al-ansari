frappe.ui.form.on('Shift Type', {
	validate: function(frm) {
		// Calculate the shift hours
		var shift_hours = calculate_time_diff(frm.doc.start_time,frm.doc.end_time)
		frm.set_value('shift_hours',shift_hours)
	}
})

function calculate_time_diff(start_time,end_time) {
	var st = start_time.split(":")
	var et = end_time.split(":")
	var h = parseFloat(et[0]) - parseFloat(st[0])
	var m = parseFloat((parseFloat(et[1]) - parseFloat(st[1]))/60)
	var s = parseFloat((parseFloat(et[2]) - parseFloat(st[2]))/3600)
	var fh = parseFloat(h+m+s)
	return fh
}