odoo.define('website_shipping_address.custom', function(require) {
"use strict";

// Dev one change address
// Note: Dev one: follow public widget is just inlcuded to hide country field
var publicWidget = require('web.public.widget');

// Dev one change Buy Now button issue
var session = require('web.session');
var sAnimations = require('website.content.snippets.animation');
var WebsiteSale = new sAnimations.registry.WebsiteSale();
// Dev one change Buy Now button issue end

publicWidget.registry.WebsiteSale.include({
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.$('.div_country').hide();
        });
    },
    /**
     * @private
     */
     _changeCountry: function () {
        if (!$("#country_id").val()) {
            return;
        }
        this._rpc({
            route: "/shop/country_infos/" + $("#country_id").val(),
            params: {
                mode: 'shipping',
            },
        }).then(function (data) {
            // placeholder phone_code
            //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

            // populate states and display
            var selectStates = $("select[name='state_id']");
            // dont reload state at first loading (done in qweb)
            if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                if (data.states.length) {
                    selectStates.html('');
                    _.each(data.states, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);
                        selectStates.append(opt);
                    });
                    selectStates.parent('div').show();
                } else {
                    selectStates.val('').parent('div').hide();
                }
                selectStates.data('init', 0);
            } else {
                selectStates.data('init', 0);
            }

            // manage fields order / visibility
            if (data.fields) {
                if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                    $(".div_zip").before($(".div_city"));
                } else {
                    $(".div_zip").after($(".div_city"));
                }
                // Dev one: remove country_name to avoid displaying country field for public user
                var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                if (session.is_website_user) {
                    all_fields = ["street", "zip", "city",]; // "state_code"];
                }
                _.each(all_fields, function (field) {
                    $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                });
            }
        });
    },
});
// Dev one change address end

$(document).ready(function (ev) {
        var state_options = $("select[name='area_id']:enabled option:not(:first)");
        $(".checkout_autoformat").on('change', "select[name='state_id']", function(e) {
            var select = $("select[name='area_id']");
            state_options.detach();
            var displayed_state = state_options.filter("[data-state_id="+($(this).val() || 0)+"]");
            $(select).append(displayed_state);
        });
        $(".phone_input").bind('keypress',function (e) {
            console.log('xxx',e)
            if (String.fromCharCode(e.keyCode).match(/[^0-9]/g)) return false;
        });
        if($('#oe_signup_form').length){
            console.log("\n\n\n $('#oe_signup_form')  ", $('#oe_signup_form'))
            $('button[type="submit"]').attr("disabled", true);
            $('input[name="login"]').on('keyup', function(ev) {
                var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
                if (emailReg.test( $(ev.currentTarget).val() )){
                    $('button[type="submit"]').attr("disabled", false);
                    $('.email-error').addClass('d-none');
                }
                else{
                    $('.email-error').removeClass('d-none');
                }
            });
        }

        // Dev one change address
        var isValidForm = function () {
            var requiredElements = $(".checkout_autoformat [required='True']");
            var valid = true;
            for (var i = 0; i < requiredElements.length; i++) {
                var $elem = $(requiredElements[i]);
                if (!$elem.val()) {
                    $elem.focus();
                    valid = false;
                    break;
                }
            }
            return valid;
        };

        if ($(".checkout_autoformat").length) {
            $(".checkout_autoformat .a-submit").on("click", function (ev) {
                if (!isValidForm()) {
                    ev.preventDefault();
                    ev.stopImmediatePropagation();
                    $(ev.currentTarget).removeClass('disabled');
                    if ($(".invalid-warning").length) {
                        $(".invalid-warning").remove();
                    }
                    $(".oe_cart h3.page-header").after($("<h4 class='text-danger invalid-warning'>Some required fields are empty.</h4>"));
                }
            });
            $("input[name='phone']").on("keydown", function (ev) {
                // Allow backspace, enter and tab
                if (ev.keyCode === 8 || ev.keyCode === 13 || ev.keyCode === 9) {
                    return true;
                }
//                if (String.fromCharCode(ev.keyCode).match(/[^0-9]/g)) return false;
                if ($(ev.currentTarget).val().length > 7) return false;
            });
            $("input[name='block']").on("keydown", function (ev) {
                // Allow backspace, enter and tab
                if (ev.keyCode === 8 || ev.keyCode === 13 || ev.keyCode === 9) {
                    return true;
                }
//                if (String.fromCharCode(ev.keyCode).match(/[^0-9]/g)) return false;
            });
        }
        // Dev one change address end


        // Dev one change Buy Now button issue
        if (!$('#ajax_cart_product_template').length) {
            $(document).on('click', '.oe_website_sale #buy_now', async function(ev){
                // if($('#add_to_cart').hasClass('quick-add-to-cart') || $('.a-submit').attr('optional-product') == 1) {
                //     ev.preventDefault();
                // } else {
                    var is_quick_view = $('#add_to_cart').hasClass('quick-add-to-cart');
                    if(!is_quick_view) {
                        ev.preventDefault();
                        WebsiteSale._onClickAdd(ev);
                    }
                // }
            });
        }
        // Dev one change Buy Now button issue end


//    For email verification
//        $('.email_verify').click(function (){
//            if ($("input[name='email']")[0].value){
//                console.log("IFIFIFIFIFIFIFIF")
//            } else {
//                alert("Email ID not found.")
//            }
//        });
    });
});