odoo.define("website_base.attachment_request", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

        const dropArea = document.getElementById('dropArea');
        const fileInput = document.getElementById('fileInput');
        dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        });
        dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        fileInput.files = e.dataTransfer.files;
        });

        // Get references to the drop area and file input elements
        const dropArea2 = document.getElementById('dropArea2');
        const fileInput2 = document.getElementById('fileInput2');
        dropArea2.addEventListener('dragover', (e) => {
        e.preventDefault();
        });
        dropArea2.addEventListener('drop', (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        fileInput2.files = e.dataTransfer.files;
        });

})