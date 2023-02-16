frappe.ui.form.on("Interview Feedback",{
    onload:function(frm){
        auto_populate_grading_table(frm);
    },
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
    
    })
    frm.get_field("grading").grid.cannot_add_rows = true;
    refresh_field("grading")
    
}
