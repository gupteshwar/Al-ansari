# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

from al_ansari.al_ansari.report.accounts_receivable_summary___al_ansari.accounts_receivable_summary___al_ansari import AccountsReceivableSummary


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return AccountsReceivableSummary(filters).run(args)
