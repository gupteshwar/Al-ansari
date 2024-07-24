frappe.ui.form.on("Payment Entry", {
    get_ledger: function (frm) {
        if (frm.doc.party_type == 'Supplier' && frm.doc.party) {
            var d = new frappe.ui.Dialog({
                title: __('Get Ledger based on filters'),
                fields: [
                    {
                        "label": "From Date",
                        "fieldname": "from_date",
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today()
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
                        "fieldtype": "Date",
                        "default": frappe.datetime.add_days(frappe.datetime.get_today(), 1)
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
                primary_action_label: __('Fetch Entries'),
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
    refresh:function(frm, cdt, cdn) {
        if(frm.doc.docstatus == 0) {
            frm.add_custom_button(__('Get Detailed Entries'), function(){ 
                fetch_detailed_entries(frm)     
            })
          
        }
        frm.add_custom_button(__('PO FIX'), function(){ 
            frm.doc.references.forEach(function(row){
                if (row.reference_name && row.reference_doctype) {
                    return frappe.call({
                        method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_reference_details",
                        args: {
                            reference_doctype: row.reference_doctype,
                            reference_name: row.reference_name,
                            party_account_currency: frm.doc.payment_type=="Receive" ?
                                frm.doc.paid_from_account_currency : frm.doc.paid_to_account_currency
                        },
                        callback: function(r, rt) {
                            if(r.message) {
                                console.log(r.message.outstanding_amount)
                                row.outstanding_amount = r.message.outstanding_amount
                                row.exchange_rate = r.message.exchange_rate
                             
                                frm.refresh_field("outstanding_amount");
                                frm.refresh_field("exchange_rate");

                                 frm.refresh_field('references')
                            }
                        }
                    })
                }
            })
            
            
        })
        frm.set_df_property('references_details','cannot_add_rows',true)
        frm.set_df_property('references_details','cannot_delete_rows',true)

        cur_frm.refresh_field('references_details')

        // if (cur_frm.doc.bifurcate_cost_center == 1 && frm.doc.references_details.length>0) {
        //     frm.add_custom_button(__('Split Deductions'), function(){
        //         if(frm.doc.deductions.length > 0){
        //             // var splitted_records_deductions = split_entries_as_per_cc(frm,frm.doc.deductions,frm.doc.references_details)
        //             // console.log("splitted_records_deductions>>>>>",splitted_records_deductions)
        //             // frappe.call({
        //             //     method: "al_ansari.al_ansari.customization.payment_entry.get_general_ledger_data",
        //             //     args: {
        //             //         filters: data
        //             //     },
        //             //     callback: function (r) {
        //             //         console.log(r.message)
        //             //         // d.fields_dict.msg_wrapper.$wrapper.append(r.message);
        //             //     },
        //             // });

        //         } else {
        //             frappe.throw(__("No Deductions found"))
        //         }  
        //     }, __("Split"));
            
        //     frm.add_custom_button(__('Split Taxes'), function(){
        //         if(frm.doc.taxes.length > 0){
        //             var splitted_records_taxes = split_entries_as_per_cc(frm,frm.doc.taxes,frm.doc.references_details)
        //             // console.log("splitted_records_taxes>>>>>",JSON.stringify(splitted_records_taxes))
        //             // frm.doc.taxes = splitted_records_taxes
        //             // frm.refresh_field('taxes')
        //             // frappe.call({
        //             //     method: "al_ansari.al_ansari.customization.payment_entry.split_entries_as_per_cc",
        //             //     args: {
        //             //         doc: frm.doc
        //             //     },
        //             //     callback: function (r) {
        //             //         console.log(r.message.taxes)
        //             //         // d.fields_dict.msg_wrapper.$wrapper.append(r.message);
        //             //     },
        //             // });
        //             console.log("Doneksaaa")
        //         } else {
        //             frappe.throw(__("No taxes found"))
        //         }         
        //     }, __("Split"));   
        // }
    },
    // Commented the auto fill of payroll cost center

    // onload: function(frm) {
    //     if (frappe.session.user) {
    //         frappe.call({
    //             method: 'frappe.client.get_value',
    //             args: {
    //                 doctype: 'Employee',
    //                 filters: {
    //                     user_id: frappe.session.user
    //                 },
    //                 fieldname: 'payroll_cost_center'
    //             },
    //             callback: function(response) {
    //                 if (response.message) {

    //                     if(frm.doc.__islocal && !frm.doc.cost_center){
    //                         frm.set_value('cost_center', response.message.payroll_cost_center);
    //                     }
    //                     else if(!frm.doc.cost_center){
    //                         frm.set_value('cost_center', response.message.payroll_cost_center);
    //                         // frm.save()
    //                     }
    //                 }
    //             }
    //         });
    //     }
    // },
    // paid_amount: function(frm) {
    //     frm.trigger('fetch_detailed_entries')
    // },
    onload: function(frm) {
        frm.set_df_property('references_details','cannot_add_rows',true)
        frm.set_df_property('references_details','cannot_delete_rows',true)
        cur_frm.refresh_field('references_details')
    },
    paid_amount: function(frm) {
        if (cur_frm.doc.references && cur_frm.doc.references.length >0 && frm.doc.bifurcate_cost_center ==1){
            frm.clear_table('references_details')
            frm.refresh_field('references_details')

            if (cur_frm.doc.references.length > 0){

                fetch_detailed_entries(frm)
            }
        }
    },
    validate: function(frm) {
        if (cur_frm.doc.references && cur_frm.doc.references.length >0 && frm.doc.bifurcate_cost_center ==1){
            var r_total_amt = 0
            cur_frm.doc.references.forEach(function (r) {
                if(r.allocated_amount == 0) {
                    frappe.throw("Please allocate some amount in the references table as allocated amount cannot be zero")
                }
                r_total_amt += r.allocated_amount 
            })

            // frm.set_value('paid_amount',r_total_amt)

        }
        
        if (cur_frm.doc.references && cur_frm.doc.references.length >0 && frm.doc.bifurcate_cost_center ==1){
            var rs_issue =[]
            cur_frm.doc.references.forEach(function (rs) {
                console.log("11111111111.........", rs.allocated_amount)
                console.log("22222222222.........", rs.outstanding_amount)
                if ((rs.allocated_amount > rs.outstanding_amount.toFixed(3)) || (rs.allocated_amount<0) ){
                    rs_issue.push(rs.idx)
                }
            })

            console.log("rs_issue....................", rs_issue)
            if (rs_issue.length >0){
                    frappe.throw(__("The following records in reference table has issue with allocated amount {0}",[rs_issue]))
                }
        }


        if (cur_frm.doc.references_details && cur_frm.doc.references_details.length >0 && frm.doc.bifurcate_cost_center ==1){
            var rd_issue =[]
            cur_frm.doc.references_details.forEach(function (rd) {
                console.log("----------1", rd.allocated_amount)
                console.log("----------2", rd.outstanding)
                console.log("----------3", (rd.allocated_amount > rd.outstanding))
                console.log("----------4", (rd.allocated_amount<0))

                if ((rd.allocated_amount > rd.outstanding) || (rd.allocated_amount<0) ){
                    rd_issue.push(rd.idx)
                }
            })
            console.log(rd_issue)
            if (rd_issue.length >0){
                    frappe.throw(__("The following records in reference details table has issue with allocated amount {0}",[rd_issue]))
                }
        }

    },
    target_exchange_rate: function(frm){
        if(frm.doc.paid_from_account_currency != frm.doc.paid_to_account_currency){
            frm.doc.paid_amount = frm.doc.received_amount * frm.doc.target_exchange_rate
            frm.refresh_field('paid_amount')
        }
    }
});

function split_entries_as_per_cc(frm,taxes,references_details) {
    var splitted_records = []
    var counter = 0
    // taxes.forEach(function (row) {
    //     references_details.forEach(function(ref_row){
    //         counter += counter
    //         // var cost_center = ref_row.custom_cost_center
    //         // // var entered_amt = row.tax_amount
    //         // row['cost_center'] = cost_center
    //         // row['tax_amount'] = ref_row.amount //(((ref_row.amount/frm.doc.paid_amount)*100) *entered_amt)/100
    //         row.cost_center = ref_row.custom_cost_center
    //         row.cost_center = ref_row.amount
    //         row.idx = counter
    //         splitted_records.push(row)            
    //     })
    // })
    var original_taxes = taxes
    frm.clear_table('taxes')
    frm.refresh_field('taxes')
    for(var i=0;i<original_taxes.length;i++){
        for(var j=0; j<references_details.length; j++) {

            var childTable = cur_frm.add_child("taxes");
            childTable.charge_type = original_taxes[i]['charge_type']
            childTable.tax_amount=references_details[j]['amount']
            childTable.cost_center=references_details[j]['custom_cost_center']
            childTable.rate=original_taxes[i]['rate']
            childTable.account_head=original_taxes[i]['account_head']

            cur_frm.refresh_fields("taxes");

        }

    }
}


function fetch_detailed_entries(frm) {
    if(frm.doc.references) {
        // calculate_and_set_paid_amount(frm)
        // frm.doc.references.forEach(function (ref) {
            frappe.call({
                method: "al_ansari.al_ansari.customization.payment_entry.fetch_detailed_entries",
                args: {
                    doc: frm.doc
                },
                callback: function (r) {
                    // frm.clear_table('references_details')
                    if(r.message[0]) {
                        console.log(r.message[0])
                        frm.doc.references_details = []
                        r.message[0].forEach(function(row){
                            row.forEach(function(r) {
                                console.log(r)
                                var childTable = cur_frm.add_child("references_details");
                                childTable.custom_cost_center = r.custom_cost_center
                                childTable.amount = r.amount
                                childTable.outstanding = r.outstanding
                                childTable.reference_doctype = r.reference_doctype
                                childTable.reference_name = r.reference_name
                                childTable.allocated_amount = r.allocated_amount || 0
                                childTable.exchange_rate = r.exchange_rate
                            })
                            // var childTable = cur_frm.add_child("references_details");
                            // childTable.custom_cost_center = row.custom_cost_center
                            // childTable.amount = row.amount
                            // childTable.reference_doctype = row.reference_doctype
                            // childTable.reference_name = row.reference_name
                            // childTable.allocated_amount = row.allocated_amount || 0
                        })
                        cur_frm.refresh_fields("references_details");
                    }
                   
                    frm.set_value('bifurcate_cost_center',r.message[1])
                },
            });
        // })
    }
}


frappe.ui.form.on("Payment Entry Reference", {
    references_remove: function(frm,cdt,cdn) {
        frm.clear_table('references_details')
        frm.refresh_field('references_details')
    },
    allocated_amount: function(frm,cdt,cdn){
        let row = locals[cdt][cdn]
        if (row.allocated_amount>row.outstanding_amount){
            // row.allocated_amount = 0
            frappe.throw("Allocated Amount should not exceed outstanding amount in References table")
        }

        // calculate_and_set_paid_amount(frm)

    },
    reference_name: function (frm,cdt,cdn) {
        fetch_detailed_entries(frm)
    }
})

            
function calculate_and_set_paid_amount(frm){
    var paid_amount = 0
    frm.doc.references.forEach(function(r){
        paid_amount += r.allocated_amount
    })

    frm.set_value('paid_amount',paid_amount)
    fetch_detailed_entries(frm)

} 

frappe.ui.form.on("Payment Entry Reference Item", {
    
    allocated_amount: function(frm,cdt,cdn){
        let row = locals[cdt][cdn]
        if (row.allocated_amount>row.outstanding){
            // row.allocated_amount = 0
            frappe.throw("Allocated Amount should not exceed outstanding amount in the References Details table")
        }
        if (row.allocated_amount<0){
            // row.allocated_amount = 0
            frappe.throw("Allocated Amount should not be negative in the References Details table")
        }
        // calculate_and_set_paid_amount(frm)
    }
})