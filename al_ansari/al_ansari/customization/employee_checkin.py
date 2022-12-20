from __future__ import unicode_literals
import frappe
from frappe.handler import uploadfile
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours

# calculate actual hours for the day if log type is OUT
def calculate_actual_hours(doc,method):
	if doc.log_type == "OUT":
		record = frappe.db.sql("""
			SELECT employee, time from `tabEmployee Checkin` 
			where employee = %s
			and DATE(time) = DATE(%s) 
			and log_type = 'IN';  
			""",(doc.employee,doc.time),as_dict=1)
		print(record)
		if record:
			holiday_list,h_ot_rate,nh_ot_rate,default_shift,grade = frappe.db.get_value("Employee",doc.employee,['holiday_list','h_ot_rate','nh_ot_rate','default_shift','grade'])
			shift_hours = frappe.db.get_value("Shift Type",default_shift,["shift_hours"])
			productive_hours_ratio = frappe.db.get_value("Employee Grade",grade,["productive_hours_ratio"])
			# print("holiday_list==",holiday_list)
			# print("holiday_list==",h_ot_rate)
			# print("holiday_list==",nh_ot_rate)
			# print("record[0]==",productive_hours_ratio)
			if holiday_list :
				holiday_date = frappe.db.sql("""
					SELECT holiday_date from `tabHoliday`
					where holiday_date = Date(%s)
					and parent = %s
					""",(doc.time,holiday_list),as_dict=1)
				# print("holiday_date==",holiday_date)
				if len(holiday_date) > 0:
					# record[0]['ot_rate'] = h_ot_rate
					doc.is_holiday = 1
					doc.overtime_rate = h_ot_rate
				elif len(holiday_date) == 0:
					# record[0]['ot_rate'] = nh_ot_rate
					doc.is_holiday = 0
					doc.overtime_rate = nh_ot_rate
			else:
				frappe.throw("Holiday List not found. Please get in touch with Admin and get holiday list assigned")

			# record[0]['shift_hours'] = shift_hours or 0
			# record[0]['productive_hours_ratio'] = productive_hours_ratio or 0
			doc.shift_hours = shift_hours or 0
			doc.productive_hours =  productive_hours_ratio or 0
			# print("record[0]==",record[0])

			# return record[0]

def validate(doc,method):
	valid_loc = validate_login_coordinates(doc)
	print("valid_loc=",doc.valid_location)
	# if valid_loc == 

	if valid_loc.valid_location == 0:
		frappe.throw("Please make sure you are on valid location as per branches assigned to you")

	if not doc.photo:
		if frappe.cache().get_value('photo_filedata'):
			docname = doc.name
			filedata = frappe.cache().get_value('photo_filedata')
			photoUpload(docname,filedata)
			data = uploadfile()
			doc.photo = data.get('file_url')
			frappe.cache().set_value("photo_filedata", "")
		# else:
		# 	frappe.throw("Photo Capture mandatory")

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
		actual_hours,rec = calculate_actual_hours_for_day(doc.employee,doc.time)
		if(doc.name == rec):
			doc.actual_hours = actual_hours
			doc.save()

@frappe.whitelist()
def upload_photo(filedata):
	frappe.cache().set_value("photo_filedata", filedata)
	return "done"

def photoUpload(docname,filedata):
	data = {
		"from_form": 1,
		"filename": docname+".png",
		"filedata":filedata
	}
	for p in ["from_form", "doctype", "docname", "filename", "filedata"]:
		frappe.form_dict[p] = data.get(p)


@frappe.whitelist()
def validate_login_coordinates(frm):
	# frm = frappe.json.loads(frm)
	# print(type(frm))
	employee = frm.employee
	# to get branches of employee
	emp_branches = frappe.db.sql("""select GROUP_CONCAT(DISTINCT(ab.branch)) as branch
	from `tabEmployee` e,`tabAlternate Branch` ab 
	where ab.parent = e.name 
	and e.name = %s""",(employee),as_list=1)[0];
	# print("emp_branches == ",emp_branches)
	# get branch name for employee
	branch = frappe.db.get_value("Employee",frm.employee,"branch")
	# print("branch",branch)
	if branch:
		emp_branches.append(branch)
	# print("all branches assigned to emp ==",emp_branches)
	if None in emp_branches and len(emp_branches) == 1:
		frappe.throw("No Branch is assigned to you yet")
		return False

	branch = frappe.db.sql("""
		Select name 
		from `tabBranch Location` 
		where LEAST(from_latitude,to_latitude)<= %s 
		and GREATEST(from_latitude,to_latitude)>= %s 
		and LEAST(from_longitude,to_longitude)<= %s 
		and GREATEST(from_longitude,to_longitude)>= %s
		""",(frm.latitude,frm.latitude,frm.longitude,frm.longitude),as_list=1)
	print("current login branch out of all assigned==",branch[0])
	if emp_branches:
		if len(branch) <= 0:
			frappe.msgprint("No suitable branch found for the for the co-ordinates recorded. Please check your location")
			frm.valid_location = 0
			return frm
		else:
			if branch[0][0] in emp_branches:
				print("True")
				frm.valid_location = 1
				return frm 
			else:
				print("False")
				# frappe.msgprint("Please check the branches assigned and login branch")		
				frm.valid_location = 0
				return frm

@frappe.whitelist()
def calculate_actual_hours_for_day(employee,time):
	# first_login = frappe.db.sql(""" 
	# 	Select name,time 
	# 	from `tabEmployee Checkin`
	# 	where DATE(creation) = DATE(CURDATE())
	# 	and log_type = 'IN'
	# 	and employee = %s
	# 	order by creation asc limit 1
	# 	""",(employee),as_dict=1)

	# last_login = frappe.db.sql(""" 
	# 	Select name,time 
	# 	from `tabEmployee Checkin`
	# 	where DATE(creation) = DATE(CURDATE())
	# 	and log_type = 'OUT'
	# 	and employee = %s
	# 	order by creation desc limit 1
	# 	""",(employee),as_dict=1)

	first_login = frappe.db.sql(""" 
		Select name,time 
		from `tabEmployee Checkin`
		where DATE(time) = DATE(%s)
		and log_type = 'IN'
		and employee = %s
		order by creation asc limit 1
		""",(time,employee),as_dict=1)

	last_login = frappe.db.sql(""" 
		Select name,time 
		from `tabEmployee Checkin`
		where DATE(time) = DATE(%s)
		and log_type = 'OUT'
		and employee = %s
		order by creation desc limit 1
		""",(time,employee),as_dict=1)

	if first_login:
		# print("@@@@@@@@@@@@@@@@@=========",first_login)
		# print("first_login = ",first_login[0]["time"])
		# print("last_login = ",last_login[0]["time"])

		actual_hours = time_diff_in_hours(last_login[0]["time"],first_login[0]["time"])
		# print("actual_hours ==",actual_hours)
		return actual_hours,last_login[0]["name"]
	else:
		frappe.throw("No Log In entry found for the day.Please Log In first in order to make a Log Out Entry")