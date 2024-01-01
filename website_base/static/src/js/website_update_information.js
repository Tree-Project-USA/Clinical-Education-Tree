odoo.define("website_base.website_update_information", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;
    publicWidget.registry.UpdateInformation = publicWidget.Widget.extend({
        selector: ".student_profile",
        events: {
            'input .updated': '_ShowButton',
            'change .updated': '_changeInput',
        },
        // 



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
            $("#home_address").prop({ "required": true, })
            $("#mobile").prop({ "required": true, })
            $("#phone").prop({ "required": true, })
            $("#email").prop({ "required": true, })
        },
        /**
         * @private
         */
        _changeInput: function() {
            var home_address = $("#home_address").val()
            var phone = $("#phone").val()
            var personal_phone = $("#personal_phone").val()
            var personal_email_address = $("#personal_email_address").val()
            let popupConfirm = $(".popup-card-confirm")[0]
            if (home_address && phone && personal_phone && personal_email_address) {
                ajax.jsonRpc("/save/changes/information", 'call', {
                    'home_address': home_address,
                    'phone': phone,
                    'personal_phone': personal_phone,
                    'personal_email_address': personal_email_address,
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