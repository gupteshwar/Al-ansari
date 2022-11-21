from __future__ import unicode_literals
import frappe
from frappe.handler import uploadfile
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours

def after_insert(doc,method):
	if frappe.cache().get_value('photo_filedata'):
		docname = doc.name
		filedata = frappe.cache().get_value('photo_filedata')
		photoUpload(docname,filedata)
		data = uploadfile()
		frappe.db.set_value("Employee Checkin",docname,"photo",data.get('file_url'))
		frappe.db.set_value("Employee Checkin",docname,"is_photo",1)
		frappe.cache().set_value("photo_filedata", "")
	if doc.log_type == "OUT":
		actual_hours,rec = calculate_actual_hours_for_day(doc.employee)
		if(doc.name == rec):
			doc.actual_hours = actual_hours
			doc.save()

def validate(doc,method):
	if not doc.photo:
		if frappe.cache().get_value('photo_filedata'):
			docname = doc.name
			filedata = frappe.cache().get_value('photo_filedata')
			photoUpload(docname,filedata)
			data = uploadfile()
			doc.photo = data.get('file_url')
			frappe.cache().set_value("photo_filedata", "")
		else:
			frappe.throw("Photo Capture mandatory")


@frappe.whitelist()
def upload_photo(filedata):
	frappe.cache().set_value("photo_filedata", filedata)
	return "done"

def photoUpload(docname,filedata):
	data = {
		"from_form": 1,
		"doctype": "Employee Checkin",
		"docname": docname,
		"filename": docname+".png",
		"filedata":filedata
	}
	for p in ["from_form", "doctype", "docname", "filename", "filedata"]:
		frappe.form_dict[p] = data.get(p)

@frappe.whitelist()
def calculate_actual_hours(employee):
	record = frappe.db.sql("""
		SELECT employee, time from `tabEmployee Checkin` 
		where employee = %s
		and DATE(time) = CURDATE() 
		and log_type = 'IN';  
		""",(employee),as_dict=1)

	if record:
		holiday_list,h_ot_rate,nh_ot_rate,default_shift,grade = frappe.db.get_value("Employee",employee,['holiday_list','h_ot_rate','nh_ot_rate','default_shift','grade'])
		shift_hours = frappe.db.get_value("Shift Type",default_shift,["shift_hours"])
		productive_hours_ratio = frappe.db.get_value("Employee Grade",grade,["productive_hours_ratio"])
		print("holiday_list==",holiday_list)
		print("holiday_list==",h_ot_rate)
		print("holiday_list==",nh_ot_rate)
		print("record[0]==",productive_hours_ratio)
		if holiday_list :
			holiday_date = frappe.db.sql("""
				SELECT holiday_date from `tabHoliday`
				where holiday_date = CURDATE()
				and parent = %s
				""",(holiday_list),as_dict=1)
			print("holiday_date==",holiday_date)
			if len(holiday_date)>0:
				record[0]['ot_rate'] = h_ot_rate
			elif len(holiday_date)==0:
				print("Hi")
				record[0]['ot_rate'] = nh_ot_rate
		else:
			frappe.throw("Holiday List not found. Please get in touch with Admin and get holiday list assigned")

		record[0]['shift_hours'] = shift_hours or 0
		record[0]['productive_hours_ratio'] = productive_hours_ratio or 0
		print("record[0]==",record[0])

		return record[0]


@frappe.whitelist()
def validate_login_coordinates(frm):
	frm = frappe.json.loads(frm)
	emp_branches = frappe.db.sql("""select GROUP_CONCAT(DISTINCT(ab.branch)) as branch
	from `tabEmployee` e,`tabAlternate Branch` ab 
	where ab.parent = e.name 
	and e.name = %s""",(frm["employee"]),as_list=1)[0];

	branch = frappe.db.get_value("Employee",frm["employee"],"branch")
	print("branch",branch)
	if branch:
		emp_branches.append(branch)
	print("branch1==",emp_branches)

	branch = frappe.db.sql("""
		Select name 
		from `tabBranch Location` 
		where LEAST(from_latitude,to_latitude)<= %s 
		and GREATEST(from_latitude,to_latitude)>= %s 
		and LEAST(from_longitude,to_longitude)<= %s 
		and GREATEST(from_longitude,to_longitude)>= %s
		""",(frm["latitude"],frm["latitude"],frm["longitude"],frm["longitude"]),as_list=1)
	print("branch2==",branch)
	if emp_branches:
		if len(branch)<=0:
			frappe.throw("No suitable branch found for the for the co-ordinates recorded. Please check your location")
		else:
			if branch[0] in emp_branches:
				return True 
			else:
				return False		

@frappe.whitelist()
def calculate_actual_hours_for_day(employee):
	first_login = frappe.db.sql(""" 
		Select name,time 
		from `tabEmployee Checkin`
		where DATE(creation) = DATE(CURDATE())
		and log_type = 'IN'
		and employee = %s
		order by creation asc limit 1
		""",(employee),as_dict=1)

	last_login = frappe.db.sql(""" 
		Select name,time 
		from `tabEmployee Checkin`
		where DATE(creation) = DATE(CURDATE())
		and log_type = 'OUT'
		and employee = %s
		order by creation desc limit 1
		""",(employee),as_dict=1)

	print("first_login = ",first_login[0]["time"])
	print("last_login = ",last_login[0]["time"])

	actual_hours = time_diff_in_hours(last_login[0]["time"],first_login[0]["time"])
	print("actual_hours ==",actual_hours)
	return actual_hours,last_login[0]["name"]