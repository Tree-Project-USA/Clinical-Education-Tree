odoo.define("website_base.state_hardship", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    var counter_files = 0;

    publicWidget.registry.HardShipInformation = publicWidget.Widget.extend({
        selector: ".hardship_information",
        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            this._check_request_stage();
        },
        _check_request_stage: function() {
            var stage = $("#state").val();
            if (stage == "initial_submission") {
                $("#initial_submission").css({
                    "background-color": "#083B4D",
                    color: "#F9D6BF",
                });
            } else if (stage == "update_required") {
                $("#update_required").css({
                    "background-color": "#083B4D",
                    color: "#F9D6BF",
                });
            } else if (stage == "under_review") {
                $("#under_review").css({
                    "background-color": "#083B4D",
                    color: "#F9D6BF",
                });
            } else if (stage == "approved") {
                $("#approved").css({
                    "background-color": "#08a05c",
                    color: "#fff",
                });
            }else if (stage == "declined") {
                $("#declined").css({
                    "background-color": "red",
                    color: "#fff",
                });
            }else if (stage == "expired") {
                $("#expired").css({
                    "background-color": "083B4D",
                    color: "#F9D6BF",
                });
            }
        }
    })

})