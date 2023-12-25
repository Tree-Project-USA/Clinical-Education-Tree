odoo.define("website_base.location_student_update_hard_ship", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    var ajax = require('web.ajax');
    var counter_zip = 0;
    var zip_cod = 0;
    var state;
    var city;
    publicWidget.registry.LocationStudentHardShipUpdate = publicWidget.Widget.extend({
        selector: ".hard_ship_update",
        events: {
            'input input[type="text"]': '_onZipChanges',
            'click #add_zip': '_onClickAddzip',
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            this._onClickAddzip();
        },
          /**
        * @private
        */
        _onClickAddzip: function(ev) {
            var count = counter_zip + 1;
            const zip_id = "#" + $(".file-list:last").attr("id");
            const zip_new_tag =
                `<tr class="file-list" id="zip_` + counter_zip + `">
                <td>
                    <div class="form-group">
                        <span>` + count  + ` </span>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div>
								<input
									type="text"
									class="form-control"
                                    ${counter_zip === 0 ? 'required' : ''}
									name="zip_code_` + counter_zip + `" 
									id="zip_code_` + counter_zip + `"
								/>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div>
								<input
									type="text"
									class="form-control"
                                    ${counter_zip === 0 ? 'required' : ''}
                                    style="pointer-events: none;"
									name="state_` + counter_zip + `" 
									id="state_` + counter_zip + `"
								/>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div>
								<input
									type="text"
									class="form-control"
                                    style="pointer-events: none;"
                                    ${counter_zip === 0 ? 'required' : ''}
									name="city_` + counter_zip + `" 
									id="city_` + counter_zip + `"
								/>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="text-center" >
                    <i class="btn fa fa-trash fa_custom" 
                    id="remove_zip_` + counter_zip + `" type="button" 
                        style="color:#dc3545;font-size:18px">
                    </i>
                </td>`

            if ($(".file-list:last").attr("id") !== undefined) {
                $(zip_id).after(zip_new_tag);
            } else {
                $("#add_zip_code").append(zip_new_tag);
            }
            zip_cod = "#zip_code_" + counter_zip 
            state = "#state_" + counter_zip 
            city = "#city_" + counter_zip 

            // delete row in  row of files
            var removerow = '#remove_zip_' + counter_zip;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if(counter_zip > 1){
                    if (el.closest('.file-list').index() >= $('.file-list:last').index()) {
                        el.closest('.file-list').remove();
                        counter_zip--
                        if (counter_zip < 3){
                            $("#add_zip").removeClass("d-none")
                        }
                        console.log(counter_zip)
                        $('input[name="len_zip_code"]').attr('value', counter_zip)
                    }
                }
            });

            Array.prototype.remove = function() {
                var what, a = arguments,
                    L = a.length,
                    ax;
                while (L && this.length) {
                    what = a[--L];
                    while ((ax = this.indexOf(what)) !== -1) {
                        this.splice(ax, 2);
                    }
                }
                return this;
            };
            counter_zip++
            console.log(counter_zip)
            $('input[name="len_zip_code"]').attr('value', counter_zip)
            if (counter_zip >= 3){
                $("#add_zip").addClass("d-none")
            }
        },

        /**
        * @private
        */
        _onZipChanges: function () {
            var zip_code = $(zip_cod).val();
            ajax.jsonRpc("/show/locations", 'call', { zip_code }).then(function(data) {
                $(state).val(data.state)
                $(city).val(data.city)
            });
        },
    })
})
