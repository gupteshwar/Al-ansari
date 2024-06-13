import frappe
from collections import OrderedDict
import json
from frappe import _, _dict
from frappe.utils import cstr, getdate
from six import iteritems

from math import ceil


from erpnext import get_company_currency, get_default_company
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimension_with_children,
)
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.report.utils import convert_to_presentation_currency, get_currency
from erpnext.accounts.utils import get_account_currency



def validate_reference_details(doc,method):
	if len(doc.references_details)==0 and not doc.cost_center:
		pass
	if len(doc.references)>0 and len(doc.references_details)==0 and doc.is_new !=1:
		frappe.throw("Please click the Get Detailed Entries button to proceed")
	# else:
		# check_and_allocate_amount(doc)
	total_reference_amount = 0
	total_detail_reference_amount = 0

	for rec in doc.references:
		total_reference_amount += rec.allocated_amount

	for rec1 in doc.references_details:
		total_detail_reference_amount += rec1.allocated_amount

	# print("total_reference_amount", total_reference_amount)
	# print("total_detail_reference_amount", total_detail_reference_amount)

	# if total_reference_amount > doc.paid_amount: 
	# 	frappe.throw("Cannot Allocate More amount from Paid Amount")

	# if total_detail_reference_amount > doc.paid_amount:
	# 	frappe.throw("Cannot Allocate More amount from Paid Amount")

	if len(doc.references)>0 and len(doc.references_details) > 0 :
		if doc.references:
			grand_total=0
			outstanding = 0
			allocated_amount_r = 0
			for r in doc.references:
				grand_total += r.total_amount
				outstanding += r.outstanding_amount

				allocated_amount_r += round(r.allocated_amount,2)

			doc.grand_total = grand_total
			doc.total_outstanding = outstanding 

		if doc.references_details :
			t_outstanding = 0
			t_allocated = 0
			t_amount = 0

			default_currency = frappe.db.get_value("Company", doc.company, 'default_currency')
			if doc.paid_from_account_currency == default_currency:
				for i in doc.references_details:
					t_amount += i.amount
					t_outstanding +=i.outstanding
					t_allocated +=round(i.allocated_amount,2)
				doc.total_outstanding = t_outstanding

				doc.total_amount = t_amount
				doc.total_allocated = t_allocated
			else:
				for i in doc.references_details:
					t_amount += i.amount 
					t_outstanding +=i.outstanding
					t_allocated +=round(i.allocated_amount, 2)
				doc.total_outstanding = t_outstanding

				doc.total_amount = t_amount
				doc.total_allocated = t_allocated
		print("====================",t_allocated,allocated_amount_r)
		# if round(t_allocated, 2) != round(allocated_amount_r,2):
		# 	frappe.throw("The total allocated amount should be same in both the table and also as paid amount")
		

# def check_and_allocate_amount(doc):
# 	for ref in doc.references:
# 		ref_allocation = 0
# 		for ref_d in doc.references_details:
# 			if ref['reference_name'] == ref_d['reference_name']:
# 				ref_allocation += ref_d['allocated_amount']
# 		ref['allocated_amount'] = ref_allocation

def validate_paid_amt_greater_than_outstanding_amt(doc,method):

	default_currency = frappe.db.get_value("Company", doc.company, 'default_currency')
	if doc.paid_from_account_currency == default_currency:
		# if doc.references:
		# 	total_outstanding = 0
		# 	for i in doc.references:
		# 		total_outstanding = total_outstanding + i.outstanding_amount
		# 	if  total_outstanding < doc.paid_amount :
		# 			frappe.throw(title="Amount Exceeded!", msg="Paid amount is greater than the Outstanding amount")

		# if doc.references_details:
		# 	total_outstanding = 0
		# 	for i in doc.references_details:
		# 		total_outstanding = total_outstanding + i.allocated_amount
		# 	if total_outstanding > doc.paid_amount:
		# 		frappe.throw(title="Amount Exceeded!", msg="Allocated amount is less or equal to the Paid Amount")

		if not doc.references and not doc.references_details:
			if not doc.cost_center:
				frappe.throw(title="Mandatory", msg="Please select the cost center to proceeds")
			if doc.party_balance < doc.paid_amount and not doc.is_advance_pay:
				frappe.throw(title="Amount Exceeded!",msg="Paid Amount exceeds Party Balance. Please check the Is Advance checkbox to proceed.")


	

