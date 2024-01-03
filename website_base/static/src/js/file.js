odoo.define("website_base.file", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    var counter_files = 0;

    publicWidget.registry.Course = publicWidget.Widget.extend({
        selector: ".hardship, .hard_ship_update",
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
            const file_id = "#" + $(".file-list1:last").attr("id");
            // add row for file
            const file_new_tag =
                `<tr class="file-list1" id="course_` + counter_files + `">
                <td class="row-index" colspan="5">
                    <div class="row">
                        <div class="col-12">
                        <div class="file-upload" id="file-upload_` + counter_files + `">
                            <div class="file-select">
                                <div class="file-select-button" id="fileName_` + counter_files + `">
                                    Choose File
                                </div>
                                <div class="file-select-name" id="noFile_` + counter_files + `">
                                    Drag and drop your file here
                                </div> 
                                <input type="file" 
                                    multiple
                                    accept=".jpg, .jpeg, .png, .pdf, .docx, .xls, .pptx"
                                    required
                                    name="datas_${counter_files}"
                                    id="chooseFile_${counter_files}"
                                />
                            </div>
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

            if ($(".file-list1:last").attr("id") !== undefined) {
                $(file_id).after(file_new_tag);
            } else {
                $("#add_file").append(file_new_tag);

            }

            // delete row in  row of files
            var removerow = '#remove_file_' + counter_files;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if (el.closest('.file-list1').index() >= $('.file-list1:last').index()) {
                    el.closest('.file-list1').remove();
                    counter_files--
                    $('input[name="len_file"]').attr('value', counter_files)
                }
            });

            var ChooseFile = '#chooseFile_' + counter_files
            var FileUpload = '#file-upload_' + counter_files
            var NoFile = '#noFile_' + counter_files
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
            counter_files++
            $('input[name="len_file"]').attr('value', counter_files)
        },
    })

})