odoo.define('website_language_switch_theme_clarico', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    var _t = core._t

    publicWidget.registry.cart_popup = publicWidget.Widget.extend({
        selector: '#wrapwrap',

        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self.get_template_values().then(function (content) {
                    self.content = content;
                });
            });
        },
        start: function () {
            var def = this._super.apply(this, arguments);
            if ($(".te_header_style_1_main").length) {
                this.$el.find('.te_header_1_right').append(this.content);
            } else if ($(".te_header_style_2_main").length) {
                this.$el.find('.te_login_right > div').append(this.content);
            } else if ($(".te_header_style_3_main").length) {
                this.$el.find('.te_login_right').append(this.content);
            } else if ($(".te_header_style_4_main").length) {
                this.$el.find('.te_login_right').append(this.content);
            } else if ($(".te_header_style_5_main").length) {
                this.$el.find('.te_header_before_right').append(this.content);
            } else if ($(".te_header_style_6_main").length) {
                this.$el.find('.te_header_before_right').append(this.content);
            } else if ($(".te_header_style_7_main").length) {
                this.$el.find('.te_header_right_icon').append(this.content);
            } else {
                this.$el.find('.te_header_right_icon').append(this.content);
            }
            return def;
        },

        get_template_values() {
            var url = window.location.href.split('?')[0];
            return ajax.post('/website_language_switch_theme_clarico/get_template_content' + window.location.search, {
                url: window.location.pathname,
            });
        }
    });

});