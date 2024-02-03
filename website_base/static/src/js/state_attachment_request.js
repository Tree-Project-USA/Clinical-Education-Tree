odoo.define("website_base.state_attachment_request", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    var counter_files = 0;

    publicWidget.registry.StateAttachmentRequest = publicWidget.Widget.extend({
        selector: ".medical_document",
        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            this._check_request_stage();
        },
        _check_request_stage: function() {
            var stage = $("#stage").val();
           if (stage == "update_required") {
                $("#update").css({
                    "background-color": "#000000",
                    color: "#b4904f",
                });
            } else if (stage == "under_review") {
                $("#review").css({
                    "background-color": "#000000",
                    color: "#b4904f",
                });
            } else if (stage == "confirmed") {
                $("#confirm").css({
                    "background-color": "#08a05c",
                    color: "#fff",
                });
            }else if (stage == "cancel") {
                $("#cancel").css({
                    "background-color": "red",
                    color: "#fff",
                });
            }
        }
    })

})