TRANSLATIONS = frappe._dict()

@frappe.whitelist()
def get_general_ledger_data(filters):
    filters = frappe._dict(json.loads(filters))
    filters.party = [filters.get('party')]
    get_data = execute(filters)

    data_to_show = ""
    header = f'''<div class="wrapper" style="width:100%; overflow-x:auto;">
            <center><h3>Genral Ledger</h3></center>
            <table class="table table-bordered" style="width:100%">
            <tr>
            <th>Account</th>
            <th>Debit</th>
            <th>Credit</th>
            <th>Balance</th>
            </tr>
            '''

    data_to_show = data_to_show + '''<tr>
                                    <td>Opening</td>
                                    <td>{debit} </td>
                                    <td>{credit}</td>
                                    <td>{balance}</td>
                                    </tr>'''.format(debit = get_data[0]['debit'], 
                                            credit = get_data[0]['credit'], 
                                            balance = get_data[0]['balance'])

    data_to_show = data_to_show + '''<tr>
                                    <td>For The Period</td>
                                    <td>{debit} </td>
                                    <td>{credit}</td>
                                    <td>{balance}</td>
                                    </tr>'''.format(debit = get_data[-2]['debit'], 
                                            credit = get_data[-2]['credit'], 
                                            balance = get_data[-2]['balance'])

    data_to_show = data_to_show + '''<tr>
                                    <td>Closing</td>
                                    <td>{debit} </td>
                                    <td>{credit}</td>
                                    <td>{balance}</td>
                                    </tr>'''.format(debit = get_data[-1]['debit'], 
                                            credit = get_data[-1]['credit'], 
                                            balance = get_data[-1]['balance'])

    data_to_show = data_to_show + '''</table> </div>''' 
    
    return header+data_to_show
   
def execute(filters):
    if not filters:
        return [], []

    account_details = {}

    for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
        account_details.setdefault(acc.name, acc)

    if filters.get("party"):
        filters.party = frappe.parse_json(list(filters.get("party")))

    validate_filters(filters, account_details)

    validate_party(filters)

    filters = set_account_currency(filters)

    update_translations()

    res = get_result(filters, account_details)
    
    return res

def update_translations():
	TRANSLATIONS.update(
		dict(OPENING=_("Opening"), TOTAL=_("Total"), CLOSING_TOTAL=_("Closing (Opening + Total)"))
	)

def validate_filters(filters, account_details):
	if not filters.get("company"):
		frappe.throw(_("{0} is mandatory").format(_("Company")))

	if not filters.get("from_date") and not filters.get("to_date"):
		frappe.throw(
			_("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date")))
		)

	if filters.get("account"):
		filters.account = frappe.parse_json(filters.get("account"))
		for account in filters.account:
			if not account_details.get(account):
				frappe.throw(_("Account {0} does not exists").format(account))

	if filters.get("account") and filters.get("group_by") == "Group by Account":
		filters.account = frappe.parse_json(filters.get("account"))
		for account in filters.account:
			if account_details[account].is_group == 0:
				frappe.throw(_("Can not filter based on Child Account, if grouped by Account"))

	if filters.get("voucher_no") and filters.get("group_by") in ["Group by Voucher"]:
		frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	if filters.get("project"):
		filters.project = frappe.parse_json(filters.get("project"))

	if filters.get("cost_center"):
		filters.cost_center = frappe.parse_json(filters.get("cost_center"))

def validate_party(filters):
	party_type, party = filters.get("party_type"), filters.get("party")
   
	if party and party_type:
		for d in [party]:
			if not frappe.db.exists(party_type, d):
				frappe.throw(_("Invalid {0}: {1}").format(party_type, d))

