odoo.define("website_base.departments", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var counter_availability = 0;
    var previous;
    var number_of_company;
    const previous_list = []
    const services_type_list = []

    publicWidget.registry.Departments = publicWidget.Widget.extend({
        selector: ".availability",
        events: {
            'click #add_departments': '_onClickDepartment',
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            this._onClickDepartment();
        },

        start: function () {
            this.$(".custom-select").select2();
        },


        _onClickDepartment: function(ev) {
            var option = "select..."
            const department_id = "#" + $(".department-list:last").attr("id");
            // add row for file
            const department_new_tag =
            `<tr class="department-list" id="zip_` + counter_availability + `">
            <td class="row-index" colspan="7">
                <div class="row">
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Program</label>
                        <select name="company_id_` + counter_availability + `" 
                            id="company_id_` + counter_availability + `"
                            class="form-control col-xl-12 custom-select company_id_` + counter_availability + `" required="1">
                            <option  value="" selected="selected">` + option + `</option>
                        </select>
                    </div>
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Locations</label>
                        <select 
                            name="department_id_` + counter_availability + `"  
                            id="department_id_` + counter_availability + `"
                            class="form-control col-xl-12 custom-select company_id_` + counter_availability + `" required="1"
                        >
                        <option  value="" selected="selected">` + option + `</option>
                        </select>
                    </div>
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Year</label>
                        <select name="term_` + counter_availability + `" 
                            id="term_` + counter_availability + `"
                            class="form-control col-xl-12 custom-select experience_id_` + counter_availability + `" required="1">
                            <option  value="" selected="selected">` + option + `</option>
                        </select>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Term</label>
                        <select name="placement_term_${counter_availability}"
                        id="placement_term_${counter_availability}"  
                        class="form-control col-xl-12 custom-select placement_term_` + counter_availability + `" required="1">
                            <option value="" selected="selected">` + option + `</option>
                            <option value="fall">FALL</option>
                            <option value="spring">SPRING</option>
                            <option value="summer">SUMMER</option>
                        </select>
                    </div>
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">CE Type</label>
                        <select name="experience_id_` + counter_availability + `" 
                            id="experience_id_` + counter_availability + `"
                            class="form-control col-xl-12 custom-select experience_id_` + counter_availability + `" required="1">
                            <option  value="" selected="selected">` + option + `</option>
                        </select>
                    </div>
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Offer Setting Type</label>
                        <select name="setting_` + counter_availability + `"  
                        class="form-control col-xl-12 custom-select setting_` + counter_availability + `" required="1">
                            <option  value="" selected="selected">` + option + `</option>
                            <option  value="op">OP</option>
                            <option value="ip">IP</option>
                        </select>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Number of Offer</label>
                        <div>
                            <input
                                type="text"
                                class="form-control"
                                ${counter_availability === 0 ? 'required' : ''}
                                name="offers_` + counter_availability + `" 
                                id="offers_` + counter_availability + `"
                            />
                        </div>
                    </div>
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">Start Date</label>
                        <div>
                            <input
                                type="text"
                                class="form-control"
                                ${counter_availability === 0 ? 'required' : ''}
                                name="start_date_` + counter_availability + `" 
                                id="start_date_` + counter_availability + `"
                                readonly="1"
                            />
                        </div>
                    </div>
                    <div class="col-lg-4 col-12">
                        <label for="staticEmail" class="col-form-label">End Date</label>
                        <div>
                            <input
                                type="text"
                                class="form-control"
                                ${counter_availability === 0 ? 'required' : ''}
                                name="end_date_` + counter_availability + `" 
                                id="end_date_` + counter_availability + `"
                                readonly="1"
                            />
                        </div>
                    </div>
                </div>
               
            </td>
            <td class="text-center" >
                <i class="btn fa fa-trash fa_custom" 
                id="remove_department_` + counter_availability + `" type="button" 
                    style="color:#dc3545;font-size:18px">
                </i>
            </td>`

            if ($(".department-list:last").attr("id") !== undefined) {
                $(department_id).after(department_new_tag);
            } else {
                $("#add_department").append(department_new_tag);

            }

            // delete row in  row of files
            var removerow = '#remove_department_' + counter_availability;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if (el.closest('.department-list').index() >= $('.department-list:last').index()) {
                    el.closest('.department-list').remove();
                    counter_availability--
                    $('input[name="len_department"]').attr('value', counter_availability)
                }
            });

            var ChooseFile = '#chooseFile_' + counter_availability
            var FileUpload = '#file-upload_' + counter_availability
            var NoFile = '#noFile_' + counter_availability
            $(ChooseFile).bind('change', function () {
                var filename = $(ChooseFile).val();
                if (/^\s*$/.test(filename)) {
                  $(FileUpload).removeClass('active');
                  $(NoFile).text("Drag and drop your file here"); 
                }
                else {
                  $(FileUpload).addClass('active');
                  $(NoFile).text(filename.replace("C:\\fakepath\\", "")); 
                }
              });
              

            Array.prototype.remove = function() {
                var what, a = arguments,
                    L = a.length,
                    ax;
                while (L && this.length) {
                    what = a[--L];
                    while ((ax = this.indexOf(what)) !== -1) {
                        this.splice(ax, 1);
                    }
                }
                return this;
            };
            var department = "#department_id_" + counter_availability;
            var experience = "#experience_id_" + counter_availability;
            var term = "#term_" + counter_availability;
            var setting = "#setting_" + counter_availability;
            var company = "#company_id_" + counter_availability;
            var placement_term = "#placement_term_" + counter_availability;
            var start_date = "#start_date_" + counter_availability;
            var end_date = "#end_date_" + counter_availability;
            var facility_id = $("#facility_id").val()
            $(department).select2();
            $(company).select2();
            $(experience).select2();
            $(term).select2();
            $(setting).select2();
            // $(placement_term).select2();

            $(term).focus(function() {
                // Store the current value on focus, before it changes
            }).change(function() {
                var years = $(term).val()
                ajax.jsonRpc("/clinical/experience/dates", 'call', {
                    years 
                }).then(function(result) {
                    $(experience).empty();
                    $("#select2-chosen-3").html("<span>Select ...</span>");
                    $(experience).html("<option>Select ...</option>");
                    _.each(result["clinical_experience_ids"], function(value){
                        $(experience).append($('<option>', {
                            value: value.id,
                            text: value.name,
                        }));
                    });
                })
            })
            ajax.jsonRpc("/departments", 'call', {
                'id': facility_id,
            }).then(function(result) {
                _.each(result["company_ids"], function(value){
                    $(company).append($('<option>', {
                        value: value.id,
                        text: value.name,
                    }))
                })
                _.each(result["SELECTION_YEAR_RANGE"], function(value){
                    $(term).append($('<option>', {
                        value: value.id,
                        text: value.id,
                    }))
                })
            })
            $(company).focus(function() {
                // Store the current value on focus, before it changes
            }).change(function() {
                var company_id = $(company).val()
                ajax.jsonRpc("/inforamtion/company", 'call', { company_id }).then(function(data) {
                    $(department).empty();
                    _.each(data["department_ids"], function(value){
                        $(department).append($('<option>', {
                            value: value.id,
                            text: value.name + '/' + value.street + '/' + value.city + '/' + value.state,
                        }))
                    })
                });
            })
            $(experience).focus(function() {
                // Store the current value on focus, before it changes
            }).change(function() {
                var years = $(term).val()
                var terms = $(placement_term).val()
                var experience_id = $(experience).val()
                ajax.jsonRpc("/program/experience/term", 'call', { experience_id, years, terms }).then(function(data) {
                    $(start_date).val(data.start_date)
                    $(end_date).val(data.end_date)
                });
            })
            counter_availability++
            $('input[name="len_department"]').attr('value', counter_availability)
        },
    })

})