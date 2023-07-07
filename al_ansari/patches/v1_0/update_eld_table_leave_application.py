
import frappe
from al_ansari.al_ansari.customization.leave_application import split_entries_monthly,add_fractional_eld,calculate_fractional_wage

def execute():
	leave_applications = frappe.get_all("Leave Application",
			filters = [['docstatus','=',1],['leave_type','IN',('Sick Leave')]],
			fields=["name","leave_type"])
	print("Patch=",leave_applications)
	for l_app in leave_applications:
		leave_app = frappe.get_doc("Leave Application",l_app)
		linked_ppl = frappe.db.get_value("Leave Type",l_app.leave_type,"partial_paid_leave")

		from_date = leave_app.from_date.strftime('%Y-%m-%d')
		to_date = leave_app.to_date.strftime('%Y-%m-%d')
		if linked_ppl:
			if len(leave_app.eld_fraction_monthly) == 0:
				monthly_breakup = split_entries_monthly(l_app.leave_type,from_date,to_date)
				if monthly_breakup:
					for mb in monthly_breakup:
						if monthly_breakup[0][0] != from_date:
							leave_app.append('eld_fraction_monthly',{
									'from_date': from_date,
									'to_date':frappe.utils.add_days(mb[0],days=-1),
								})
							leave_app.save()
							print(leave_app.eld_fraction_monthly)	
							add_fractional_eld(leave_app,linked_ppl)
							leave_app.save()
						
						leave_app.append('eld_fraction_monthly',{
								'from_date': mb[0],
								'to_date':mb[1],
							})
						leave_app.save()
						print(leave_app.eld_fraction_monthly)	
						add_fractional_eld(leave_app,linked_ppl)
						leave_app.save()
					frappe.db.commit()
				else:
					leave_app.append('eld_fraction_monthly',{
								'from_date': from_date,
								'to_date':to_date,
							})
					leave_app.save()
					add_fractional_eld(leave_app,linked_ppl)
					leave_app.save()
					frappe.db.commit()
			else:
				print("Already up to date")