def set_account_currency(filters):
	if filters.get("account") or (filters.get("party") and len(filters.party) == 1):
		filters["company_currency"] = frappe.get_cached_value(
			"Company", filters.company, "default_currency"
		)
		account_currency = None

		if filters.get("account"):
			if len(filters.get("account")) == 1:
				account_currency = get_account_currency(filters.account[0])
			else:
				currency = get_account_currency(filters.account[0])
				is_same_account_currency = True
				for account in filters.get("account"):
					if get_account_currency(account) != currency:
						is_same_account_currency = False
						break

				if is_same_account_currency:
					account_currency = currency

		elif filters.get("party"):
			gle_currency = frappe.db.get_value(
				"GL Entry",
				{"party_type": filters.party_type, "party": filters.party[0], "company": filters.company},
				"account_currency",
			)

			if gle_currency:
				account_currency = gle_currency
			else:
				account_currency = (
					None
					if filters.party_type in ["Employee", "Student", "Shareholder", "Member"]
					else frappe.db.get_value(filters.party_type, filters.party[0], "default_currency")
				)

		filters["account_currency"] = account_currency or filters.company_currency
		if filters.account_currency != filters.company_currency and not filters.presentation_currency:
			filters.presentation_currency = filters.account_currency

	return filters

def get_result(filters, account_details):
    accounting_dimensions = []
    if filters.get("include_dimensions"):
        accounting_dimensions = get_accounting_dimensions()

    gl_entries = get_gl_entries(filters, accounting_dimensions)

    data = get_data_with_opening_closing(filters, account_details, accounting_dimensions, gl_entries)
    
    result = get_result_as_list(data, filters)

    return result

def get_gl_entries(filters, accounting_dimensions):
    currency_map = get_currency(filters)
    select_fields = """, debit, credit, debit_in_account_currency,
        credit_in_account_currency """

    order_by_statement = "order by posting_date, account, creation"

    if filters.get("include_dimensions"):
        order_by_statement = "order by posting_date, creation"

    if filters.get("group_by") == "Group by Voucher":
        order_by_statement = "order by posting_date, voucher_type, voucher_no"
    if filters.get("group_by") == "Group by Account":
        order_by_statement = "order by account, posting_date, creation"

    if filters.get("include_default_book_entries"):
        filters["company_fb"] = frappe.db.get_value(
            "Company", filters.get("company"), "default_finance_book"
        )

    dimension_fields = ""
    if accounting_dimensions:
        dimension_fields = ", ".join(accounting_dimensions) + ","

    distributed_cost_center_query = ""
    if filters and filters.get("cost_center"):
        select_fields_with_percentage = """, debit*(DCC_allocation.percentage_allocation/100) as debit,
        credit*(DCC_allocation.percentage_allocation/100) as credit,
        debit_in_account_currency*(DCC_allocation.percentage_allocation/100) as debit_in_account_currency,
        credit_in_account_currency*(DCC_allocation.percentage_allocation/100) as credit_in_account_currency """

        distributed_cost_center_query = """
        UNION ALL
        SELECT name as gl_entry,
            posting_date,
            account,
            party_type,
            party,
            voucher_type,
            voucher_no, {dimension_fields}
            cost_center, project,
            against_voucher_type,
            against_voucher,
            account_currency,
            remarks, against,
            is_opening, `tabGL Entry`.creation {select_fields_with_percentage}
        FROM `tabGL Entry`,
        (
            SELECT parent, sum(percentage_allocation) as percentage_allocation
            FROM `tabDistributed Cost Center`
            WHERE cost_center IN %(cost_center)s
            AND parent NOT IN %(cost_center)s
            GROUP BY parent
        ) as DCC_allocation
        WHERE company=%(company)s
        {conditions}
        AND posting_date <= %(to_date)s
        AND cost_center = DCC_allocation.parent
        """.format(
            dimension_fields=dimension_fields,
            select_fields_with_percentage=select_fields_with_percentage,
            conditions=get_conditions(filters).replace("and cost_center in %(cost_center)s ", ""),
        )

    gl_entries = frappe.db.sql(
        """
        select
            name as gl_entry, posting_date, account, party_type, party,
            voucher_type, voucher_no, {dimension_fields}
            cost_center, project,
            against_voucher_type, against_voucher, account_currency,
            remarks, against, is_opening, creation {select_fields}
        from `tabGL Entry`
        where company=%(company)s {conditions}
        {distributed_cost_center_query}
        {order_by_statement}
        """.format(
            dimension_fields=dimension_fields,
            select_fields=select_fields,
            conditions=get_conditions(filters),
            distributed_cost_center_query=distributed_cost_center_query,
            order_by_statement=order_by_statement,
        ),
        filters,
        as_dict=1,
        debug = 1
    )

    if filters.get("presentation_currency"):
        return convert_to_presentation_currency(gl_entries, currency_map, filters.get("company"))
    else:
        return gl_entries

