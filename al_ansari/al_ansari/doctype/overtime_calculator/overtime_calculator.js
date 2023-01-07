// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Calculator', {
	refresh: function(frm) {
		// if(frm.doc.docstatus ==1){
		// 	frm.add_custom_button(__("Additional Salary"), function() {
		// 		if(frm.doc.payroll_date) {
		// 			frappe.call({
		// 			    method: "al_ansari.al_ansari.doctype.overtime_calculator.overtime_calculator.additional_salary_entry", //dotted path to server method
		// 			    args: {
		// 			    	"frm":frm.doc
		// 			    },
		// 			    callback: function(r) {
		// 			        // code snippet
		// 			        console.log(r.message)
					        
		// 			    }
		// 			});
		// 		}else {
		// 			frappe.throw("Please select the Payroll Date to create Additional Salary records")
		// 		}
				
		// 	})
		// }
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
	branch: function(frm) {
		frm.clear_table('overtime_calculator_detail')
		frm.refresh_field('overtime_calculator_detail')
	},
	reporting_manager: function(frm) {
		frm.clear_table('overtime_calculator_detail')
		frm.refresh_field('overtime_calculator_detail')
	},
	validate: function(frm) {
		if(frm.doc.from_date > frm.doc.to_date) {
		    frappe.throw(" 'From date' cannot be greater than 'To Date' ")
		}
		if(!frm.doc.payroll_date) {
			frappe.throw("Please enter the payroll date to proceed")
		}
		if(frm.doc.overtime_calculator_detail){
			for(var x=0;x<frm.doc.overtime_calculator_detail.length;x++) {
				// if(frm.doc.overtime_calculator_detail[x].actual_hours == undefined ||frm.doc.overtime_calculator_detail[x].actual_hours == 0)
				frm.doc.overtime_calculator_detail[x].actual_hours = frm.doc.overtime_calculator_detail[x].holiday_actual_hours.toFixed(2) +frm.doc.overtime_calculator_detail[x].non_holiday_actual_hours.toFixed(2)
				frm.doc.overtime_calculator_detail[x].holiday_productive_hours = (frm.doc.overtime_calculator_detail[x].holiday_overtime.toFixed(2) * frm.doc.overtime_calculator_detail[x].productive_hours_ratio)
				frm.doc.overtime_calculator_detail[x].non_holiday_productive_hours = frm.doc.overtime_calculator_detail[x].non_holiday_overtime.toFixed(2)* frm.doc.overtime_calculator_detail[x].productive_hours_ratio
				frm.doc.overtime_calculator_detail[x].holiday_overtime_amount = frm.doc.overtime_calculator_detail[x].holiday_productive_hours.toFixed(2) * frm.doc.overtime_calculator_detail[x].holiday_overtime_rate
				frm.doc.overtime_calculator_detail[x].non_holiday_overtime_amount = frm.doc.overtime_calculator_detail[x].non_holiday_productive_hours.toFixed(2) * frm.doc.overtime_calculator_detail[x].non_holiday_overtime_rate
				frm.doc.overtime_calculator_detail[x].overtime_amount = frm.doc.overtime_calculator_detail[x].holiday_overtime_amount + frm.doc.overtime_calculator_detail[x].non_holiday_overtime_amount
				// frm.doc.overtime_calculator_detail[x].total_overtime = frm.doc.overtime_calculator_detail[x].holiday_overtime + frm.doc.overtime_calculator_detail[x].non_holiday_overtime
			}	
		} else {
			frappe.throw("Please click the Get Employees button and then Save.")
		}
		

		// frm.doc.overtime_calculator_detail[x].non_holiday_overtime_amt = frm.doc.overtime_calculator_detail[x].total_overtime * frm.doc.overtime_calculator_detail[x].productive_hours_ratio
		// frappe.call({
	    //     method: "frappe.client.get_value",
	    //     args: {
	    //             doctype: "Overtime Calculator",
	    //             fieldname: "name",
	    //             filters: {
		// 					from_date: frm.doc.from_date,
		// 					to_date: frm.doc.to_date,
		// 					docstatus: 1
	    //             }
	    //     },
	    //     callback: function(response) {
	    //          var name = response.message.name;
	    //          if (name) {
	    //             frappe.msgprint("Record for same time period already exists");
		// 			validated=false;
	    // 			return false;
			
	    //          }
	    //     }
		// });
	},
	get_employees: function(frm) {
		frappe.call({
		    method: "al_ansari.al_ansari.doctype.overtime_calculator.overtime_calculator.get_employees_on_oc", //dotted path to server method
		    args: {
		    	"from_date": frm.doc.from_date,
		    	"to_date": frm.doc.to_date,
		    	"branch": frm.doc.branch || " ",
		    	"reporting_manager": frm.doc.reporting_manager || " "
		    },
		    callback: function(r) {
		        // code snippet
		        frm.clear_table('overtime_calculator_detail')
		        for(var i=0;i<r.message.length;i++){
		        	var childTable = cur_frm.add_child("overtime_calculator_detail");
		        	childTable.employee = r.message[i]["name"]
		        	childTable.employee_name = r.message[i]["employee_name"]
		        	childTable.productive_hours_ratio = r.message[i]["productive_hours_ratio"]
		        	childTable.holiday_overtime_rate = r.message[i]["holiday_overtime_rate"]
		        	childTable.non_holiday_overtime_rate = r.message[i]["non_holiday_overtime_rate"]
		        	childTable.holiday_overtime = r.message[i]["holiday_overtime"]
		        	childTable.non_holiday_overtime = r.message[i]["non_holiday_overtime"]
		        	childTable.holiday_actual_hours = r.message[i]["holiday_actual_hours"]
		        	childTable.non_holiday_actual_hours = r.message[i]["non_holiday_actual_hours"]
		        	childTable.holiday_shift_total = r.message[i]["h_shift_total"]
		        	childTable.non_holiday_shift_total = r.message[i]["nh_shift_total"]
		        	childTable.shift_hours = r.message[i]["h_shift_total"] + r.message[i]["nh_shift_total"]
		        	// childTable.total_overtime = Number(r.message[i]["holiday_overtime"]) + Number(r.message[i]["non_holiday_overtime"])
		        }
		        
		        cur_frm.refresh_fields("overtime_calculator_detail");
		    }
		});
	}
});
