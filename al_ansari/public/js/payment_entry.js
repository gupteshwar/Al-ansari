frappe.ui.form.on("Payment Entry", {
    party: function (frm) {
        if (frm.doc.party_type == 'Supplier' && frm.doc.party) {
            var d = new frappe.ui.Dialog({
                title: __('Get Ledger based on filters'),
                fields: [
                    {
                        "label": "From Date",
                        "fieldname": "from_date",
                        "fieldtype": "Date"
                    },
                    {
                        "fieldname":"party_type",
                        "label": __("Party Type"),
                        "fieldtype": "Link",
                        "options": "Party Type",
                        "default": "Supplier",
                        on_change: function() {
                            frappe.query_report.set_filter_value('party', "");
                        }
                    },
                    {
                        "fieldname": "col_break",
                        "fieldtype": "Column Break",
                    },
                    {
                        "label": "To Date",
                        "fieldname": "to_date",
                        "fieldtype": "Date"
                    },
                    {
                        "fieldname":"party",
                        "label": __("Party"),
                        "fieldtype": "Dynamic Link",
                        "options": "party_type",
                        "default": frm.doc.party
                    },
                    {
                        "fieldtype": "Section Break",
                        "fieldname": "sec_break"
                    },
                    {
                        'fieldname': 'msg_wrapper',
                        'fieldtype': 'HTML'
                    }
                ],
                primary_action_label: __('Get Ledger'),
			    primary_action: () => {
                        var data = d.get_values();
                        data.company = frm.doc.company
                        console.log(data)
                        frappe.call({
                            method: "al_ansari.al_ansari.customization.payment_entry.get_general_ledger_data",
                            args: {
                                filters: data
                            },
                            callback: function (r) {
                                console.log(r.message)
                                d.fields_dict.msg_wrapper.$wrapper.append(r.message);
                            },
                        });
                    },
                });
                d.show();
        }     
    },

    onload: function(frm) {
        if (frappe.session.user) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: {
                        user_id: frappe.session.user
                    },
                    fieldname: 'payroll_cost_center'
                },
                callback: function(response) {
                    if (response.message) {

                        if(frm.doc.__islocal && !frm.doc.cost_center){
                            frm.set_value('cost_center', response.message.payroll_cost_center);
                        }
                        else if(!frm.doc.cost_center){
                            frm.set_value('cost_center', response.message.payroll_cost_center);
                            // frm.save()
                        }
                    }
                }
            });
        }
    }
});