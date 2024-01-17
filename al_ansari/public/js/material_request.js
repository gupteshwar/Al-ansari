frappe.ui.form.on('Material Request', {
	cost_center: function(frm) {
        frm.doc.items.forEach(function(item){
            item.cost_center = frm.doc.cost_center
            item.branches = frm.doc.branch
        });
        frm.refresh_field('items')
    },
    branch: function(frm) {
        frm.doc.items.forEach(function(item){
            item.cost_center = frm.doc.cost_center
            item.branches = frm.doc.branch
        });
        frm.refresh_field('items')
    }
})