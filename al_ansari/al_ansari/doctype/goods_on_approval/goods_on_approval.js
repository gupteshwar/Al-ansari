// Copyright (c) 2023, Indictrans and contributors
// For license information, please see license.txt

frappe.provide("erpnext.stock");
frappe.provide("erpnext.accounts.dimensions");

frappe.ui.form.on('Goods On Approval', {
	setup: function(frm) {
		frm.set_indicator_formatter('item_code', function(doc) {
			// if (!doc.s_warehouse) {
			// 	return 'blue';
			// } else {
			// 	return (doc.qty<=doc.actual_qty) ? 'green' : 'orange';
			// }
			// Pending
			if ((doc.goods_on_approval_count == doc.goods_received_count) && (doc.goods_on_approval_count == 0)){
				return 'grey'
			} else if ((doc.goods_on_approval_count == doc.goods_received_count) && (doc.goods_on_approval_count!=0) && (doc.goods_on_approval_count != doc.qty)){
				return 'blue'
			}  else if ((doc.goods_on_approval_count > doc.goods_received_count) && (doc.goods_on_approval_count != doc.qty)){
				return 'orange'
			} else if ((doc.goods_on_approval_count > doc.goods_received_count) && (doc.goods_on_approval_count == doc.qty)){
				return 'pink'
			} else if ((doc.goods_on_approval_count == doc.goods_received_count) && (doc.goods_on_approval_count == doc.qty)){
				return 'green'
			}

		});
	},
	refresh: function(frm) {
		frm.set_indicator_formatter('item_code', function(doc) {
			// if (!doc.s_warehouse) {
			// 	return 'blue';
			// } else {
			// 	return (doc.qty<=doc.actual_qty) ? 'green' : 'orange';
			// }
			// Pending
			if ((doc.goods_on_approval_count == doc.goods_received_count) && (doc.goods_on_approval_count == 0)){
				return 'white'
			} else if ((doc.goods_on_approval_count == doc.goods_received_count) && (doc.goods_on_approval_count!=0) && (doc.goods_on_approval_count != doc.qty)){
				return 'blue'
			}  else if ((doc.goods_on_approval_count > doc.goods_received_count) && (doc.goods_on_approval_count != doc.qty)){
				return 'orange'
			} else if ((doc.goods_on_approval_count > doc.goods_received_count) && (doc.goods_on_approval_count == doc.qty)){
				return 'yellow'
			} else if ((doc.goods_on_approval_count == doc.goods_received_count) && (doc.goods_on_approval_count == doc.qty)){
				return 'green'
			}

		});
		frm.set_query("cost_center", function() {
					return {
						filters: {"company": frm.doc.company}
					};
				});
		frm.set_query("s_warehouse", "stock_entry_detail", function() {
		    return {
		        query: "erpnext.controllers.queries.warehouse_query",
		        filters: {
		        	"is_group": 0,
		        	"company": frm.doc.company,
		    			}
		    };
		});

		frm.set_query("t_warehouse", "stock_entry_detail", function() {
		    return {
		        query: "erpnext.controllers.queries.warehouse_query",
		        filters: {
		        	"is_group": 0,
		        	"company": frm.doc.company,
		    			}
		    };
		});

		if(!frm.is_new()){
			frm.add_custom_button(__("Goods on Approval"), function() { 

				frappe.model.with_doctype('Stock Entry', function() {
				var se = frappe.model.get_new_doc('Stock Entry')
				se.stock_entry_type = "Goods on Approval"
				se.company = frm.doc.company
				se.goods_on_approval_ref = frm.doc.name
				frm.doc.stock_entry_detail.forEach(function(item) {
					if (item.qty - item.goods_on_approval_count >0) {
						var mr_item = frappe.model.add_child(se,'items');
						mr_item.item_code = item.item_code;
						mr_item.item_name = item.item_name;
						mr_item.uom = item.uom;
						mr_item.stock_uom = item.stock_uom;
						mr_item.conversion_factor = item.conversion_factor;
						mr_item.item_group = item.item_group;
						mr_item.description = item.description;
						mr_item.image = item.image;
						mr_item.qty = item.qty - item.goods_on_approval_count;
						mr_item.s_warehouse = item.s_warehouse;
						mr_item.t_warehouse = item.t_warehouse;
						mr_item.required_date = frappe.datetime.nowdate();
						mr_item.basic_rate = item.basic_rate;
						mr_item.transfer_qty = item.transfer_qty;
					}
				})
				frappe.set_route('Form', 'Stock Entry', se.name);
			});
			}, __("Create"));
			frm.add_custom_button(__("Goods Return Entry"), function() { 
					frappe.model.with_doctype('Stock Entry', function() {
					var se = frappe.model.get_new_doc('Stock Entry')
					se.stock_entry_type = "Goods Return Entry"
					se.company = frm.doc.company
					se.goods_on_approval_ref = frm.doc.name
					frm.doc.stock_entry_detail.forEach(function(item) {
						if (item.qty - item.goods_received_count > 0){
							var mr_item = frappe.model.add_child(se,'items');
							mr_item.item_code = item.item_code;
							mr_item.item_name = item.item_name;
							mr_item.uom = item.uom;
							mr_item.stock_uom = item.stock_uom;
							mr_item.conversion_factor = item.conversion_factor;
							mr_item.item_group = item.item_group;
							mr_item.description = item.description;
							mr_item.image = item.image;
							mr_item.qty = item.qty - item.goods_received_count;
							mr_item.s_warehouse = item.s_warehouse;
							mr_item.t_warehouse = item.t_warehouse;
							mr_item.required_date = frappe.datetime.nowdate();
							mr_item.basic_rate = item.basic_rate;
							mr_item.transfer_qty = item.transfer_qty;
						}
					})
					frappe.set_route('Form', 'Stock Entry', se.name);
				});
			}, __("Create"));
		}
	},
	set_basic_rate: function(frm, cdt, cdn) {
		const item = locals[cdt][cdn];
		item.transfer_qty = flt(item.qty) * flt(item.conversion_factor);

		const args = {
			'item_code'			: item.item_code,
			'posting_date'		: frm.doc.posting_date,
			'posting_time'		: frm.doc.posting_time,
			'warehouse'			: cstr(item.s_warehouse) || cstr(item.t_warehouse),
			'serial_no'			: item.serial_no,
			'company'			: frm.doc.company,
			'qty'				: item.s_warehouse ? -1*flt(item.transfer_qty) : flt(item.transfer_qty),
			'voucher_type'		: frm.doc.doctype,
			'voucher_no'		: item.name,
			'allow_zero_valuation': 1,
		};
		if (item.item_code || item.serial_no) {
			frappe.call({
				method: "erpnext.stock.utils.get_incoming_rate",
				args: {
					args: args
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, 'basic_rate', (r.message || 0.0));
					frm.events.calculate_basic_amount(frm, item);
				}
			});
		}
	},

	get_warehouse_details: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if(!child.bom_no) {
			frappe.call({
				method: "erpnext.stock.doctype.stock_entry.stock_entry.get_warehouse_details",
				args: {
					"args": {
						'item_code': child.item_code,
						'warehouse': cstr(child.s_warehouse) || cstr(child.t_warehouse),
						'transfer_qty': child.transfer_qty,
						'serial_no': child.serial_no,
						'qty': child.s_warehouse ? -1* child.transfer_qty : child.transfer_qty,
						'posting_date': frm.doc.posting_date,
						'posting_time': frm.doc.posting_time,
						'company': frm.doc.company,
						'voucher_type': frm.doc.doctype,
						'voucher_no': child.name,
						'allow_zero_valuation': 1
					}
				},
				callback: function(r) {
					if (!r.exc) {
						["actual_qty", "basic_rate"].forEach((field) => {
							frappe.model.set_value(cdt, cdn, field, (r.message[field] || 0.0));
						});
						frm.events.calculate_basic_amount(frm, child);
					}
				}
			});
		}
	},

	cost_center: function(frm, cdt, cdn) {
		erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "cost_center");
	},
	set_serial_no: function(frm, cdt, cdn, callback) {
		var d = frappe.model.get_doc(cdt, cdn);
		if(!d.item_code && !d.s_warehouse && !d.qty) return;
		var	args = {
			'item_code'	: d.item_code,
			'warehouse'	: cstr(d.s_warehouse),
			'stock_qty'		: d.transfer_qty
		};
		frappe.call({
			method: "erpnext.stock.get_item_details.get_serial_no",
			args: {"args": args},
			callback: function(r) {
				if (!r.exe && r.message){
					frappe.model.set_value(cdt, cdn, "serial_no", r.message);
				}
				if (callback) {
					callback();
				}
			}
		});
	},
	calculate_basic_amount: function(frm, item) {
		item.basic_amount = flt(flt(item.transfer_qty) * flt(item.basic_rate),
			precision("basic_amount", item));
		// frm.events.calculate_total_additional_costs(frm);
	},

	calculate_total_additional_costs: function(frm) {
		const total_additional_costs = frappe.utils.sum(
			(frm.doc.additional_costs || []).map(function(c) { return flt(c.base_amount); })
		);

		frm.set_value("total_additional_costs",
			flt(total_additional_costs, precision("total_additional_costs")));
	},
});


