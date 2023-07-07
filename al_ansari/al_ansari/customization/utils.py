import frappe
import json
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