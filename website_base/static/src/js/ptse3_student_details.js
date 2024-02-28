odoo.define("website_base.ptse3_student_details", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

    var counter_document = 0;
    publicWidget.registry.PTSE3StudentDetails = publicWidget.Widget.extend({
        selector: ".student_details",
        events: {
            'change #ci_id': '_changeSelectCI',
            // 'change #new_name': '_changeInputNewName',
        },
        
        /**
         * @class
        */
       init: function() {
         
        },
 
    // _changeInputNewName: function() {
    //     var NewCi = $('input[name="new_name"]:checked') 
    //     if(NewCi.length){
    //         $(".select-ci").addClass("d-none")
    //         $(".input-ci").removeClass("d-none")
    //     }else{
    //         $(".input-ci").addClass("d-none")
    //         $(".select-ci").removeClass("d-none")
    //     }
    // },
    /**
         * @private
         */
_changeSelectCI: function() {
    const CiId = $("#ci_id") 
      ajax.jsonRpc("/show/info/ci", 'call', { 'ci_id': CiId.val() }).then(function(ci) {
            console.log(ci)
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
      })
},
        
    })
})