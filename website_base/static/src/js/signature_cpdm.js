odoo.define("website_base.signature_cpdm", function (require) {
  "use strict";
  var rpc = require("web.rpc");
  const session = require("web.session");
  var ajax = require("web.ajax");
  var publicWidget = require("web.public.widget");
  publicWidget.registry.SignatureCPDM = publicWidget.Widget.extend({
    selector: "#ptse-form",
    events: {
        'click #new_ci': '_onClickNewCI',
        'change #ci_id': '_onCiChange',
    },

    _onCiChange: function(ev) {
      var CI_Id = $('#ci_id') 
      console.log("<<<<<<<<<<<<NewCI<<<<<<<<<");
      console.log("<<<<<<<<<<<<NewCI<<<<<<<<<");
      console.log("<<<<<<<<<<<<NewCI<<<<<<<<<");
      ajax.jsonRpc("/show/info/ci", 'call', { 'ci_id': CI_Id.val() }).then(function (ci) {
      console.log(ci, "<<<<<<<<<<<<NewCI<<<<<<<<<");
      $('#entry_level_pt_degree_earned').val(ci.entry_level_pt_degree_earned)
      $('#highest_degree_earned').val(ci.highest_degree_earned)
      $('#degree_area').val(ci.degree_area)
      $('#years_experience_ci').val(ci.years_experience_ci)
      $('#years_experience_clinician').val(ci.years_experience_clinician)
      $('#areas_expertise').val(ci.areas_expertise)
      $('#clinical_certification').val(ci.clinical_certification)
      $('#specify_area').val(ci.specify_area)
      $('#apta_credentialed_ci').val(ci.apta_credentialed_ci)
      $('#other_ci_credential').val(ci.other_ci_credential)
      $('#professional_organization_membership').val(ci.professional_organization_membership)
      })
    },
    _onClickNewCI: function(ev) {
    var NewCI = document.querySelector('#new_ci')
    var CI = $('.ci')
    var InputNewCi = $('.input-newci')
    // console.log($(NewCI).checked, "<<<<<<<<<<<<NewCI<<<<<<<<<");
    // console.log(NewCI.val(), "<<<<<<<<<<<<NewCI<<<<<<<<<");
    // var openModalbuttons = document.querySelector('#new_ci');
    // console.log(openModalbuttons.checked, "<<<<<<<<<<<<NeopenModalbuttonswCI<<<<<<<<<");
 
    if (NewCI.checked){
      CI.addClass('d-none')
      InputNewCi.removeClass('d-none')
      $("#ci_id").prop({ "required": false, })
      $("#name_ci").prop({ "required": true, })
    }else{
      CI.removeClass('d-none')
      InputNewCi.addClass('d-none')
      $("#ci_id").prop({ "required": true, })
      $("#name_ci").prop({ "required": false, })
    }
    }
  })
  $(document).ready(function () {
    try {
      var CanvasStudent = document.getElementById("signature-student");
      var CanvasCI = document.getElementById("signature-ci");
      var PtseForm = document.getElementById("ptse-form");

      //  window.onresize = resizeCanvas;
      // resizeCanvas();
      // window.onresize = resizeCanvas2;
      //  resizeCanvas2();

      var SignaturePadStudent = new SignaturePad(CanvasStudent, {
        backgroundColor: "rgb(250,250,250)",
      });
      var SignaturePadCI = new SignaturePad(CanvasCI, {
        backgroundColor: "rgb(250,250,250)",
      });

  

      document.getElementById("save").addEventListener('submit', event => {
        console.log(session);
        var StudentSignature = $("#student_signature")
        console.log(PtseForm.checkValidity(), "<<<<<<<<<<<<PtseForm.checkValidity()<<<<<<<<<");
        if (!PtseForm.checkValidity()) {
        rpc.query({
            model: "res.partner",
            method: "search_read",
            args: [[], ["is_student", "name"]],
          }).then(function (partner) {
            console.log(partner, "<<<<<<<<=====");
            if(!StudentSignature.val()){
              if (partner[0]["is_student"] && SignaturePadStudent.isEmpty()) {
                let popup = $("#popup-card-error")[0];
                $(popup).css("transform", "translateX(0)");
                setTimeout(function () {
                  $(popup).css("transform", "translateX(500px)");
                }, 4000);
              } else {
                StudentSignature.val(SignaturePadStudent.toDataURL().split(",")[1]);
  
                console.log($("#student_signature").val());
                event.preventDefault()
                event.stopPropagation()
                // ajax.jsonRpc('/save/report', 'call',{
                //     'student_signature' : StudentSignature.val(),
                // }).then(function (result) {
  
                // });
              }
            }else{
              event.preventDefault()
              event.stopPropagation()
            }
          });
        }
      } , false );
      document.getElementById("clear-student").addEventListener("click", function () {
          SignaturePadStudent.clear();
        });
      document.getElementById("clear-ci").addEventListener("click", function () {
          SignaturePadCI.clear();
        });
    } catch (e) {}
  });
});
