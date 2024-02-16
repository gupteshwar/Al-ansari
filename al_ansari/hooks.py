


from . import __version__ as app_version

app_name = "al_ansari"
app_title = "Al Ansari"
app_publisher = "Indictrans"
app_description = "Al Ansari Exchange"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "neha.t@indictranstech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/al_ansari/css/al_ansari.css"
# app_include_js = "/assets/al_ansari/js/al_ansari.js"

# include js, css files in header of web template
# web_include_css = "/assets/al_ansari/css/al_ansari.css"
# web_include_js = "/assets/al_ansari/js/al_ansari.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "al_ansari/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
	"Employee" : "public/js/employee.js",
	"Leave Application": "public/js/leave_application.js",
	"Employee Checkin": "public/js/employee_checkin.js",
	"Shift Type": "public/js/shift_type.js",
	"Expense Claim": "public/js/expense_claim.js",
	"Leave Type": "public/js/leave_type.js",
	"Payroll Entry": "public/js/payroll_entry.js",	
	"Job Opening": "public/js/job_opening.js",
	"Salary Structure Assignment": "public/js/salary_structure_assignment.js",
	"Additional Salary": "public/js/additional_salary.js",
	"Salary Slip": "public/js/salary_slip.js",
	"Appraisal": "public/js/appraisal.js",
	"Customer": "public/js/customer.js",
	"Journal Entry": "public/js/journal_entry.js",
	"Purchase Invoice": "public/js/purchase_invoice.js",
	"Sales Invoice": "public/js/sales_invoice.js",
	"Sales Order": "public/js/sales_order.js",
	"Purchase Order": "public/js/purchase_order.js",
	"Blanket Order": "public/js/blanket_order.js",
	"Request for Quotation": "public/js/request_for_quotation.js",
	"Supplier Quotation": "public/js/supplier_quotation.js",
	"POS Closing Entry" : "public/js/pos_closing_entry.js",
	"POS Opening Entry" : "public/js/pos_opening_entry.js",
	"Job Applicant": "public/js/job_applicant.js",
	"Employee Advance": "public/js/employee_advance.js",
	"Quotation": "public/js/quotation.js",
	"Purchase Receipt": "public/js/purchase_receipt.js",
	"Purchase Invoice": "public/js/purchase_invoice.js",
	"Landed Cost Voucher": "public/js/landed_cost_voucher.js",
	"Stock Entry": "public/js/stock_entry.js",
    "Asset Movement": "public/js/asset_movement.js",
	"Payment Entry": "public/js/payment_entry.js",
    "Delivery Note": "public/js/delivery_note.js",
    "POS Invoice":"public/js/pos_invoice.js",
    "Asset Repair":"public/js/asset_repair.js",
    "Item Price List": "public/js/item_price_list.js",
    "Material Request": "public/js/material_request.js",
}

