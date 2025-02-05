odoo.define('caret_united18_pos.CaretPosModel', function(require){
"use strict";


    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var _super_posmodel = models.PosModel.prototype;
    var models_update = models.PosModel.prototype.models;
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');

    var _t = core._t;
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    for(var i=0; i<models_update.length; i++){
        var model=models_update[i];
        if(model.model === 'res.company'){
             model.fields.push('street');
             model.fields.push('street2');
             model.fields.push('city');
             model.fields.push('zip');
             model.fields.push('state_id');

        } 
    }

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            partner_model.fields.push('qty_available','final_sales_price','type');
            partner_model.domain.push('|', ['qty_available','>',0], ['name','=ilike','Discount']);
            var res_partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            res_partner_model.domain.push(['company_id','=',session.company_id]);
            return _super_posmodel.initialize.call(this, session, attributes);
        },
        load_new_partners: function(){
        var self = this;
        var def  = new $.Deferred();
        var fields = _.find(this.models,function(model){ return model.model === 'res.partner'; }).fields;
        var domain = [['customer','=',true],['company_id','=',self.config.company_id[0]],['write_date','>',this.db.get_partner_write_date()]];
        rpc.query({
                model: 'res.partner',
                method: 'search_read',
                args: [domain, fields],
            }, {
                timeout: 3000,
                shadow: true,
            })
            .then(function(partners){
                if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
                    def.resolve();
                } else {
                    def.reject();
                }
            }, function(type,err){ def.reject(); });
        return def;
        }

    });

    var PosModelSuper = models.PosModel;

    models.PosModel = models.PosModel.extend({
        refresh_qty_available:function(product){
            var $elem = $("[data-product-id='"+product.id+"'] .qty-tag");
            $elem.html(product.qty_available);
            if (product.qty_available <= 0 && !$elem.hasClass('not-available')){
                $elem.addClass('not-available');
            }
        },
        push_order: function(order, opts){
            var self = this;
            var pushed = PosModelSuper.prototype.push_order.call(this, order, opts);
            if (order){
                order.orderlines.each(function(line){
                    var product = line.get_product();
                    product.qty_available -= line.get_quantity();
                    self.refresh_qty_available(product);
                });
            }
            return pushed;
        },
        push_and_invoice_order: function(order){
            var self = this;
            var invoiced = PosModelSuper.prototype.push_and_invoice_order.call(this, order);

            if (order && order.get_client()){
                if (order.orderlines){
                    order.orderlines.each(function(line){
                        var product = line.get_product();
                        product.qty_available -= line.get_quantity();
                        self.refresh_qty_available(product);
                    });
                } else if (order.orderlines){
                    order.orderlines.each(function(line){
                        var product = line.get_product();
                        product.qty_available -= line.get_quantity();
                        self.refresh_qty_available(product);
                    });
                }
            }

            return invoiced;
        },
        _save_to_server: function (orders, options) {
        self = this;
        if (!orders || !orders.length) {
            var result = $.Deferred();
            result.resolve([]);
            return result;
        }

        options = options || {};

        var self = this;
        var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;
        var order_ids_to_sync = _.pluck(orders, 'id');
        var args = [_.map(orders, function (order) {
                order.to_invoice = options.to_invoice || false;
                return order;
            })];
        return rpc.query({
                model: 'pos.order',
                method: 'create_from_ui',
                args: args,
            }, {
                timeout: timeout,
                shadow: !options.to_invoice
            })
            .then(function (server_ids) {
                _.each(order_ids_to_sync, function (order_id) {
                    self.db.remove_order(order_id);
                    self.send_SMS(order_id);
                });
                self.set('failed',false);
                return server_ids;
            }).fail(function (type, error){
                if(error.code === 200 ){
                    if (error.data.exception_type == 'warning') {
                        delete error.data.debug;
                    }
                    if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
                        self.gui.show_popup('error-traceback',{
                            'title': error.data.message,
                            'body':  error.data.debug
                        });
                    }
                    self.set('failed',error);
                }
                console.error('Failed to send orders:', orders);
            });
        },
        send_SMS: function(order_id){
        var args = [order_id];
        return rpc.query({
                model: 'pos.order',
                method: 'send_order_sms',
                args: args,
            });
        },
    });
    var PosModelProduct = models.Product;

    models.Product = models.Product.extend({
        get_price: function(pricelist, quantity){
            var self = this;
            var price = PosModelProduct.prototype.get_price.call(this, pricelist,quantity);
            var price = self.final_sales_price;
            return price;
        },
    });

    var PosModelOrderline = models.Orderline;

    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity, keep_price){
            var quant = parseFloat(quantity) || 0;
            var product = this.get_product();
            if (product.qty_available < quant && product.type != "service") {
                this.pos.gui.show_popup('error',_t('Do not Allowed to add Quantity more than Available Quantity'));
                return;
            }
            else {
                return PosModelOrderline.prototype.set_quantity.call(this, quantity, keep_price);
            }
        }
    });

    models.Order = models.Order.extend({
        get_total_tax_details: function(){
            var tax_details = this.get_tax_details();
            var tax_full_details = [];
            var cgst = 0;
            var sgst = 0;
            var igst = 0;
            var other = 0;
            var other_tax_name = '';
            for (var tax in tax_details) {
                var detail = tax_details[tax];
                if(detail.name.match(/CGST/gi)){
                    cgst += detail.amount;
                }
                else if(detail.name.match(/SGST/gi)){
                    sgst += detail.amount;
                }
                else if(detail.name.match(/IGST.*/)){
                    igst += detail.amount;
                }
                else{
                    other += detail.amount;
                    other_tax_name = detail.name;
                }
            }
            tax_full_details.push({amount: cgst, name: 'CGST'},
                                  {amount: sgst, name: 'SGST'},
                                  {amount: igst, name: 'IGST'},
                                  {amount: other, name: other_tax_name}
                                );
            return tax_full_details
        }
    });
});
