odoo.define("website_base.signature_cpdm", function (require) {
  "use strict";
  var rpc = require("web.rpc");
  const session = require("web.session");
 
  $(document).ready(function () {
    try {
      var CanvasStudent = document.getElementById("signature-student");
      var PtseForm = document.getElementById("ptse-form");

      //  window.onresize = resizeCanvas;
      // resizeCanvas();
      // window.onresize = resizeCanvas2;
      //  resizeCanvas2();

      var SignaturePadStudent = new SignaturePad(CanvasStudent, {
        backgroundColor: "rgb(250,250,250)",
      });
      document.getElementById("save-student-signature").addEventListener('click', event => {
        console.log(session);
        var StudentSignature = $("#student_signature")
        console.log(PtseForm.checkValidity(), "<<<<<<<<<<<<PtseForm.checkValidity()<<<<<<<<<");
      
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
                event.preventDefault();
                PtseForm.submit();
                // ajax.jsonRpc('/save/report', 'call',{
                //     'student_signature' : StudentSignature.val(),
                // }).then(function (result) {
  
                // });
              }
            }else{
              event.preventDefault();
              PtseForm.submit();
            }
          });
        } );
      document.getElementById("clear-student").addEventListener("click", function () {
          SignaturePadStudent.clear();
        });
   
    } catch (e) {}
    try{
      var CanvasCI = document.getElementById("signature-ci");
      var PtseForm = document.getElementById("ptse-form");
      var SignaturePadCI = new SignaturePad(CanvasCI, {
        backgroundColor: "rgb(250,250,250)",
      });
      document.getElementById("save-ci-signature").addEventListener('click', event => {
        console.log(session);
        var CiSignature = $("#ci_signature")
        var CiSignatureDate = $("#ci_signature_date")
        console.log(CiSignature.val(), "<<<<<<<<<<<<PtseForm.checkValidity()<<<<<<<<<");
        if (SignaturePadCI.isEmpty() && !CiSignatureDate.val()) {
          let popup = $("#popup-card-error")[0];
          $(popup).css("transform", "translateX(0)");
          setTimeout(function () {
            $(popup).css("transform", "translateX(500px)");
          }, 4000);
          
        }else{
          console.log(SignaturePadCI.isEmpty(), "<<<<<<<<<<<<SignaturePadCI.isEmpty()<<<<<<<<<");
          CiSignature.val(SignaturePadCI.toDataURL().split(",")[1]);
          console.log(CiSignature.val(), "<<<<<<<<<<<<SignaturePadCI.isEmpty()<<<<<<<<<");
          event.preventDefault();
          PtseForm.submit();
        }
      } );
      document.getElementById("clear-ci").addEventListener("click", function () {
        SignaturePadCI.clear();
      });
      console.log(SignaturePadCI,'SignaturePadCI');
    }catch (e) {}
  });
});
