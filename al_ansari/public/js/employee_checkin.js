frappe.ui.form.on('Employee Checkin', {
	onload: function(frm) {
		frm.toggle_reqd('latitude',1)
		frm.toggle_reqd('longitude',1)
		if(frm.is_new()) {
			frm.set_value('manual_entry',1)
		}
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
	employee:function(frm) {
		if(frm.doc.time.split(" ")[1].split(":")[0]>="12") {
			frm.set_value("log_type","OUT")
		} else {
			frm.set_value("log_type","IN")
		}
	},
	validate:function (frm) {
		if(frm.doc.time.split(" ")[1].split(":")[0]>="12") {
			frm.set_value("log_type","OUT")
		} else {
			frm.set_value("log_type","IN")
		}
	}
	
})