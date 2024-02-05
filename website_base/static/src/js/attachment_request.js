odoo.define("website_base.attachment_request", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

    var counter_attachments = 0;
    publicWidget.registry.Attachment = publicWidget.Widget.extend({
        selector: ".attachment_request",
        events: {
            'click #add_attachments': '_onClickAddAttachment',
        },
        
        /**
         * @class
        */
       init: function() {
           this._super.apply(this, arguments);
           this._popoverRPC = null;
           this._onClickAddAttachment();
        },
        
        _onClickAddAttachment: function(ev) {
            const attachment_id = "#" + $(".attachment-list:last").attr("id");
            // add row for file
            const attachment_new_tag =
                `<tr class="attachment-list" id="attachment_` + counter_attachments + `">
                <td class="row-index">
                    <select name="attachment_type_id_` + counter_attachments + `" 
                        id="attachment_type_id_` + counter_attachments + `"
                        class="form-control col-xl-12 custom-select attachment_type_id_` + counter_attachments + `" required="1">
                        <option  value="" selected="selected" disabled="1">Select...</option>
                    </select>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div class="form-group input-material">
                                <input type="date" 
                                    class="form-control" 
                                    name="expiration_date_` +  + `" 
                                    id="expiration_date_` + counter_attachments + `"
                                />
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                        <div class="file-upload" id="file-upload_` + counter_attachments + `">
                            <div class="file-select">
                                <div class="file-select-button" id="fileName_` + counter_attachments + `">
                                    Choose File
                                </div>
                                <div class="file-select-name" id="noFile_` + counter_attachments + `">
                                    Drag and drop your file here
                                </div> 
                                <input type="file" 
                                    multiple
                                    accept=".jpg, .jpeg, .png, .pdf, .docx, .xls, .pptx"
                                    required
                                    name="datas_${counter_attachments}"
                                    id="chooseFile_${counter_attachments}"
                                />
                            </div>
                        </div>
                        </div>
                    </div>
                </td>
                <td class="text-center" >
                    <i class="btn fa fa-trash fa_custom" 
                    id="remove_attachment_` + counter_attachments + `" type="button" 
                        style="color:#dc3545;font-size:18px">
                    </i>
                </td>`

            if ($(".attachment-list:last").attr("id") !== undefined) {
                $(attachment_id).after(attachment_new_tag);
            } else {
                $("#add_attachment").append(attachment_new_tag);

            }

            // delete row in  row of files
            var removerow = '#remove_attachment_' + counter_attachments;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if (el.closest('.attachment-list').index() >= $('.attachment-list:last').index()) {
                    el.closest('.attachment-list').remove();
                    counter_attachments--
                    $('input[name="len_file"]').attr('value', counter_attachments)
                }
            });
            var ChooseFile = '#chooseFile_' + counter_attachments
            var FileUpload = '#file-upload_' + counter_attachments
            var NoFile = '#noFile_' + counter_attachments
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
            var attachment = "#attachment_type_id_" + counter_attachments;
            ajax.jsonRpc("/attachment").then(function(result) {
                _.each(result["attachment_type_ids"], function(value){
                    $(attachment).append($('<option>', {
                        value: value.id,
                        text: value.name,
                    }))
                })
            })
            counter_attachments++
            $('input[name="len_attachment"]').attr('value', counter_attachments)
        },
    })

})