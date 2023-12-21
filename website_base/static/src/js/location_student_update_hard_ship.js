odoo.define("website_base.location_student_update_hard_ship", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var ids = []
    publicWidget.registry.HardShipUpdate = publicWidget.Widget.extend({
        selector: ".hard_ship_update",
        events: {
            'click #add_zip_code': '_onClickZipCode',
            'change input[name="zip"]': "_onZipChanges",
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
        },

         /**
        * @private
        */
         _onZipChanges: function () {
            var zip = $('.total_project_costs > tbody > tr.project_cost_line div > input[name="zip"]');
            var State = $('.total_project_costs > tbody > tr.project_cost_line div > input[name="state"]');
            var City = $('.total_project_costs > tbody > tr.project_cost_line div > input[name="city"]');
            _.each(zip, function(value, index) {
                var remove_zip = 0;
                var zip_code = zip[index].value
                if (zip_code){
                    ajax.jsonRpc("/show/locations", 'call', { zip_code }).then(function(data) {
                        State[index].value = data['state']
                        City[index].value = data['city']
                        if (ids.includes(data.id) || data.id == false){
                            console.log("alrady found")
                        }else{
                            ids.push(data.id) 
                            console.log(ids)
                            $('#list_zip_code_h_u').val(ids);
                        }
                    });
                }
                zip[index].onblur = function() {
                    remove_zip = index
                    ids.splice(remove_zip, 1);
                    if (zip_code){
                        ajax.jsonRpc("/show/locations", 'call', { zip_code }).then(function(data) {
                            State[index].value = data['state']
                            City[index].value = data['city']
                            if (ids.includes(data.id) || data.id == false){
                                console.log("alrady found")
                            }else{
                                ids.push(data.id) 
                                console.log(ids)
                                $('#list_zip_code_h_u').val(ids);
                            }
                        });
                    }
                }
            })
        },
    })

})