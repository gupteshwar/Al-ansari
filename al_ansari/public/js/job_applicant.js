frappe.ui.form.on("Job Applicant",{
    onload:function(frm){
        auto_populate_child_table(frm);
    },
})

var arr = ["Are you currently employed?","Why do you want to leave your current job? & Relocate?","If you are appointed, how long you need to join us?",
"Do you have any relative here in Oman?","What are your current salary package and other benefits?",
"What is your salary package expectation? Is it Negotiable?",
"Years of experience in Oman and Other Country?",
"Would you be interested in doing other roles as well as the role you applied for?","Why are you interested to work with us?","Languages you are fluent ?","Would you be willing to travel / relocate?"
,"Please provide references, each from your current and previous employer?"
,"Can we contact the 02 references you have provided? If No, why?"
,"Please indicate your interview availability?"
,"No of dependents?"]

function auto_populate_child_table(frm) {
    var job_applic = frappe.model.get_doc("Job Applicant", frm.doc.name)
    frm.doc.questions_and_answers = []
    $.each(arr, function(index, row) {
        var d = frm.add_child("questions_and_answers");
            d.questions = row

            })
            refresh_field("questions_and_answers")
    }