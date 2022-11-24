frappe.ui.form.on('Employee Checkin', {
	onload: function(frm) {
		frm.toggle_reqd('latitude',1)
		frm.toggle_reqd('longitude',1)
	},
	refresh: function(frm) {
		frm.add_custom_button(__('Capture Photo'), function() {
			frm.events.capture_photo()
		});	
		if (!frm.doc.__islocal) {
			frm.set_df_property("photo","hidden",0)
			frm.set_df_property("check_in","hidden",0)
			frm.set_df_property("profile_pic","hidden",0)
		}
		else
		{
			frm.set_df_property("photo","hidden",1)
			frm.set_df_property("check_in","hidden",1)
			frm.set_df_property("profile_pic","hidden",1)
		}
		document.getElementsByClassName("btn-attach")[0].style.display = "none";
		document.getElementsByClassName("btn-xs")[0].style.display = "none";
		if(frm.doc.photo)
		{
			frm.get_field("profile_pic").$wrapper.html(`<img src=${frm.doc.photo} width="150" height="200"><br><br><br>`);
		}
		else
		{
			frm.get_field("profile_pic").$wrapper.html(``);
		}
	},
	capture_photo: () => {
		const capture = new frappe.ui.Capture({
			animate: false,
			  error: true
		})
		capture.show()
		capture.submit(data => {
			cur_frm.call({
				method: "al_ansari.al_ansari.customization.employee_checkin.upload_photo",
				args: {
					filedata: data
				},
				callback: function(r) {
					if (r.message=="done") {
						cur_frm.set_value("photo","");
					}
				}
			});
		})

	},
	log_type: function(frm) {
		if(frm.doc.employee) {
			frappe.call({
			    method: 'frappe.client.get_value',
			    args: {
			        'doctype': 'Employee',
			        'filters': {'name': frm.doc.employee},
			        'fieldname': [
			            'branch',
			            'default_shift'
			        ]
			    },
			    async:false,
			    callback: function(r) {
			        if (!r.exc) {
			        	console.log(r.message)
			            validate_corordinates(frm)
			            frm.set_value('shift',r.message.default_shift)
			        }
			    }
			});
		}
	},
	before_save: function(frm) {
		if(frm.doc.log_type == 'OUT') {
			// calculate the actual hours and validate working day
			frappe.call({
			    method: "al_ansari.al_ansari.customization.employee_checkin.calculate_actual_hours", //dotted path to server method
			    args: {
			    	"employee": frm.doc.employee,
			    },
			    callback: function(r) {
			        // code snippet
			        console.log("calculate_actual_hours==" + r.message["actual_hours"])
			        frm.set_value('overtime_rate', r.message["ot_rate"])
			        frm.set_value('productive_hours',r.message["productive_hours_ratio"])
			        frm.set_value('actual_hours', r.message["actual_hours"])
			    }
			});
		}
	}
})

var validate_corordinates = function(frm,branch){
	// validate the Geolocation co-ordinates

		frappe.call({
		    method: "al_ansari.al_ansari.customization.employee_checkin.validate_login_coordinates",
		    args: {
		        'frm': frm.doc
		    },
		    callback: function(r) {
		        if (!r.exc) {
		            console.log(r.message)
		        }
		    }
		});
}