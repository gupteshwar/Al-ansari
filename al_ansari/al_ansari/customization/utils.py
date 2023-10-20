import frappe
import json
from frappe import _
from erpnext.setup.utils import get_exchange_rate


def validate(doc,method):
    validate_exchange_rate(doc,method)  

def validate_exchange_rate(doc,method):
    if doc.currency != "OMR":

        company_currency = frappe.db.get_value(
			"Company", filters={"name": doc.company}, fieldname=["default_currency"]
		)

        if doc.doctype == "Sales Order" or doc.doctype == "Purchase Order":
            transaction_date = doc.transaction_date

        if doc.doctype == "Sales Invoice" or doc.doctype == "Purchase Invoice":
            transaction_date = doc.posting_date

        if doc.doctype == "Sales Order" or doc.doctype == "Sales Invoice":
            args = "for_selling"

        if doc.doctype == "Purchase Order" or doc.doctype == "Purchase Invoice":
            args = "for_buying"
 
        conversion_rate = get_exchange_rate(doc.currency, company_currency,transaction_date,args)
  
        currency_tolerance = frappe.db.get_value("Currency",filters = {"name":doc.currency}, fieldname = ["tolerance"])  #get tolerance value from currency

        tolerance_value = conversion_rate * (int(currency_tolerance)/100)

        min_conversion_rate = conversion_rate - tolerance_value 

        max_conversion_rate = conversion_rate + tolerance_value

        if doc.conversion_rate < min_conversion_rate or doc.conversion_rate > max_conversion_rate:
            frappe.throw(f"Invalid exchange rate. The exchange rate should be within {min_conversion_rate} and {max_conversion_rate}."
                         " Please adjust the exchange rate.")

@frappe.whitelist()
def fetch_cr_dr_details(doc):
    doc = json.loads(doc)
    cc_accounting_entries = []
    cost_centers = []
    for i in doc.get('accounts'):
        if i.get('cost_center') not in cost_centers:
            cost_centers.append(i.get('cost_center'))
    
    for cc in cost_centers:
        debit = 0
        credit = 0
        for i in doc.get('accounts'):
            if i.get('cost_center') == cc:
                debit += i.get('debit')
                credit += i.get('credit')
        cc_accounting_entries.append({'cost_center': cc, 'debit': debit, 'credit': credit})
    
    return cc_accounting_entries

def validate_total_debit_and_credit_against_cc(doc, method):
    if doc.cc_accounting_entries:
        for i in doc.cc_accounting_entries:
            if i.total_difference:
                frappe.throw(
				    _("Total Debit must be equal to Total Credit for Cost Center {1}. The difference is {0}").format(i.difference, i.cost_center)
			    )   