odoo.define("website_base.website_update_scce_information", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;
    publicWidget.registry.UpdateInformation = publicWidget.Widget.extend({
        selector: ".scce_profile",
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
        },
        /**
         * @private
         */
        _changeInput: function() {
            var phone = $("#phone").val()
            var email = $("#email").val()
            let popupConfirm = $(".popup-card-confirm")[0]
            if (phone && email) {
                ajax.jsonRpc("/save/changes/scce_information", 'call', {
                    'phone': phone,
                    'email': email,
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