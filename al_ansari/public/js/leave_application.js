frappe.ui.form.on('Leave Application', {
	refresh: function(frm) {
		// Rejoining Details button should be visible only on Annual Leave application
		if(frm.doc.docstatus==1 && !frm.doc.rejoining_details_ref && frm.doc.leave_type == 'Annual Leave') {
			frm.add_custom_button(__("Mark Rejoin Details"), function() {
				frappe.call({
					method: "al_ansari.al_ansari.doctype.rejoining_details.rejoining_details.validate_rejoining_record",
					args: {
						"leave": frm.doc,
					},
					callback: function(r) {
						if (r.message){
							var doclist = frappe.model.sync(r.message);
							frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
						}
					}
				})
			});
			
		}
	},
	validate: function(frm) {
		// auto fill rejoin date field
		frm.set_value('rejoin_date',frappe.datetime.add_days(frm.doc.to_date, 1))
		frappe.call({
		    method: "al_ansari.al_ansari.customization.leave_application.split_entries_monthly", //dotted path to server method
		    args:{
		    	"leave_type":frm.doc.leave_type,
		    	"from_date": frm.doc.from_date,
		    	"to_date":frm.doc.to_date
		    },
		    callback: function(r) {
		        // code snippet
		        frm.clear_table("eld_fraction_monthly")
		        console.log(r)
		        var rec = r.message
		        make_splitted_entries(rec,frm)
		    }
		});
	},
	on_submit: function(frm) {
		// auto fill rejoin date field
		frm.set_value('rejoin_date',frappe.datetime.add_days(frm.doc.to_date, 1))
		frappe.call({
		    method: "al_ansari.al_ansari.customization.leave_application.split_entries_monthly", //dotted path to server method
		    args:{
		    	"leave_type":frm.doc.leave_type,
		    	"from_date": frm.doc.from_date,
		    	"to_date":frm.doc.to_date
		    },
		    callback: function(r) {
		        // code snippet
		        frm.clear_table("eld_fraction_monthly")
		        var rec = r.message
		        make_splitted_entries(rec,frm)
		    }
		});
	}
});

function make_splitted_entries(rec,frm) {
    if(rec.length>0){
    	for(var e=0; e<rec.length;e++) {
    		var fd = new Date(frm.doc.from_date)
    		var ed = new Date(fd. getFullYear(), fd. getMonth()+1, 0)
    		var dd = ed.getDate()
    		var mm = ed.getMonth()+1
    		var yyyy = ed.getFullYear()
    		if (dd < 10) dd = '0' + dd;
    		if (mm < 10) mm = '0' + mm;
    		var f_ed = yyyy+"-"+mm+"-"+dd
    		console.log(f_ed)
    		if(e==0 && rec[e][0] != frm.doc.from_date) {
    			var childTable = cur_frm.add_child("eld_fraction_monthly");
				childTable.from_date = frm.doc.from_date
				childTable.to_date = f_ed 
    		}
    		var childTable = cur_frm.add_child("eld_fraction_monthly");
			childTable.from_date = rec[e][0]
			childTable.to_date = rec[e][1]
    	}
    	cur_frm.refresh_fields("eld_fraction_monthly");
    }
}