def get_conditions(filters):
	conditions = []

	if filters.get("account"):
		filters.account = get_accounts_with_children(filters.account)
		conditions.append("account in %(account)s")

	if filters.get("cost_center"):
		filters.cost_center = get_cost_centers_with_children(filters.cost_center)
		conditions.append("cost_center in %(cost_center)s")

	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")

	if filters.get("group_by") == "Group by Party" and not filters.get("party_type"):
		conditions.append("party_type in ('Customer', 'Supplier')")

	if filters.get("party_type"):
		conditions.append("party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("party in %(party)s")

	if not (
		filters.get("account")
		or filters.get("party")
		or filters.get("group_by") in ["Group by Account", "Group by Party"]
	):
		conditions.append("(posting_date >=%(from_date)s or is_opening = 'Yes')")

	conditions.append("(posting_date <=%(to_date)s)")

	if filters.get("project"):
		conditions.append("project in %(project)s")

	if filters.get("finance_book"):
		if filters.get("include_default_book_entries"):
			conditions.append(
				"(finance_book in (%(finance_book)s, %(company_fb)s, '') OR finance_book IS NULL)"
			)
		else:
			conditions.append("finance_book in (%(finance_book)s)")

	if not filters.get("show_cancelled_entries"):
		conditions.append("is_cancelled = 0")

	from frappe.desk.reportview import build_match_conditions

	match_conditions = build_match_conditions("GL Entry")

	if match_conditions:
		conditions.append(match_conditions)

	if filters.get("include_dimensions"):
		accounting_dimensions = get_accounting_dimensions(as_list=False)

		if accounting_dimensions:
			for dimension in accounting_dimensions:
				if not dimension.disabled:
					if filters.get(dimension.fieldname):
						if frappe.get_cached_value("DocType", dimension.document_type, "is_tree"):
							filters[dimension.fieldname] = get_dimension_with_children(
								dimension.document_type, filters.get(dimension.fieldname)
							)
							conditions.append("{0} in %({0})s".format(dimension.fieldname))
						else:
							conditions.append("{0} in %({0})s".format(dimension.fieldname))

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_accounts_with_children(accounts):
	if not isinstance(accounts, list):
		accounts = [d.strip() for d in accounts.strip().split(",") if d]

	all_accounts = []
	for d in accounts:
		if frappe.db.exists("Account", d):
			lft, rgt = frappe.db.get_value("Account", d, ["lft", "rgt"])
			children = frappe.get_all("Account", filters={"lft": [">=", lft], "rgt": ["<=", rgt]})
			all_accounts += [c.name for c in children]
		else:
			frappe.throw(_("Account: {0} does not exist").format(d))

	return list(set(all_accounts))

def get_data_with_opening_closing(filters, account_details, accounting_dimensions, gl_entries):
	data = []

	gle_map = initialize_gle_map(gl_entries, filters)

	totals, entries = get_accountwise_gle(filters, accounting_dimensions, gl_entries, gle_map)

	# Opening for filtered account
	data.append(totals.opening)

	if filters.get("group_by") != "Group by Voucher (Consolidated)":
		for acc, acc_dict in iteritems(gle_map):
			# acc
			if acc_dict.entries:
				# opening
				data.append({})
				if filters.get("group_by") != "Group by Voucher":
					data.append(acc_dict.totals.opening)

				data += acc_dict.entries

				# totals
				data.append(acc_dict.totals.total)

				# closing
				if filters.get("group_by") != "Group by Voucher":
					data.append(acc_dict.totals.closing)
		data.append({})
	else:
		data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	return data

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			account="'{0}'".format(label),
			debit=0.0,
			credit=0.0,
			debit_in_account_currency=0.0,
			credit_in_account_currency=0.0,
		)

	return _dict(
		opening=_get_debit_credit_dict(TRANSLATIONS.OPENING),
		total=_get_debit_credit_dict(TRANSLATIONS.TOTAL),
		closing=_get_debit_credit_dict(TRANSLATIONS.CLOSING_TOTAL),
	)

def group_by_field(group_by):
	if group_by == "Group by Party":
		return "party"
	elif group_by in ["Group by Voucher (Consolidated)", "Group by Account"]:
		return "account"
	else:
		return "voucher_no"

