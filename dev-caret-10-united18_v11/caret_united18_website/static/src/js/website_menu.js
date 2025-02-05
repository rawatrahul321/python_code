odoo.define('caret_united18_website.website_menu', function (require) {
"use strict";

var Widget = require('web.Widget');
var chat_manager = require('mail.chat_manager');
var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');

var WebsiteMenu = Widget.extend({
    template:'WebsiteMenu',
    events: {
        "click": "_onMenuClick",
    },
    _onMenuClick: function(){
       this.do_action('goto_website');
    },
});
SystrayMenu.Items.push(WebsiteMenu);

return WebsiteMenu;
});