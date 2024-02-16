odoo.define("website_base.website_update_ci_information", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;
    publicWidget.registry.UpdateInformationCi = publicWidget.Widget.extend({
        selector: ".ci_profile",
        events: {
            'input .updated': '_ShowButton',
            'change .updated': '_changeInput',
        },
        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
        },

        /**
         * @override
         */
        start: function() {
            var def = this._super.apply(this, arguments);
            return def;
        },
        /**
         * @private
         */
        _ShowButton: function() {
            $("#phone").prop({ "required": true, })
            $("#email").prop({ "required": true, })
            $("#entry_level_pt_degree_earned").prop({ "required": true, })
            $("#highest_degree_earned").prop({ "required": true, })
            $("#degree_area").prop({ "required": true, })
            $("#years_experience_ci").prop({ "required": true, })
            $("#years_experience_clinician").prop({ "required": true, })
            $("#areas_expertise").prop({ "required": true, })
            $("#clinical_certification").prop({ "required": true, })
            $("#specify_area").prop({ "required": true, })
            $("#apta_credentialed_ci").prop({ "required": true, })
            $("#other_ci_credential").prop({ "required": true, })
            $("#professional_organization_membership").prop({ "required": true, })
        },
        /**
         * @private
         */
        _changeInput: function() {
            var phone = $("#phone").val()
            var email = $("#email").val()
            var entry_level_pt_degree_earned = $("#entry_level_pt_degree_earned").val()
            var highest_degree_earned = $("#highest_degree_earned").val()
            var degree_area = $("#degree_area").val()
            var years_experience_ci = $("#years_experience_ci").val()
            var years_experience_clinician = $("#years_experience_clinician").val()
            var areas_expertise = $("#areas_expertise").val()
            var clinical_certification = $("#clinical_certification").val()
            var specify_area = $("#specify_area").val()
            var apta_credentialed_ci = $("#apta_credentialed_ci").val()
            var other_ci_credential = $("#other_ci_credential").val()
            var professional_organization_membership = $("#professional_organization_membership").val()
            let popupConfirm = $(".popup-card-confirm")[0]
            if (phone && email) {
                ajax.jsonRpc("/save/changes/ci_information", 'call', {
                    'phone': phone,
                    'email': email,
                    'entry_level_pt_degree_earned': entry_level_pt_degree_earned,
                    'highest_degree_earned': highest_degree_earned,
                    'degree_area': degree_area,
                    'years_experience_ci': years_experience_ci,
                    'years_experience_clinician': years_experience_clinician,
                    'areas_expertise': areas_expertise,
                    'clinical_certification': clinical_certification,
                    'specify_area': specify_area,
                    'apta_credentialed_ci': apta_credentialed_ci,
                    'other_ci_credential': other_ci_credential,
                    'professional_organization_membership': professional_organization_membership,
                }).then(function(data) {


                })
                $(popupConfirm).css("transform", "translateX(0)");
                setTimeout(function() {
                    $(popupConfirm).css("transform", "translateX(500px)");
                }, 4000);
            }
        },

    })

})