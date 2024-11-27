
odoo.define("clinical_decision_making.map", function (require) {
    "use strict";

    const AbstractAction = require("web.AbstractAction");
    const core = require("web.core");
    const ajax = require("web.ajax");

    const MapScce = AbstractAction.extend({
        contentTemplate: "MapScce",

        start: function () {
           
            return this._super(...arguments).then(() => {
                setTimeout(() => {
                    this._initializeMap();
                }, 0); 
            });
        },

        _initializeMap: function() {
            var statesData = {
                "type": "FeatureCollection",
                "features": []
            };
    
            var mapElement = document.getElementById('map');
            if (!mapElement) {
                console.error("Map container not found!");
                return;
            }
    
            var map = L.map('map').setView([37.8, -96], 4);
    
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '<a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
            }).addTo(map);
    
            L.geoJSON(statesData, {
                style: function (feature) {
                    return {
                        fillColor: '#cce5ff',
                        weight: 3,
                        color: '#0077b6',
                        fillOpacity: 0.5,
                    };
                },
            }).addTo(map);
    
            // var searchControl = L.esri.Geocoding.geosearch().addTo(map);
            // var results = L.layerGroup().addTo(map);
    
            ajax.jsonRpc("/scce/map/data/", 'call', {}).then(function (data) {
                data.forEach(function (data) {
                    var popupContent = `
                        <div>
                            <div class="row">
                                <div class="col-6">
                                    <strong>Clinical Site Name</strong>
                                    <h6>${data.clinical_site_name ? data.clinical_site_name : "Not found Site Name"}</h6>
                                </div>
                                <div class="col-6">
                                    <strong>SCCE Email Address</strong>
                                    <h6>${data.scce_email_address ? data.scce_email_address : "Not found Email"}</h6>
                                </div>
                                <div class="col-6">
                                    <strong>SCCE First Name</strong>
                                    <h6>${data.scce_first_name ? data.scce_first_name : "Not found First Name"}</h6>
                                </div>
                                <div class="col-6">
                                    <strong>SCCE Last Name</strong>
                                    <h6>${data.scce_last_name ? data.scce_last_name : "Not found Last Name"}</h6>
                                </div>
                                <div class="col-6 mt-2">
                                    <strong>SCCE Site Address</strong>
                                    <h6>${data.clinical_site_address ? data.clinical_site_address : "Not found Site Address"}</h6>
                                </div>
                                <div class="col-6 mt-2">
                                    <strong>City</strong>
                                    <h6>${data.city ? data.city : "Not found City"}</h6>
                                </div>
                                <div class="col-6 mt-2">
                                    <strong>State</strong>
                                    <h6>${data.state ? data.state : "Not found State"}</h6>
                                </div>
                                <div class="col-6 mt-2">
                                    <strong>Zip Code</strong>
                                    <h6>${data.name ? data.name : "Not found Zip Code"}</h6>
                                </div>
                                <div class="col-12 mt-2">
                                    <strong>Settings</strong>
                                    <ul>
                                        ${data.settings.length > 0 
                                            ? data.settings.map(d => `<li>${d.name}</li>`).join('') 
                                            : '<li>No settings available</li>'
                                        }
                                    </ul>
                                </div>
                            </div>
                        </div>
                    `;
                    L.marker(data.coords)
                        .addTo(map)
                        .bindPopup(popupContent);
                });
            });
        }
    });

    core.action_registry.add("map_scce_tag", MapScce);
    return MapScce;
});

