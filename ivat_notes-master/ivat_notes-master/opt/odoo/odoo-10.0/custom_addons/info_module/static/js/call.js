odoo.define('info_module.call', function(require){
 "use strict"
var Widget = require('web.Widget');
    var core = require('web.core');
    var web_client = require('web.web_client');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');

    var MessageOfTheDay = Widget.extend({
        template: "MessageOfTheDay",
        start: function() {
            var self = this;
            return new instance.web.Model("info_module.mrp.workorder")
                .query(["message"])
                .order_by('-create_date', '-id')
                .first()
                .then(function(result) {
                	console.log("dsaaaaaaaaaaaaaaaaaaaaaaa")
                    self.$(".oe_mywidget_message_of_the_day").text(result.message);
                });
        },
    });

    var HomePage = AbstractAction.extend(ControlPanelMixin.{
        template: "HomePage",
        start: function() {
            var messageofday = new MessageOfTheDay(this)
            messageofday.appendTo(this.$el);
        },
    });
    core.action_registry.add('message.homepage', HomePage);

})
;