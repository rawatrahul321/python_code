odoo.define('payment_acquirer_knet.payment_acquirer_knet', function(require){
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    if ($.blockUI) {
        $.blockUI.defaults.css.border = '0';
        $.blockUI.defaults.css["background-color"] = '';
        $.blockUI.defaults.overlayCSS["opacity"] = '0.9';
    }

    var KNETPaymentForm = publicWidget.Widget.extend({
        init: function(){
            this._initBlockUI(_t("Redirecting to KNET Payment Gateway..."));
        },
        _initBlockUI: function(message) {
            if ($.blockUI) {
                $.blockUI({
                    'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                            '    <br />' + message +
                            '</h2>'
                });
            }
            $("#o_payment_form_pay").attr('disabled', 'disabled');
        },
    });

    new KNETPaymentForm();
});