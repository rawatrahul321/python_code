odoo.define('website_shipping_address.portal_my_details', function(require) {
"use strict";
$(document).on('ready', function (ev) {
        // var state_options = $("select[name='area_id']:enabled option:not(:first)");
        // $(".checkout_autoformat").on('change', "select[name='state_id']", function(e) {
        //     var select = $("select[name='area_id']");
        //     state_options.detach();
        //     var displayed_state = state_options.filter("[data-state_id="+($(this).val() || 0)+"]");
        //     $(select).append(displayed_state);
        // });
        // $(".phone_input").bind('keypress',function (e) {
        //     if (String.fromCharCode(e.keyCode).match(/[^0-9]/g)) return false;
        // });
        if($('#oe_signup_form').length){
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
        // $('input[name="firstname"]').on('change', function(ev) {
        //     $('input[name="name"]').val($(ev.currentTarget).val() + ' ' + $('input[name="lastname"]').val());
        // });
        // $('input[name="lastname"]').on('change', function(ev) {
        //     $('input[name="name"]').val($('input[name="firstname"]').val() + ' ' + $(ev.currentTarget).val());
        // });
    });
});

odoo.define('website_shipping_address.portal_my_details2', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var dom = require('web.dom');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var utils = require('web.utils');
    var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
    var core = require('web.core');
    var config = require('web.config');
    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.WebsiteSaleExtended = sAnimations.Class.extend(ProductConfiguratorMixin, {
        selector: '.oe_website_sale',
        read_events: {
            'change select[name="state_id"]': '_onChangeState',
            'change select[name="country_id"]': '_onCountry',
        },
        init: function () {
            this._super.apply(this, arguments);
            this.isWebsite = true;
        },
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        _onCountry: function (ev) {
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
                var selectAreas = $("select[name='area_id']");
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
                        if(data.areas.length) {
                            selectAreas.html('');
                            _.each(data.areas, function (x) {
                                var opt = $('<option>').text(x[1])
                                    .attr('value', x[0])
                                    .attr('data-code', x[2]);
                                selectAreas.append(opt);
                            });
                            selectAreas.val('').parent('div').removeClass('d-none');
                            selectAreas.parent('div').show();
                        }
                        else {
                            selectAreas.val('').parent('div').addClass('d-none');
                        }
                        selectAreas.data('init', 0);
                    } else {
                        selectStates.val('').parent('div').hide();
                        selectAreas.val('').parent('div').addClass('d-none');
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
                    var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                    _.each(all_fields, function (field) {
                        $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                    });
                }

            });
        },

        _onChangeState: function (ev) {
            if (!this.$('.checkout_autoformat').length) {
                return;
            }
            this._changeState();
        },
        _changeState: function () {
            if (!$("#state_id").val()) {
                return;
            }
            this._rpc({
                route: "/shop/state_info/" + $("#state_id").val(),
                params: {
                    mode: 'shipping',
                },
            }).then(function (data) {
                var selectAreas = $("select[name='area_id']");
//                // dont reload state at first loading (done in qweb)
                if (selectAreas.data('init')===0 || selectAreas.find('option').length===1) {
                    if (data.areas.length) {
                        selectAreas.html('');
                        _.each(data.areas, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectAreas.append(opt);
                        });
                        selectAreas.val('').parent('div').removeClass('d-none');
                        selectAreas.parent('div').show();
                    } else {
                        selectAreas.val('').parent('div').hide();
                    }
                    selectAreas.data('init', 0);
                } else {
                    selectAreas.data('init', 0);
                }

            });
        },

    });
});