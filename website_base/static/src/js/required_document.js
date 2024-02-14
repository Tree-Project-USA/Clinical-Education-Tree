odoo.define("website_base.required_document", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

    var counter_document = 0;
    publicWidget.registry.TypeDocument = publicWidget.Widget.extend({
        selector: ".required_document",
        events: {
            'click #add_type_documents': '_onClickAddTypeDocument',
        },
        
        /**
         * @class
        */
       init: function() {
           this._super.apply(this, arguments);
           this._popoverRPC = null;
           this._onClickAddTypeDocument();
        },
        
        _onClickAddTypeDocument: function(ev) {
            const required_document_id = "#" + $(".document-list:last").attr("id");
            // add row for file
            const required_document_new_tag =
                `<tr class="document-list" id="document_` + counter_document + `">
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div class="form-group input-material">
                                <input type="text" 
                                    class="form-control" 
                                    name="name_` + counter_document + `" 
                                    id="name_` + counter_document + `"
                                />
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div class="form-group input-material">
                                <input type="text" 
                                    class="form-control" 
                                    name="portal_id_` + counter_document + `" 
                                    id="portal_id_` + counter_document + `"
                                />
                            </div>
                        </div>
                    </div>
                </td>
                <td class="row-index">
                    <div class="row">
                        <div class="col-12">
                            <div class="form-group input-material">
                                <input type="text" 
                                    class="form-control" 
                                    name="description_` + counter_document + `" 
                                    id="description_` + counter_document + `"
                                />
                            </div>
                        </div>
                    </div>
                </td>
                <td class="text-center" >
                    <i class="btn fa fa-trash fa_custom" 
                    id="remove_document_` + counter_document + `" type="button" 
                        style="color:#dc3545;font-size:18px">
                    </i>
                </td>`

            if ($(".document-list:last").attr("id") !== undefined) {
                $(required_document_id).after(required_document_new_tag);
            } else {
                $("#add_type_document").append(required_document_new_tag);

            }

            // delete row in  row of files
            var removerow = '#remove_document_' + counter_document;
            $(removerow).click(function(ev) {
                var el = $(ev.target);
                if (el.closest('.document-list').index() >= $('.document-list:last').index()) {
                    el.closest('.document-list').remove();
                    counter_document--
                    $('input[name="len_file"]').attr('value', counter_document)
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
            counter_document++
            $('input[name="len_type_documents"]').attr('value', counter_document)
        },
    })

})