odoo.define('caret_united18_website.website_sale', function (require) {
"use strict";

var ajax = require('web.ajax');
var Widget = require('web.Widget');
var core = require('web.core');

    $(document).ready(function () {
        $("#check_product_qty").on('click', function(event) {
            ajax.jsonRpc("/check/product_qty", 'call', {}).then(function (data) {
                if (data){
                    event.preventDefault();
                    for (var i in data) {
                        $(".product_qty_warning").prepend('<p>'+i+': '+data[i]+'</p>');
                    }
                    $('#quantity_warning').modal("show");
                 }
                else{
                    window.location.replace('checkout','');
                }
            });
        });
        $(".direct_add_to_cart").on('click', function(o) {
            var prod_id = $(this).attr('id')
            var is_restrict = $(this).closest('form').find('input[name="is_restrict"]').val()
            var restrict_qty = parseInt($(this).closest('form').find('input[name="restrict_qty"]').val())
            var website_product_qty_restrict = $(this).closest('form').find('input[name="website_product_qty_restrict"]').val()

            var pro_qty = parseInt($(this).closest('form').find('input[name="add_qty"]').val())
            var available_qty = parseInt($(this).closest('form').find('input[name="available_quantity"]').val())
            var prod_spec = $(this).closest('form').find('input[name="product_spec"]').val()
            if (available_qty >= pro_qty) {
                if (!website_product_qty_restrict){
                    ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':pro_qty, 'prod_spec':prod_spec}).then(function (data) {
                        if (data){
                                 window.location.reload();
                                }
                    });
                }
                else if (!is_restrict){
                    ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':pro_qty, 'prod_spec':prod_spec}).then(function (data) {
                        if (data){
                                 window.location.reload();
                                }
                    });
                }
                else if (is_restrict && (restrict_qty >= pro_qty)) {
                    ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':pro_qty, 'prod_spec':prod_spec}).then(function (data) {
                        if (data){
                                 window.location.reload();
                                }
                    });
                }
                else {
                    $(this).closest('form').find('input[name="add_qty"]').val(restrict_qty || 0);
                }
            }
            else {
                  $(this).closest('form').find('input[name="add_qty"]').val( available_qty );
            }
        });

        $(".direct_buy").on('click', function(o){
            var is_restrict = $(this).closest('form').find('input[name="is_restrict"]').val()
            var restrict_qty = parseInt($(this).closest('form').find('input[name="restrict_qty"]').val())
            var website_product_qty_restrict = $(this).closest('form').find('input[name="website_product_qty_restrict"]').val()
            var prod_id = $(this).attr('id')
            var pro_qty = parseInt($(this).closest('form').find('input[name="add_qty"]').val())
            var available_qty = parseInt($(this).closest('form').find('input[name="available_quantity"]').val())
            var prod_spec = $(this).closest('form').find('input[name="product_spec"]').val()
            if (available_qty >= pro_qty) {
                if (!website_product_qty_restrict){
                    ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':pro_qty, 'prod_spec':prod_spec}).then(function (data) {
                        var url = window.location.href;
                        if(url.indexOf('?debug') != -1){
                            var newurl = url.replace('?debug', '');
                            var split_url = newurl.split("shop")[0]
                            window.location = split_url + "shop/cart?debug";
                        }
                        else{
                            var split_url = url.split("shop")[0]
                            window.location = split_url + "shop/cart";
                        }
                    });
                }
                else if (!is_restrict){
                    ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':pro_qty, 'prod_spec':prod_spec}).then(function (data) {
                        var url = window.location.href;
                        if(url.indexOf('?debug') != -1){
                            var newurl = url.replace('?debug', '');
                            var split_url = newurl.split("shop")[0]
                            window.location = split_url + "shop/cart?debug";
                        }
                        else{
                            var split_url = url.split("shop")[0]
                            window.location = split_url + "shop/cart";
                        }
                    });
                }
                else if (is_restrict && (restrict_qty >= pro_qty)) {
                    ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':pro_qty, 'prod_spec':prod_spec}).then(function (data) {
                        var url = window.location.href;
                        if(url.indexOf('?debug') != -1){
                            var newurl = url.replace('?debug', '');
                            var split_url = newurl.split("shop")[0]
                            window.location = split_url + "shop/cart?debug";
                        }
                        else{
                            var split_url = url.split("shop")[0]
                            window.location = split_url + "shop/cart";
                        }
                    });
                }
                else {
                  $(this).closest('form').find('input[name="add_qty"]').val( restrict_qty || 0 );
                }
            }
            else {
                  $(this).closest('form').find('input[name="add_qty"]').val( available_qty );
            }
        });

        $(".cart-prod-note").on('change', function(o){
            var prod_id = $(this).attr('id')
            var prod_spec = $(this).closest('.form-group').find('input[name="product_spec_cart"]').val()
            ajax.jsonRpc("/shop/cart/add_to_cart/update", 'call', {'prod_id':prod_id, 'pro_qty':0, 'prod_spec':prod_spec}).then(function (data) {
                if (data){
                    window.location.reload();
                   }
            });
        });
        
    });
});
