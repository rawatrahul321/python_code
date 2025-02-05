odoo.define('pos_order_display',function(require) {
"use strict";

var gui = require('point_of_sale.gui');
var chrome = require('point_of_sale.chrome');
var popups = require('point_of_sale.popups');
var core = require('web.core');
var models = require('point_of_sale.models');
var rpc = require('web.rpc');
var PosModelSuper = models.PosModel;
var pos_screens = require('point_of_sale.screens');
/*var Model = require('web.DataModel');*/
var QWeb = core.qweb;
var _t = core._t;

models.PosModel = models.PosModel.extend({
    _save_to_server: function (orders, options) {
        var result_new = PosModelSuper.prototype._save_to_server.call(this, orders, options);
        var self = this;
        var new_order = {};
        var order_list = self.pos_orders;
        var order_list_new = self.order;
        // var order_list_new = self.list_orders;
        for (var i in orders) {
            var partners = self.partners;
            var partner = "";
            for(var j in partners){
                if(partners[j].id == orders[i].data.partner_id){
                    partner = partners[j].name;
                }
            }
            new_order = {
                'amount_tax': orders[i].data.amount_tax,
                'amount_total': orders[i].data.amount_total,
                'pos_reference': orders[i].data.name,
                'return_ref': orders[i].data.return_ref,
                'return_status':orders[i].data.return_status,
                'partner_id': [orders[i].data.partner_id, partner],
                'session_id': [
                    self.pos_session.id, self.pos_session.name
                ]
            };
            order_list.push(new_order);
            order_list_new.push(new_order);
            self.pos_orders = order_list;
            self.order = order_list_new;
            self.gui.screen_instances.OldOrdersWidget.render_list(order_list);
            // self.gui.screen_instances.ReturnOrdersWidget.render_list(order_list);
            self.gui.screen_instances.ReturnOrdersWidget.render_list(order_list_new);
        }
        return result_new;
    },
});

});