odoo.define("website_base.location_student", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;
    var ids = []
    var counter_locations = 0
    var ZipCodeDiet = {}
    publicWidget.registry.Locations = publicWidget.Widget.extend({
        selector: ".locations_student",
        events: {
            // 'click .custom_create': '_onClickSubmit',
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            console.log($("#variable"), '====')
            const variable = $("#variable").val()
            console.log(variable, '====')
            for (let i = 0; i < parseInt(variable); i++) {
                this._AddLocationsStudent()
            }
        },

        /**
         * @override
         */
        start: function() {
            var def = this._super.apply(this, arguments);
            $('.locations_student').removeClass('d-none')
            $('.loading-indicator').addClass('d-none')
            return def;
        },
        /**
         * @private
         */
        _AddLocationsStudent: function() {
            var locations_zip_vals = $('#locations_zip').val();
            console.log(locations_zip_vals, '===========locations_zip_vals')
            if (locations_zip_vals) {
                var locations_vals = JSON.parse(locations_zip_vals);
                console.log(locations_vals, '===========locations_zip_vals')

            }
            var IndexLocations = counter_locations + 1
            const LocationsZipID = "#" + $(".locations-list:last").attr("id");
            const LocationsZipNewTag =
                `<tr class="file-list" id="locations_` + counter_locations + `">
                <input type="hidden" name="id_` + counter_locations + `" id="id_` + counter_locations + `" />
                    <td>
                        <div class="form-group">
                            <span>` + IndexLocations + ` </span>
                        </div>
                    </td>
                    <td>
                        <div class="form-group">
                            <div class="input-group mb-2">
                                <input type="text" id="zip_` + counter_locations + `"
                                    name="zip_` + counter_locations + `" required="required"
                                    class="form-control"
                                    maxlength="5"
                                />
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="form-group">
                            <div class="input-group mb-2">
                                <input type="text" id="state_` + counter_locations + `"
                                    name="state_` + counter_locations + `" required="required"
                                    class="form-control"
                                    style="pointer-events: none;"
                                />
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="form-group">
                            <div class="input-group mb-2">
                                <input type="text" id="city_` + counter_locations + `"
                                    name="city_` + counter_locations + `" required="required"
                                    class="form-control"
                                    style="pointer-events: none;"
                                />
                            </div>
                        </div>
                    </td>
                </tr>`

            if ($(".locations-list:last").attr("id") !== undefined) {
                $(LocationsZipID).after(LocationsZipNewTag);
            } else {
                $("#locations_zip_code").append(LocationsZipNewTag);
            }

            var ZipID = "#zip_" + counter_locations
            var StateID = "#state_" + counter_locations
            var CityID = "#city_" + counter_locations
            var LocationsID = "#id_" + counter_locations
            $(ZipID).keypress(function(event) {
                if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
                    event.preventDefault();
                }
            });
            $(ZipID).bind('input', function() {
                var ZipCode = $(ZipID).val()
                ajax.jsonRpc("/show/locations", 'call', { 'zip_code': ZipCode }).then(function(data) {
                    if (data.id) {
                        $(StateID).val(data['state'])
                        $(CityID).val(data['city'])
                        $(LocationsID).val(data['id'])
                        $.each(ZipCodeDiet, function(key, val) {
                            if (val == data.id) {
                                $(".zip_code_error").removeClass("d-none")
                                $(StateID).val("")
                                $(CityID).val("")
                            }


                        })
                        ZipCodeDiet[ZipID] = data.id

                        $.each(ZipCodeDiet, function(key, val) {
                            ids.push(val)
                        })
                        $('#list_zip_code').val(ids);
                    } else {
                        $(".zip_code_error").removeClass("d-none")
                        setTimeout(function() {
                            $(".zip_code_error").addClass("d-none")
                        }, 3000);
                        $(StateID).val("")
                        $(CityID).val("")
                    }
                })
            });
            if (locations_vals) {

                $(ZipID).val(locations_vals[counter_locations]).change()

            }
            counter_locations++;
        },
    })


    $(document).ready(function() {
        $('input[type=checkbox]').change(function(e) {
                let popup = $(".popup-card-error")[0]
                let content = $("#content-p")
                if ($('input[type=checkbox]:checked').length > 5) {
                    $(this).prop('checked', false)
                    $(content).text('Only allowed 5 preferred settings')
                    $(popup).css("transform", "translateX(0)");
                    setTimeout(function() {
                        $(popup).css("transform", "translateX(500px)");
                    }, 4000);
                }
            }),

            /**
             * @private
             * @param {Event} ev
             */
            $('.preferred_setting').on('click', '.new-setting-submit', function(event) {
                var $this = $(this);
                var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                var list = []
                let popup = $(".popup-card-error")[0]
                let content = $("#content-p")
                checkboxes.forEach(boxes => {
                    if (boxes.checked == true) {
                        list.push(boxes.id)
                    }
                })
                if (list.length < 5) {
                    $(content).text('Must be selected 5 preferred settings')
                    $(popup).css("transform", "translateX(0)");
                    setTimeout(function() {
                        $(popup).css("transform", "translateX(500px)");
                    }, 4000);
                } else {
                    $('#list_setting').val(list)
                    ajax.jsonRpc("/check/preferred/setting", 'call', {
                        'list_setting': list,
                    }).then(function(result) {
                        if (result == true) {
                            event.preventDefault();
                            $this.closest('form').submit();
                        } else {
                            $(content).text('You should have one (IP) as minimum and one (OP)')
                            $(popup).css("transform", "translateX(0)");
                            setTimeout(function() {
                                $(popup).css("transform", "translateX(500px)");
                            }, 4000);
                        }
                    })
                }



            })
    })



})