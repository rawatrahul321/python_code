/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('geoip_redirect.wk_geoip', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
    var addLatLong = { lat: 28.4667, lng: 77.0333 };

    $(document).ready(function() {        
        var marker = '';
        var drag = false;
        var change_condition = true;
        var map = '';
        var markers = [];

        function initialize() {
            map = new google.maps.Map(document.getElementById('address_map'), {
                zoom: 10,
                center: addLatLong
            });
            var country = '';
            google.maps.event.addListener(map, 'click', function(event) {
                var myLatLng = event.latLng;
                change_condition = false;
                addMarker(event.latLng, map);
                setLocation(event, country);
                toggleBounce();
            });
            addMarker(addLatLong, map);
            var addCurr = getAddress();
            if (addCurr) {
                getLatLong(addCurr);
            } else {
               $.getJSON('http://api.petabyet.com/geoip/?callback', function(data) {
                    var currentLatitude = data.latitude;
                    var currentLongitude = data.longitude;
                    addLatLong = { lat: currentLatitude, lng: currentLongitude };
                    map.setCenter(addLatLong)
                    addMarker(addLatLong, map);
                });
            }
        }

        function addMarker(location, map) {
            deleteMarkers();
            marker = new google.maps.Marker({
                map: map,
                draggable: true,
                animation: google.maps.Animation.DROP,
                position: location
            });
            markers.push(marker);
            google.maps.event.addListener(marker, 'dragend', function(event) {
                toggleBounce();
                change_condition = true;
                drag = false;
            });
            var country = '';
            google.maps.event.addListener(marker,'drag',function(event) {
                change_condition = false;
                drag = true;
                setLocation(event, country);
            });
        }

        function toggleBounce() {
            if (marker.getAnimation() !== null) {
                marker.setAnimation(null);
            } else {
                marker.setAnimation(google.maps.Animation.BOUNCE);
            }
        }

        function deleteMarkers() {
            clearMarkers();
            markers = [];
        }
        function clearMarkers() {
            setMapOnAll(null);
        }

        function setMapOnAll(map) {
            for (var i = 0; i < markers.length; i++) {
                markers[i].setMap(map);
            }
        }

        function getAddress() {
            var address = '';
            
            var street = $("input[name='street']").val();
            if (street) {
                address = street;
            }
            var street2 = $("input[name='street2']").val();
            if (street2) {
                address = address + ", " + street2;
            }
            var city = $("input[name='city']").val();
            if (city) {
                address = address + ", " + city;
            }
            var state = $.trim($("select[name='state_id'] option:selected").text());
            if (state !='State / Province...') {
                address = address + ", " + state;
            }
            var country = $.trim($("select[name='country_id'] option:selected").text());
            if (country != 'Country...') {
                address = address + ", " + country;
            }
            var zip = $("input[name='zip']").val();
            if (zip) {
                address = address + ", " + zip;
            } else {
                zip = $("input[name='zipcode']").val();
                if (zip) {
                    address = address + ", " + zip;
                }
            }
            
            return address;
        }

        function getLatLong(address) {
           var geocoder = geocoder = new google.maps.Geocoder();
            geocoder.geocode( { 'address': address}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var latitude = results[0].geometry.location.lat();
                    var longitude = results[0].geometry.location.lng();
                    addLatLong = { lat: latitude, lng: longitude };
                    map.setCenter(addLatLong)
                    addMarker(addLatLong, map);
                }
            });
        }

        function setLocation(event, country) {
            var myLatLng = event.latLng;
            var lat = myLatLng.lat();
            var lng = myLatLng.lng();
            var latlng = new google.maps.LatLng(lat, lng);
            var geocoder = geocoder = new google.maps.Geocoder();
            geocoder.geocode({ 'latLng': latlng }, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                        var components = results[1].address_components;
                        var formatted_address = results[1].formatted_address;
                        var street = '';
                        var street2 = '';
                        var city = '';
                        var state = '';
                        var stateId = '';
                        var postalCode = '';
                        for (var i = 0, component; component = components[i]; i++) {
                                if (component.types[0] == 'country') {
                                    if (country != component.long_name) {
                                        country = component.long_name;
                                        $("select[name='country_id'] option").each(function() {
                                            if ($.trim($(this).text()) == country) {
                                                $("select[name='country_id']").val($(this).val());
                                            }
                                        });
                                    } else {
                                        country = component.long_name;
                                    }
                                } else if (component.types[0] == 'administrative_area_level_1') {
                                    state = component.long_name;
                                } else if (component.types[0] == 'locality') {
                                    city = component.long_name;
                                } else if (component.types[0] == 'postal_code') {
                                    postalCode = component.long_name;
                                } else {
                                    if (!street) {
                                        street = component.long_name;
                                    } else {
                                        if (street2) {
                                            street2 = street2 + ", " + component.long_name;
                                        } else {
                                            street2 = component.long_name;
                                        }                                            
                                    }
                                }
                            }
                        $("select[name='state_id'] option").each(function() {
                            var stateval = $.trim($(this).text());
                            if (stateval == state) {
                                stateId = $(this).val();
                            }
                        });
                        $("input[name='street']").val(street);
                        $("input[name='street2']").val(street2);
                        $("input[name='city']").val(city);
                        $("input[name='zip']").val(postalCode);
                        $("select[name='state_id']").val(stateId);
                        if (!drag) {
                            change_condition = true;
                        }
                    }
                }
            });
        }

        $("select[name='country_id']").on("change", function (event) {
            if (change_condition) {
                getLatLong(getAddress());
            }
        });

        $("select[name='state_id']").on("change", function (event) {
           getLatLong(getAddress());
        });

        $("input[name='city']").bind('input propertychange', function() {
           getLatLong(getAddress());
        });

        $("input[name='street']").bind('input propertychange', function() {
           getLatLong(getAddress());
        });

        $("input[name='street2']").bind('input propertychange', function() {
           getLatLong(getAddress());
        });

        google.maps.event.addDomListener(window, 'load', initialize);
        if($(document).find('#address_map').length){
           initialize();
        }
    });

})