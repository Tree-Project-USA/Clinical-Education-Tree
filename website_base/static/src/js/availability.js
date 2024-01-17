odoo.define("website_base.availability", function(require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var counter_availab = 0;
    var zip_cod = 0;
    var state;
    var city;
    publicWidget.registry.LocationStudentHardShipUpdate = publicWidget.Widget.extend({
        selector: ".availability",
        events: {
            'input input[type="text"]': '_onZipChanges',
            'click #add_availability': '_onClickAddavailability',
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            this._onClickAddavailability();
        },
          /**
        * @private
        */
        _onClickAddavailability: function(ev) {
            var count = counter_availab + 1;
            const availability_id = "#" + $(".file-list:last").attr("id");
            const availability_row_new_tag =
                `<tr class="file-list text-center" id="availability_` + counter_availab + `">
                <td>
                    <div class="form-group">
                        <span>` + count  + ` </span>
                    </div>
                </td>
                <td class="row-index">
                    <div class="form-group">
                        <div class="input-group mb-2">
                            <input type="text" id="facility_` + counter_availab + `"
                                name="facility_` + counter_availab + `" required="required"
                                class="form-control"
                                style="pointer-events: none;"
                            />
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
                                    ${counter_availab === 0 ? 'required' : ''}
									name="state_` + counter_availab + `" 
									id="state_` + counter_availab + `"
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
                                    ${counter_availab === 0 ? 'required' : ''}
									name="city_` + counter_availab + `" 
									id="city_` + counter_availab + `"
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
                                    ${counter_availab === 0 ? 'required' : ''}
									name="city_` + counter_availab + `" 
									id="city_` + counter_availab + `"
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
                                    ${counter_availab === 0 ? 'required' : ''}
									name="city_` + counter_availab + `" 
									id="city_` + counter_availab + `"
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
									type="date"
									class="form-control"
                                    ${counter_availab === 0 ? 'required' : ''}
									name="city_` + counter_availab + `" 
									id="city_` + counter_availab + `"
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
                                    ${counter_availab === 0 ? 'required' : ''}
                                    name="city_` + counter_availab + `" 
                                    id="city_` + counter_availab + `"
                                />
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div>
                                <select name="sitting_id_` + counter_availab + `" 
                                    id="sitting_id_` + counter_availab + `"
                                    class="form-control col-xl-12 custom-select sitting_id_` + counter_availab + `" required="1">
                                    <option  value="" selected="selected" disabled="1">option</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div>
                                <select name="student_id_` + counter_availab + `" 
                                    id="student_id_` + counter_availab + `"
                                    class="form-control col-xl-12 custom-select student_id_` + counter_availab + `" required="1">
                                    <option  value="" selected="selected" disabled="1">option</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="text-center" >
                    <i class="btn fa fa-trash fa_custom" 
                    id="remove_zip_` + counter_availab + `" type="button" 
                        style="color:#dc3545;font-size:18px">
                    </i>
                </td>`

            if ($(".file-list:last").attr("id") !== undefined) {
                $(availability_id).after(availability_row_new_tag);
            } else {
                $("#add_availability_row").append(availability_row_new_tag);
            }
            zip_cod = "#zip_code_" + counter_availab 
            state = "#state_" + counter_availab 
            city = "#city_" + counter_availab 

            // delete row in  row of files
            var removerow = '#remove_zip_' + counter_availab;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if(counter_availab > 1){
                    if (el.closest('.file-list').index() >= $('.file-list:last').index()) {
                        el.closest('.file-list').remove();
                        counter_availab--
                        if (counter_availab < 3){
                            $("#add_zip").removeClass("d-none")
                        }
                        $('input[name="len_zip_code"]').attr('value', counter_availab)
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
            const domain = []
            var facility = "#facility_" + counter_availab;
            var sitting_id = "#sitting_id_" + counter_availab;
            var student_id = "#student_id_" + counter_availab;
            ajax.jsonRpc("/data/availability", 'call').then(function(data) {
               console.log(data)
               $(facility).val(data['facility_name'])
            })
            counter_availab++
            $('input[name="len_zip_code"]').attr('value', counter_availab)
            if (counter_availab >= 3){
                $("#add_zip").addClass("d-none")
            }
        },
    })
})