frappe.ui.form.on('Stock Entry Detail', {
	qty: function(frm, cdt, cdn) {
		frm.events.set_serial_no(frm, cdt, cdn, () => {
			frm.events.set_basic_rate(frm, cdt, cdn);
		});
	},

	conversion_factor: function(frm, cdt, cdn) {
		frm.events.set_basic_rate(frm, cdt, cdn);
	},

	s_warehouse: function(frm, cdt, cdn) {
		frm.events.set_serial_no(frm, cdt, cdn, () => {
			// frm.events.get_warehouse_details(frm, cdt, cdn);
		});

		// set allow_zero_valuation_rate to 0 if s_warehouse is selected.
		let item = frappe.get_doc(cdt, cdn);
		if (item.s_warehouse) {
			frappe.model.set_value(cdt, cdn, "allow_zero_valuation_rate", 0);
		}
	},

	t_warehouse: function(frm, cdt, cdn) {
		// frm.events.get_warehouse_details(frm, cdt, cdn);
	},

	basic_rate: function(frm, cdt, cdn) {
		var item = locals[cdt][cdn];
		frm.events.calculate_basic_amount(frm, item);
	},
	
	barcode: function(doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.barcode) {
			frappe.call({
				method: "erpnext.stock.get_item_details.get_item_code",
				args: {"barcode": d.barcode },
				callback: function(r) {
					if (!r.exe){
						frappe.model.set_value(cdt, cdn, "item_code", r.message);
					}
				}
			});
		}
	},

	uom: function(doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.uom && d.item_code){
			return frappe.call({
				method: "erpnext.stock.doctype.stock_entry.stock_entry.get_uom_details",
				args: {
					item_code: d.item_code,
					uom: d.uom,
					qty: d.qty
				},
				callback: function(r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			});
		}
	},

	item_code: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.item_code) {
			var args = {
				'item_code'			: d.item_code,
				'warehouse'			: cstr(d.s_warehouse) || cstr(d.t_warehouse),
				'transfer_qty'		: d.transfer_qty,
				'serial_no'		: d.serial_no,
				'bom_no'		: d.bom_no,
				'expense_account'	: d.expense_account,
				'cost_center'		: d.cost_center,
				'company'		: frm.doc.company,
				'qty'			: d.qty,
				'voucher_type'		: frm.doc.doctype,
				'voucher_no'		: d.name,
				'allow_zero_valuation': 1,
			};

			return frappe.call({
				doc: frm.doc,
				method: "get_item_details",
				args: args,
				callback: function(r) {
					if(r.message) {
						var d = locals[cdt][cdn];
						$.each(r.message, function(k, v) {
							if (v) {
								frappe.model.set_value(cdt, cdn, k, v); // qty and it's subsequent fields weren't triggered
							}
						});
						refresh_field("stock_entry_detail");

						let no_batch_serial_number_value = !d.serial_no;
						if (d.has_batch_no && !d.has_serial_no) {
							// check only batch_no for batched item
							no_batch_serial_number_value = !d.batch_no;
						}

						if (no_batch_serial_number_value && !frappe.flags.hide_serial_batch_dialog) {
							erpnext.stock.select_batch_and_serial_no(frm, d);
						}
					}
				}
			});
		}
	},
	expense_account: function(frm, cdt, cdn) {
		erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "expense_account");
	},
	cost_center: function(frm, cdt, cdn) {
		erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "cost_center");
	},
	sample_quantity: function(frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
	batch_no: function(frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
});

var validate_sample_quantity = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.sample_quantity && frm.doc.purpose == "Material Receipt") {
		frappe.call({
			method: 'erpnext.stock.doctype.stock_entry.stock_entry.validate_sample_quantity',
			args: {
				batch_no: d.batch_no,
				item_code: d.item_code,
				sample_quantity: d.sample_quantity,
				qty: d.transfer_qty
			},
			callback: (r) => {
				frappe.model.set_value(cdt, cdn, "sample_quantity", r.message);
			}
		});
	}
};