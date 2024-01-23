odoo.define("website_base.departments", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    var counter_availability = 0;

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

        _onClickDepartment: function(ev) {
            var option = "select..."
            const department_id = "#" + $(".department-list:last").attr("id");
            // add row for file
            const department_new_tag =
            `<tr class="department-list" id="zip_` + counter_availability + `">
            <td class="row-index">
                <select name="department_id_` + counter_availability + `" 
                    id="department_id_` + counter_availability + `"
                    class="form-control col-xl-12 custom-select department_id_` + counter_availability + `" required="1">
                    <option  value="" selected="selected" disabled="1">` + option + `</option>
                </select>
            </td>
            <td class="row-index">
                <select name="placement_type_` + counter_availability + `"  
                    class="form-control col-xl-12 custom-select placement_type_` + counter_availability + `">
                    <option  value="" selected="selected">` + option + `</option>
                    <option  value="ice">ICE</option>
                    <option value="tce">TCE</option>
                </select>
            </td>
            <td class="row-index">
                <select name="placement_term_` + counter_availability + `"  
                    class="form-control col-xl-12 custom-select placement_term_` + counter_availability + `">
                    <option  value="" selected="selected">` + option + `</option>
                    <option  value="fall">FALL</option>
                    <option value="spring">SPRING</option>
                    <option value="summer">SUMMER</option>
                </select>
            </td>
            <td class="row-index">
                <select name="term_` + counter_availability + `" 
                    id="term_` + counter_availability + `"
                    class="form-control col-xl-12 custom-select term_` + counter_availability + `" required="1">
                    <option  value="" selected="selected" disabled="1">` + option + `</option>
                </select>
            </td>
            <td class="row-index">
                <select name="setting_` + counter_availability + `"  
                    class="form-control col-xl-12 custom-selectsetting_` + counter_availability + `">
                    <option  value="" selected="selected">` + option + `</option>
                    <option  value="op">OP</option>
                    <option value="ip">IP</option>
                </select>
            </td>
            <td class="row-index">
                <div class="row">
                    <div class="col-12">
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
            var year = "#term_" + counter_availability;
            var facility_id = $("#facility_id").val()
            ajax.jsonRpc("/departments", 'call', {
                'id': facility_id,
            }).then(function(result) {
                console.log(result)
                console.log(result["department_ids"])
                console.log(result["company_id"])
                console.log(result["SELECTION_YEAR_RANGE"])
                _.each(result["department_ids"], function(value){
                    $(department).append($('<option>', {
                        value: value.id,
                        text: value.name,
                    }))
                })
                _.each(result["SELECTION_YEAR_RANGE"], function(value){
                    $(year).append($('<option>', {
                        value: value.id,
                        text: value.id,
                    }))
                })
            })
            counter_availability++
            $('input[name="len_department"]').attr('value', counter_availability)
        },
    })

})