def initialize_gle_map(gl_entries, filters):
	gle_map = OrderedDict()
	group_by = group_by_field(filters.get("group_by"))

	for gle in gl_entries:
		gle_map.setdefault(gle.get(group_by), _dict(totals=get_totals_dict(), entries=[]))
	return gle_map

def get_accountwise_gle(filters, accounting_dimensions, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []
	consolidated_gle = OrderedDict()
	group_by = group_by_field(filters.get("group_by"))
	group_by_voucher_consolidated = filters.get("group_by") == "Group by Voucher (Consolidated)"

	if filters.get("show_net_values_in_party_account"):
		account_type_map = get_account_type_map(filters.get("company"))

	def update_value_in_dict(data, key, gle):
		data[key].debit += gle.debit
		data[key].credit += gle.credit

		data[key].debit_in_account_currency += gle.debit_in_account_currency
		data[key].credit_in_account_currency += gle.credit_in_account_currency

		if filters.get("show_net_values_in_party_account") and account_type_map.get(
			data[key].account
		) in ("Receivable", "Payable"):
			net_value = data[key].debit - data[key].credit
			net_value_in_account_currency = (
				data[key].debit_in_account_currency - data[key].credit_in_account_currency
			)

			if net_value < 0:
				dr_or_cr = "credit"
				rev_dr_or_cr = "debit"
			else:
				dr_or_cr = "debit"
				rev_dr_or_cr = "credit"

			data[key][dr_or_cr] = abs(net_value)
			data[key][dr_or_cr + "_in_account_currency"] = abs(net_value_in_account_currency)
			data[key][rev_dr_or_cr] = 0
			data[key][rev_dr_or_cr + "_in_account_currency"] = 0

		if data[key].against_voucher and gle.against_voucher:
			data[key].against_voucher += ", " + gle.against_voucher

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	show_opening_entries = filters.get("show_opening_entries")

	for gle in gl_entries:
		group_by_value = gle.get(group_by)

		if gle.posting_date < from_date or (cstr(gle.is_opening) == "Yes" and not show_opening_entries):
			if not group_by_voucher_consolidated:
				update_value_in_dict(gle_map[group_by_value].totals, "opening", gle)
				update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)

			update_value_in_dict(totals, "opening", gle)
			update_value_in_dict(totals, "closing", gle)

		elif gle.posting_date <= to_date or (cstr(gle.is_opening) == "Yes" and show_opening_entries):
			if not group_by_voucher_consolidated:
				update_value_in_dict(gle_map[group_by_value].totals, "total", gle)
				update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)
				update_value_in_dict(totals, "total", gle)
				update_value_in_dict(totals, "closing", gle)

				gle_map[group_by_value].entries.append(gle)

			elif group_by_voucher_consolidated:
				keylist = [
					gle.get("voucher_type"),
					gle.get("voucher_no"),
					gle.get("account"),
					gle.get("party_type"),
					gle.get("party"),
				]
				if filters.get("include_dimensions"):
					for dim in accounting_dimensions:
						keylist.append(gle.get(dim))
					keylist.append(gle.get("cost_center"))

				key = tuple(keylist)
				if key not in consolidated_gle:
					consolidated_gle.setdefault(key, gle)
				else:
					update_value_in_dict(consolidated_gle, key, gle)

	for key, value in consolidated_gle.items():
		update_value_in_dict(totals, "total", value)
		update_value_in_dict(totals, "closing", value)
		entries.append(value)

	return totals, entries

def get_account_type_map(company):
	account_type_map = frappe._dict(
		frappe.get_all(
			"Account", fields=["name", "account_type"], filters={"company": company}, as_list=1
		)
	)

	return account_type_map

def get_result_as_list(data, filters):
	balance, balance_in_account_currency = 0, 0
	inv_details = get_supplier_invoice_details()

	for d in data:
		if not d.get("posting_date"):
			balance, balance_in_account_currency = 0, 0

		balance = get_balance(d, balance, "debit", "credit")
		d["balance"] = balance

		d["account_currency"] = filters.account_currency
		d["bill_no"] = inv_details.get(d.get("against_voucher"), "")

	return data

def get_supplier_invoice_details():
	inv_details = {}
	for d in frappe.db.sql(
		""" select name, bill_no from `tabPurchase Invoice`
		where docstatus = 1 and bill_no is not null and bill_no != '' """,
		as_dict=1,
	):
		inv_details[d.name] = d.bill_no

	return inv_details

