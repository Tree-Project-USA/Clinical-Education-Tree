odoo.define("website_base.scce_attachment_request", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

    var counter_scce_attachments = 0;
    publicWidget.registry.ScceAttachment = publicWidget.Widget.extend({
        selector: ".scce_attachment_request",
        events: {
            'click #add_scce_attachments': '_onClickAddScceAttachment',
        },
        
        /**
         * @class
        */
       init: function() {
           this._super.apply(this, arguments);
           this._popoverRPC = null;
           this._onClickAddScceAttachment();
        },
        
        _onClickAddScceAttachment: function(ev) {
            const scce_attachment_id = "#" + $(".scce-attachment-list:last").attr("id");
            // add row for file
            const scce_attachment_new_tag =
                `<tr class="scce-attachment-list" id="scce_attachment_` + counter_scce_attachments + `">
                <td class="row-index">
                    <select name="scce_attachment_type_id_` + counter_scce_attachments + `" 
                        id="scce_attachment_type_id_` + counter_scce_attachments + `"
                        class="form-control col-xl-12 custom-select scce_attachment_type_id_` + counter_scce_attachments + `" required="1">
                        <option  value="" selected="selected" disabled="1">Select...</option>
                    </select>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div class="form-group input-material">
                                <input type="date" 
                                    class="form-control" 
                                    name="scce_expiration_date_` + counter_scce_attachments + `" 
                                    id="scce_expiration_date_` + counter_scce_attachments + `"
                                />
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                        <div class="file-upload" id="scce_file_upload_` + counter_scce_attachments + `">
                            <div class="file-select">
                                <div class="file-select-button" id="scce_fileName_` + counter_scce_attachments + `">
                                    Choose File
                                </div>
                                <div class="file-select-name" id="scce_noFile_` + counter_scce_attachments + `">
                                    Drag and drop your file here
                                </div> 
                                <input type="file" 
                                    multiple
                                    accept=".jpg, .jpeg, .png, .pdf, .docx, .xls, .pptx"
                                    required
                                    name="scce_datas_${counter_scce_attachments}"
                                    id="scce_chooseFile_${counter_scce_attachments}"
                                />
                            </div>
                        </div>
                        </div>
                    </div>
                </td>
                <td class="text-center" >
                    <i class="btn fa fa-trash fa_custom" 
                    id="remove_scce_attachment_` + counter_scce_attachments + `" type="button" 
                        style="color:#dc3545;font-size:18px">
                    </i>
                </td>`

            if ($(".scce-attachment-list:last").attr("id") !== undefined) {
                $(scce_attachment_id).after(scce_attachment_new_tag);
            } else {
                $("#add_scce_attachment").append(scce_attachment_new_tag);

            }

            // delete row in  row of files
            var removerow = '#remove_scce_attachment_' + counter_scce_attachments;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if (el.closest('.scce-attachment-list').index() >= $('.scce-attachment-list:last').index()) {
                    el.closest('.scce-attachment-list').remove();
                    counter_scce_attachments--
                    $('input[name="len_scce_attachment"]').attr('value', counter_scce_attachments)
                }
            });
            var ChooseFile = '#scce_chooseFile_' + counter_scce_attachments
            var FileUpload = '#scce_file_upload_' + counter_scce_attachments
            var NoFile = '#scce_noFile_' + counter_scce_attachments
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
            var attachment = "#scce_attachment_type_id_" + counter_scce_attachments;
            ajax.jsonRpc("/scce/attachment").then(function(result) {
                _.each(result["attachment_type_ids"], function(value){
                    $(attachment).append($('<option>', {
                        value: value.id,
                        text: value.name,
                    }))
                })
            })
            counter_scce_attachments++
            $('input[name="len_scce_attachment"]').attr('value', counter_scce_attachments)
        },
    })

})