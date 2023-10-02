odoo.define("wbsite_base.file", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    var counter_files = 0;

    publicWidget.registry.Course = publicWidget.Widget.extend({
        selector: ".files",
        events: {
            'click #add_files': '_onClickAddCourses',
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            this._onClickAddCourses();
        },

        _onClickAddCourses: function(ev) {
            const file_id = "#" + $(".file-list:last").attr("id");
            // add row for file
            const file_new_tag =
                `<tr class="file-list" id="course_` + counter_files + `">
                <td class="row-index" colspan="5">
                    <div class="row">
                        <div class="col-12">
                            <div>
								<input
									type="file"
									multiple="multiple"
									accept="image/jpg, image/jpeg, image/png, application/pdf"
									class="form-control"
									name="datas_` + counter_files + `" 
									id="datas_` + counter_files + `"
								/>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="text-center" >
                    <i class="btn fa fa-trash fa_custom" 
                    id="remove_file_` + counter_files + `" type="button" 
                        style="color:#dc3545;font-size:18px">
                    </i>
                </td>`

            if ($(".file-list:last").attr("id") !== undefined) {
                $(file_id).after(file_new_tag);
            } else {
                $("#add_file").append(file_new_tag);

            }

            // delete row in  row of files
            var removerow = '#remove_file_' + counter_files;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if (el.closest('.file-list').index() >= $('.file-list:last').index()) {
                    el.closest('.file-list').remove();
                    counter_files--
                    $('input[name="len_file"]').attr('value', counter_files)
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
            counter_files++
            $('input[name="len_file"]').attr('value', counter_files)
        },
    })

})