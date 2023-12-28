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
            'click .refuse': '_CloseButton',
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
            $(".save_changes").removeClass("d-none");
            $(".save_changes").addClass("d-inline-block");
            $(".refuse").removeClass("d-none");
            $(".refuse").addClass("d-inline-block");
            $("#home_address").prop({ "required": true, })
            $("#mobile").prop({ "required": true, })
            $("#phone").prop({ "required": true, })
            $("#email").prop({ "required": true, })
        },
        /**
         * @private
         */
        _CloseButton: function() {
            $(".save_changes").addClass("d-none");
            $(".save_changes").removeClass("d-inline-block");
            $(".refuse").addClass("d-none");
            $(".refuse").removeClass("d-inline-block");
        },
    })

})