fixtures = ['Role','Custom Field','Property Setter','Print Format','Client Script','Report','Workflow','Workflow State','Workflow Action']

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "al_ansari.install.before_install"
# after_install = "al_ansari.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "al_ansari.uninstall.before_uninstall"
# after_uninstall = "al_ansari.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "al_ansari.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }
doc_events = {
	"Employee": {
		"before_save": ["al_ansari.al_ansari.customization.employee.before_save"],
	},
	"Expense Claim": {
		"before_submit": ["al_ansari.al_ansari.customization.expense_claim.transfer_child_attachment_to_parent"],
		"validate": ["al_ansari.al_ansari.customization.expense_claim.check_validation"]
	},
	"Leave Application": {
		# "validate":["al_ansari.al_ansari.customization.sleave_application.update_employee_status"],
		"before_submit": ["al_ansari.al_ansari.customization.leave_application.update_employee_status"],
		"after_insert": ["al_ansari.al_ansari.customization.leave_application.after_save"]
	},
	"Employee Transfer": {
		"before_submit": ["al_ansari.al_ansari.customization.employee_transfer.before_submit"]
	},
	"Employee Checkin": {	
		"before_validate": ["al_ansari.al_ansari.customization.employee_checkin.calculate_actual_hours"],
		"after_insert": ["al_ansari.al_ansari.customization.employee_checkin.after_insert"],
		"validate": ["al_ansari.al_ansari.customization.employee_checkin.validate"]
	},
	"Payment Entry":{
		"before_save":["al_ansari.al_ansari.customization.payment_entry.validate_paid_amt_greater_than_outstanding_amt"],
		"before_submit": ["al_ansari.al_ansari.customization.payment_entry.validate_outstanding_amount"],
		"validate": ["al_ansari.al_ansari.customization.payment_entry.validate_reference_details"]
	},
	"Sales Order":{
		"before_insert": "al_ansari.al_ansari.customization.sales_order.validate_cost_center",
		"before_save":["al_ansari.al_ansari.customization.sales_order.before_save"],
		"on_submit":["al_ansari.al_ansari.customization.sales_order.on_submit"],
        "validate":["al_ansari.al_ansari.customization.utils.validate"]
	},
    "Sales Invoice":{
		"before_insert": "al_ansari.al_ansari.customization.sales_invoice.validate_cost_center",
        "validate":["al_ansari.al_ansari.customization.utils.validate"]
	},
	"Delivery Note": {
		"before_insert": "al_ansari.al_ansari.customization.delivery_note.validate_cost_center"
	},
	"Employee Advance":{
		"on_submit":["al_ansari.al_ansari.customization.employee.valid_employee_adv"]
	},
	"Payment Request": {
		"validate": ["al_ansari.al_ansari.customization.payment_request.payment_request_validate"]
	},
	"Stock Entry":{
		"before_submit": ["al_ansari.al_ansari.customization.stock_entry.before_submit"],
		"on_submit": ["al_ansari.al_ansari.customization.stock_entry.on_submit"]
	},
    "Purchase Order":{
		"before_insert": "al_ansari.al_ansari.customization.purchase_order.validate_cost_center",
        "validate":["al_ansari.al_ansari.customization.utils.validate"]
	},
    "Purchase Invoice":{
		"before_insert": "al_ansari.al_ansari.customization.purchase_invoice.validate_cost_center",
        "validate":["al_ansari.al_ansari.customization.utils.validate"]
	},
	"Journal Entry": {
		"validate": "al_ansari.al_ansari.customization.utils.validate_total_debit_and_credit_against_cc"
	},
	"Purchase Receipt": {
		"before_insert": "al_ansari.al_ansari.customization.purchase_receipt.validate_cost_center",
	},
	"Asset Repair": {
		"validate": "al_ansari.al_ansari.customization.asset_repair.validate_asset_repair",
	},
	"Quotation": {
		"validate":["al_ansari.al_ansari.customization.quotation.before_save"]
	}
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"al_ansari.tasks.all"
#	],
#	"daily": [
#		"al_ansari.tasks.daily"
#	],
#	"hourly": [
#		"al_ansari.tasks.hourly"
#	],
#	"weekly": [
#		"al_ansari.tasks.weekly"
#	]
#	"monthly": [
#		"al_ansari.tasks.monthly"
#	]
# }

scheduler_events = {
	"cron": {
			"2 0 * * *": [
				"al_ansari.al_ansari.customization.leave_application.check_update_working_status_for_leave"
			]
		},
	# "daily": [
	# 	"al_ansari.al_ansari.customization.leave_application.check_update_working_status_for_leave"
	# ]
}
# Testing
# -------

# before_tests = "al_ansari.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.doctype.event.event.get_events": "al_ansari.event.get_events"
	"erpnext.hr.utils.get_employee_fields_label": "al_ansari.al_ansari.customization.leave_application.get_employee_fields_label",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "al_ansari.task.get_dashboard_data"
# }

override_doctype_dashboards = {
	"Quotation": "al_ansari.al_ansari.customization.quotation.get_data"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]




# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"al_ansari.auth.validate"
# ]

