odoo.define("website_base.file_attachment_request", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');
    publicWidget.registry.Attachment = publicWidget.Widget.extend({
        selector: ".student_profile",
        events: {
            'input #fileInput': '_onClickChangFile',
        },

        /**
         * @class
        */
       init: function() {
        this._super.apply(this, arguments);
        this._popoverRPC = null;
        this._onClickChangFile();
     },

     _onClickChangFile: function(ev) {
        console.log("ajedsdfsdfsdf");
        var dropContainer = document.getElementById('dropContainer');
        var fileInput = document.getElementById('fileInput');
        
        dropContainer.addEventListener('dragover', function(evt) {
            evt.preventDefault();
        });
        
        dropContainer.addEventListener('dragenter', function(evt) {
            evt.preventDefault();
        });
        
        dropContainer.addEventListener('drop', function(evt) {
            evt.preventDefault();
            
            fileInput.files = evt.dataTransfer.files;
            
            // If you want to use some of the dropped files
            const dT = new DataTransfer();
            for (var i = 0; i < evt.dataTransfer.files.length; i++) {
                dT.items.add(evt.dataTransfer.files[i]);
            }
            fileInput.files = dT.files;
        });
    }
    })

    
        // const dropArea = document.getElementById('dropArea');
        // const fileInput = document.getElementById('fileInput');
        // dropArea.addEventListener('dragover', (e) => {
        // e.preventDefault();
        // });
        // dropArea.addEventListener('drop', (e) => {
        // e.preventDefault();
        // const file = e.dataTransfer.files[0];
        // fileInput.files = e.dataTransfer.files;
        // });

        // // Get references to the drop area and file input elements
        // const dropArea2 = document.getElementById('dropArea2');
        // const fileInput2 = document.getElementById('fileInput2');
        // dropArea2.addEventListener('dragover', (e) => {
        // e.preventDefault();
        // });
        // dropArea2.addEventListener('drop', (e) => {
        // e.preventDefault();
        // const file = e.dataTransfer.files[0];
        // fileInput2.files = e.dataTransfer.files;
        // });

})