def get_balance(row, balance, debit_field, credit_field):
	balance += row.get(debit_field, 0) - row.get(credit_field, 0)

	return balance

# custom method to split tax entries
@frappe.whitelist()
def split_entries_as_per_cc(doc):
	doc = json.loads(doc)
	references_details = doc['references_details']
	taxes = doc['taxes']
	splitted_rows = []
	for rd in references_details:
		for t in taxes:
			entered_amt = t['tax_amount']
			t['cost_center'] = rd['custom_cost_center']
			t['tax_amount'] = (((rd['amount']/doc['paid_amount'])*100) * entered_amt)/100
			splitted_rows.append(t)
	doc['taxes'] = splitted_rows
	return doc

# custom method to fetch reference item details cc wise and separately ref document wise
@frappe.whitelist()
def fetch_detailed_entries(doc):
	ref_details = []
	bifurcated_cost_center = []
	std_cost_center = []
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_item_reference_details
	doc = json.loads(doc)
	try:
		references_details = doc['references_details']
	except:
		references_details = []

	print(doc['references'])
	references = doc['references']
	for ref in references:
		if ref.get('reference_doctype') == 'Employee Advance':

			cc = doc.get('cost_center')
			bifurcated_cc = 1
			ref_details.append([{'reference_doctype':ref.get('reference_doctype'),'reference_name':ref.get('reference_name'),'custom_cost_center':cc,'amount':ref.get('total_amount'),'outstanding':ref.get('outstanding_amount'),'allocated_amount':ref.get('allocated_amount')}])
			# print('\n\n\n\n\n\n>>>>>>>>>>qqqref_details',ref_details,bifurcated_cc)

			# return ref_details,bifurcated_cc

		elif ref.get('reference_doctype') == 'Expense Claim':

			cc = doc.get('cost_center')
			bifurcated_cc = 1
			ref_details.append([{'reference_doctype':ref.get('reference_doctype'),'reference_name':ref.get('reference_name'),'custom_cost_center':cc,'amount':ref.get('total_amount'),'outstanding':ref.get('outstanding_amount'),'allocated_amount':ref.get('allocated_amount')}])


			# return ref_details,bifurcated_cc


		else:

			data, bifurcate_cost_center = get_item_reference_details(ref.get('reference_doctype'),ref.get('reference_name'))

			print(data, "------------data")
			print(bifurcate_cost_center, "--------------bcc")
			ref_details.append(data)
			if bifurcate_cost_center == 1:
				bifurcated_cost_center.append(bifurcate_cost_center)
			else:
				std_cost_center.append(bifurcate_cost_center)
	
			if len(bifurcated_cost_center)>0 and len(std_cost_center)>0:
				frappe.throw(_("Standard and bifurcated_cost_center invoices payment entry cannot be clubbed together"))
			elif len(bifurcated_cost_center)>0 and len(std_cost_center)==0:
				bifurcated_cc = 1
			elif len(bifurcated_cost_center)==0 and len(std_cost_center)>0:	
				bifurcated_cc = 0
			ref_details = allocate_paid_amount(doc,ref_details)

	return ref_details,bifurcated_cc
		


