odoo.define("website_base.ptse3_student_details", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require("web.ajax");
    var SignaturePadStudent 
    var SignaturePadCI
    $(document).ready(function () {
        try {
            var CanvasStudent = document.getElementById("signature-student");

            //  window.onresize = resizeCanvas;
            // resizeCanvas();
            // window.onresize = resizeCanvas2;
            //  resizeCanvas2();

            SignaturePadStudent = new SignaturePad(CanvasStudent, {
                backgroundColor: "rgb(250,250,250)",
            });
        } catch (e) { }
        try{
            var CanvasCI = document.getElementById("signature-ci");
          
            SignaturePadCI = new SignaturePad(CanvasCI, {
              backgroundColor: "rgb(250,250,250)",
            });
          }catch (e) {}
    });
    var counter_document = 0;
    publicWidget.registry.PTSE3StudentDetails = publicWidget.Widget.extend({
        selector: ".student_details",
        events: {
            "change #ci_id": "_changeSelectCI",
            "change #new_name": "_changeInputNewName",
            "click #save-student-signature": "_ClickSaveStudentSignature",
            "click #save-ci-signature": "_ClickSaveCISignature",
            "click #clear-student": "_ClickClearStudentSignature",
            "click #clear-ci": "_ClickClearCISignature",
        },
        
        /**
         * @class
         */
        init: function () { },
        /**
         * @class
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            var CanvasStudent = $("#signature-student");

            $('#date_clinical_experience_dates').datetimepicker({
                format: "MMMM-DD-YYYY",
                locale: moment.locale(),
                buttons: {
                    showClose: true,
                },

            });
            $('#date_student_signature_date').datetimepicker({
                format: "MMMM-DD-YYYY",
                locale: moment.locale(),    
                buttons: {
                    showClose: true,
                },
            });
            $('#date_ci_signature_date').datetimepicker({
                format: "MMMM-DD-YYYY",
                locale: moment.locale(),    
                buttons: {
                    showClose: true,
                },
            });
            if(!$('#ci_ids').val() || $('#ci_ids').val() == " "){
                $('#new_name').prop("checked", true);
                $('#new_name').change();
               
            }
            console.log( $('#new_name'),'<<<<<<<<<<<<<<<new_name<<<<');
           
            $('.student_details').removeClass('d-none')
            $('.loading-indicator').addClass('d-none')
            return def;
        },

        _changeInputNewName: function () {
            var NewCi = $('input[name="new_name"]:checked');
            if (NewCi.length) {
                $(".select-ci").addClass("d-none");
                $(".input-ci").removeClass("d-none");
                $('#first_name').prop("required", true);
                $('#last_name').prop("required", true);
                $('#email').prop("required", true);
                $('#ci_id').prop("required", false);
                $(NewCi).val(true);
            } else {
                $(NewCi).val(false);
                $('#first_name').prop("required", false);
                $('#last_name').prop("required", false);
                $('#ci_id').prop("required", true);
                $('#email').prop("required", false);
                $(".input-ci").addClass("d-none");
                $(".select-ci").removeClass("d-none");
            }
        },
        /**
         * @private
         */
        _changeSelectCI: function () {
            const CiId = $("#ci_id");
            ajax
                .jsonRpc("/show/info/ci", "call", { ci_id: CiId.val() })
                .then(function (ci) {
                
                    console.log(ci);
                    $("#entry_level_pt_degree_earned").val(
                        ci.entry_level_pt_degree_earned
                    );
                    $("#highest_degree_earned").val(ci.highest_degree_earned);
                    $("#degree_area").val(ci.degree_area);
                    $("#years_experience_ci").val(ci.years_experience_ci);
                    $("#years_experience_clinician").val(ci.years_experience_clinician);
                    $("#areas_expertise").val(ci.areas_expertise);
                    $("#clinical_certification").val(ci.clinical_certification);
                    $("#specify_area").val(ci.specify_area);
                    $("#apta_credentialed_ci").val(ci.apta_credentialed_ci);
                    $("#other_ci_credential").val(ci.other_ci_credential);
                });
        },
        /**
         * @private
         * @override
         * @param {event} ev
         */
        _ClickSaveCISignature: function (ev) { 
            var CiSignature = $("#ci_signature")
            console.log(this.el)
            console.log(SignaturePadCI.isEmpty())
            if(!this.el.checkValidity()){
                this.el.classList.add('was-validated');
            }else if (SignaturePadCI.isEmpty()) {
                let popup = $("#popup-card-error")[0];
                $(popup).css("transform", "translateX(0)");
                setTimeout(function () {
                  $(popup).css("transform", "translateX(500px)");
                }, 4000);
                return false;
              } else {
                CiSignature.val(SignaturePadCI.toDataURL().split(",")[1])
            }
            
        },
        /**
         * @private
         * @override
         * @param {event} ev
         */
        _ClickSaveStudentSignature: function (ev) { 
            var StudentSignature = $("#student_signature")
            if(!this.el.checkValidity() || $('#ci_id').val() == "0"){
                this.el.classList.add('was-validated');
            }
            else if (SignaturePadStudent.isEmpty()) {
                let popup = $("#popup-card-error")[0];
                $(popup).css("transform", "translateX(0)");
                setTimeout(function () {
                  $(popup).css("transform", "translateX(500px)");
                }, 4000);
                return false;
              } else {
                StudentSignature.val(SignaturePadStudent.toDataURL().split(",")[1]);
                // ajax.jsonRpc('/save/report', 'call',{
                //     'student_signature' : StudentSignature.val(),
                // }).then(function (result) {
  
                // });
              }
            // if(){

            // if(SignaturePadStudent.isEmpty()){
            //     let popup = $("#popup-card-error")[0];
            //     $(popup).css("transform", "translateX(0)");
            //     setTimeout(function () {
            //       $(popup).css("transform", "translateX(500px)");
            //     }, 4000);
            // }else{
            //     ev.preventDefault();
            //     this.el.checkValidity();
            // }
            
        },
        _ClickClearStudentSignature: function (ev) { 
            SignaturePadStudent.clear();
        },
        _ClickClearCISignature: function (ev) { 
            SignaturePadCI.clear();
        },
    });
});
