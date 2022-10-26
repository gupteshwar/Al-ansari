frappe.ui.form.on('Employee Checkin', {
	onload: function(frm) {
		frm.toggle_reqd('latitude',1)
		frm.toggle_reqd('longitude',1)
	},
	log_type: function(frm) {
		if(frm.doc.employee) {
			frappe.call({
			    method: 'frappe.client.get_value',
			    args: {
			        'doctype': 'Employee',
			        'filters': {'name': frm.doc.employee},
			        'fieldname': [
			            'branch'
			        ]
			    },
			    async:false,
			    callback: function(r) {
			        if (!r.exc) {
			            validate_corordinates(frm,r.message.branch)
			        }
			    }
			});
		}
	}
})

var validate_corordinates = function(frm,branch){
	// validate the Geolocation co-ordinates
		frappe.call({
		    method: 'frappe.client.get_value',
		    args: {
		        'doctype': 'Branch Location',
		        'filters': {'name':branch},
		        'fieldname': [
		            'from_latitude',
		            'to_latitude',
		            'from_longitude',
		            'to_longitude'
		        ]
		    },
		    async:false,
		    callback: function(r) {
		        if (!r.exc) {
		            // logic to check whether between the co-ordinates else set the field to blank
		            var longi = Number(frm.doc.latitude)
		            var lati = Number(frm.doc.longitude)
		            var lati_1 = Number(r.message.from_latitude)
		            var lati_2 = Number(r.message.to_latitude)
		            var longi_1 = Number(r.message.from_longitude)
		            var longi_2 = Number(r.message.to_longitude)
		            console.log(lati_1+" "+lati_2+" "+longi_1+" "+longi_2)
		            if(lati >= Math.min(lati_1,lati_2) && lati <= Math.max(lati_1,lati_2) && longi >= Math.min(longi_1,longi_2) && longi <= Math.max(longi_1,longi_2)){
		            	console.log("OK")
		            } else {
		            	frm.set_value('latitude','')
		            	frm.set_value('longitude','')
		        		frappe.throw("Please ensure that you are within the branch locations")
		            }
		        }
		    }
		});
}