# custom method for allocating paid amount on payment entry
@frappe.whitelist()
def allocate_paid_amount(doc,ref_details):
	paid_amount = doc.get('paid_amount')
	references = doc.get('references')
	
	print(ref_details)
	print("ref_details")
	for ref in ref_details:
		for i in ref:
			print(i,"---")
			i['outstanding'] = i['amount'] or 0
			part_payments = frappe.db.sql("""
							select
								sum(per.allocated_amount)
							from
								`tabPayment Entry Reference Item` per
							join
								`tabPayment Entry` pe
							on
								pe.name = per.parent
							where
								per.reference_name = '{0}'
								and per.custom_cost_center = '{1}'
								and pe.docstatus = 1
								and pe.name != '{2}'
							""".format(i['reference_name'].replace("'","''"), i['custom_cost_center'],doc['name']))
			# if part_payments and part_payments[0][0] != None:
			# 	if i['amount'] == part_payments[0][0]:
			# 		i['allocated_amount'] = 0
			# 		i['outstanding'] = i['amount'] - i['allocated_amount']
			# 		paid_amount -= 0
			# 	else:
			# 		i['allocated_amount'] = paid_amount
			# 		i['outstanding'] = i['amount'] - i['allocated_amount']
			# 		paid_amount -= i['allocated_amount']
			# else:
			# 	if paid_amount > i['amount']:
			# 		i['allocated_amount'] = i['amount']
			# 		i['outstanding'] = i['amount'] - i['allocated_amount']
			# 		paid_amount -= i['amount']
			# 	else:
			# 		i['allocated_amount'] = paid_amount
			# 		i['outstanding'] = i['amount'] - i['allocated_amount']
			# 		paid_amount -= i['allocated_amount']

			if part_payments and part_payments[0][0] != None:
				i['outstanding'] = i['amount'] - part_payments[0][0]
			elif part_payments and part_payments[0][0] == None:
				i['outstanding'] = i['amount']
			else:
				i['outstanding'] = i['amount'] or 0

			# allocated_amt = 0
			# for re1 in references:
			# 	allocated_amt += re1["allocated_amount"]

			for re in references:
				allocated_amt = re["allocated_amount"] if re["allocated_amount"] else 0
				for update_i in ref:
					print(update_i, "-----------")
					if update_i['reference_name'] == re['reference_name'] and update_i['custom_cost_center']:
						# print(ref['outstanding'])
						# print("-----------")
						# print(allocated_amt)
						if allocated_amt > update_i["amount"]:
							update_i['allocated_amount'] = update_i["amount"]
							allocated_amt = allocated_amt - update_i["amount"]
						else:
							update_i['allocated_amount'] = allocated_amt
							allocated_amt = 0
			# for re in references:
			# 	for update_i in ref:
			# 		# print(update_i['reference_name'])
			# 		# print(update_i['custom_cost_center'])
			# 		# print('---------------')
			# 		if update_i['reference_name'] == re['reference_name'] and update_i['custom_cost_center']:
			# 			print(re['allocated_amount'])
			# 			print(paid_amount)
			# 			print("----------")
			# 			if paid_amount >= re['allocated_amount']:
			# 				print("--------------")
			# 				update_i['allocated_amount'] = i['amount']
			# 				paid_amount = paid_amount - i['amount']
			# 			else:
			# 				update_i['allocated_amount'] = paid_amount
			# 				paid_amount = 0

		# if paid_amount > ref_details[ref]['amount']:
		# 	ref_details[0][ref]['allocated_amount'] = ref_details[0][ref]['amount']
		# 	paid_amount -= ref_details[ref]['amount']
		# else:
		# 	ref_details[ref]['allocated_amount'] = paid_amount
		# 	break
	print(ref_details)
	return ref_details

@frappe.whitelist()
def get_cc_deductions(doc):
	doc = json.loads(doc)
	account = frappe.db.get_value("Company", doc.get('company'), 'exchange_gain_loss_account')
	
	cost_center_ = []
	for i in doc.get('references_details'):
		cost_center_.append({i.get('custom_cost_center'): i.get('allocated_amount')})
	
	max_value_cost_center = max(cost_center_[0], key=cost_center_[0].get)
	
	payment_deductions_dict = []
	amount = doc.get('difference_amount')
	diff_amount = 0
	for i in doc.get('references_details'):
		if i.get('custom_cost_center') ==  max_value_cost_center:
			payment_deductions_dict.append({'account': account, 'cost_center': i.get('custom_cost_center'), 'amount': amount})
		else:
			payment_deductions_dict.append({'account': account, 'cost_center': i.get('custom_cost_center'), 'amount': diff_amount})
	return payment_deductions_dict

def validate_outstanding_amount(doc, method):
	for i in doc.references_details:
		outstanding_amount = frappe.db.sql("""
								select
									per.amount, sum(per.allocated_amount)
								from
									`tabPayment Entry Reference Item` per
								join
									`tabPayment Entry` pe
								on
									pe.name = per.parent
								where
									per.reference_name = '{}'
									and per.custom_cost_center = '{}'
									and pe.party = '{}'
									and pe.docstatus != 2
							""".format(i.reference_name.replace("'","''"), i.custom_cost_center, doc.party))
		if outstanding_amount and (outstanding_amount[0][0] != None and outstanding_amount[0][1] != None):
			i.outstanding = outstanding_amount[0][0] - outstanding_amount[0][1]

