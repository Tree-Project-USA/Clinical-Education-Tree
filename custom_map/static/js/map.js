// static/src/js/custom_map.js
odoo.define('custom_map.map', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    $(document).ready(function() {
        var statesData = {
            "type": "FeatureCollection",
            "features": [
            ]
        };
        var map = L.map('map').setView([37.8, -96], 4);

        // Add the tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '<a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Add the US state borders
        L.geoJSON(statesData, {
            style: function(feature) {
                return {
                    fillColor: '#cce5ff',
                    weight: 3,
                    color: '#0077b6',
                    fillOpacity: 0.5
                };
            }
        }).addTo(map);
        var searchControl = L.esri.Geocoding.geosearch().addTo(map);
        var results = L.layerGroup().addTo(map);

        var locations = [];
        ajax.jsonRpc("/custom_map/data/", 'call', {}).then(function(data) {
            console.log(data)
            data.forEach(function(location) {
                L.marker(location.coords)
                    .addTo(map)
                    .bindPopup(location.name);
            });
        })

        locations.forEach(function(location) {
            L.marker(location.coords)
                .addTo(map)
                .bindPopup(location.name);
        });
    });
});
