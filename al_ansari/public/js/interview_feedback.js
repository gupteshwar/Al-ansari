frappe.ui.form.on("Interview Feedback",{
    onload:function(frm){
        auto_populate_grading_table(frm);
    },
    interviewer:function(frm) {
        set_position_field(frm)
    }
})

var grading = [["Outstanding","46-55","36-55"],["Above Average","36-55","26-35"],["Average","26-35","16-25"],
            ["Below Average","11-25","1-15"]]

function auto_populate_grading_table(frm) {
    var interview_fb = frappe.model.get_doc("Interview Feedback",frm.doc.name)
    frm.doc.grading = []
    $.each(grading, function(index,row) {
        var d = frm.add_child("grading");
            d.grading = row[0]
            d.with_experience = row[1]
            d.without_experience = row[2]
    
    var df = frappe.meta.get_docfield("Grading", "grading",frm.doc.name);
        df.read_only = 1;
    var x = frappe.meta.get_docfield("Grading", "with_experience",frm.doc.name);
        x.read_only = 1;
    var a = frappe.meta.get_docfield("Grading", "without_experience",frm.doc.name);
        a.read_only = 1;      
    })
    frm.get_field("grading").grid.cannot_add_rows = true;
    refresh_field("grading")
    
}
// frappe.model.get_value('Print Settings', {'name': 'Print Settings'}, 'pdf_page_size',
//   function(d) {
//     console.log(d)
//   })

function set_position_field(frm) {
    frappe.call({
        method: "frappe.client.get_value",
        args: {
                doctype: "Employee",
                fieldname: "designation",
                filters: {
                    user_id: frm.doc.interviewer,
                }
        },
        callback: function(r) {
            console.log(r.message['designation'])
            if (frm)
            frm.set_value('position',r.message['designation'])
        }
    })
}