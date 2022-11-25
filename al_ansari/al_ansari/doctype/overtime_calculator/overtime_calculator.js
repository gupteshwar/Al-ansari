// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Calculator', {
	refresh: function(frm) {
		frm.add_custom_button(__("Additional Salary"), function() {
			frappe.call({
			    method: "al_ansari.al_ansari.doctype.overtime_calculator.overtime_calculator.additional_salary_entry", //dotted path to server method
			    args: {
			    	"frm":frm.doc
			    },
			    callback: function(r) {
			        // code snippet
			        console.log(r.message)
			        
			    }
			});
		})
	},
	from_date: function(frm) {
	    if(frm.doc.from_date) {
	        frm.set_value('to_date',moment(frm.doc.from_date).endOf('month').format('YYYY-MM-DD'))
	    }
	    if((frm.doc.from_date && frm.doc.to_date)&&(frm.doc.from_date > frm.doc.to_date)) {
	        frappe.throw(" 'From date' cannot be greater than 'To Date' ")
	    }
	},
	to_date: function(frm) {
	    if((frm.doc.from_date && frm.doc.to_date)&&(frm.doc.from_date > frm.doc.to_date)) {
	        frappe.throw(" 'From date' cannot be greater than 'To Date' ")
	    }
	},
	validate: function(frm) {
		if(frm.doc.from_date > frm.doc.to_date) {
		    frappe.throw(" 'From date' cannot be greater than 'To Date' ")
		}
	},
	get_employees: function(frm) {
		frappe.call({
		    method: "al_ansari.al_ansari.doctype.overtime_calculator.overtime_calculator.get_employees_on_oc", //dotted path to server method
		    args: {
		    	"from_date": frm.doc.from_date,
		    	"to_date": frm.doc.to_date
		    },
		    callback: function(r) {
		        // code snippet
		        console.log(r.message)
		        frm.clear_table('overtime_calculator_detail')
		        for(var i=0;i<r.message.length;i++){
		        	var childTable = cur_frm.add_child("overtime_calculator_detail");
		        	childTable.employee = r.message[i]["employee"]
		        	childTable.employee_name = r.message[i]["employee_name"]
		        	childTable.productive_hours = r.message[i]["productive_hours"]
		        	childTable.actual_hours = r.message[i]["actual_hours"]
		        	childTable.shift_hours = r.message[i]["shift_hours"]
		        	childTable.overtime_amount = r.message[i]["overtime_amount"]
		        }
		        
		        cur_frm.refresh_fields("overtime_calculator_detail");
		    }
		});
	}
});
