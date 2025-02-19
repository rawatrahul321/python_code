odoo.define('product_return_pos',function(require){
"use strict";

var gui = require('point_of_sale.gui');
var chrome = require('point_of_sale.chrome');
var popups = require('point_of_sale.popups');
var core = require('web.core');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var models = require('point_of_sale.models');
var PosModelSuper = models.PosModel;
var pos_screens = require('point_of_sale.screens');
var rpc = require('web.rpc');
var QWeb = core.qweb;
var _t = core._t;

var today = new Date();
var todayDate = today.getFullYear() +"-"+
            (today.getMonth()+1) +"-"+
            today.getDate() +" "+
            today.getHours() +":"+
            today.getMinutes() +":"+
            today.getSeconds();
var prior = new Date(new Date().setDate(new Date().getDate() - 30));
var priorDate = prior.getFullYear() +"-"+
            (prior.getMonth()+1) +"-"+
            prior.getDate() +" "+
            prior.getHours() +":"+
            prior.getMinutes() +":"+
            prior.getSeconds();

PosModelSuper.prototype.models.splice(10, 0, {
    model: 'pos.order',
    fields: ['id', 'name', 'session_id', 'pos_reference', 'partner_id', 'return_status', 'amount_total','lines', 'amount_tax', 'return_ref', 'date_order'],
    domain: function(self){ return [['state','in',['done','invoiced','paid','draft','cancel']],
        ['company_id','=',self.user.company_id[0]], ['date_order', '>=', priorDate], ['date_order', '<=', todayDate]]; },
    loaded: function (self, pos_orders) {
        var orders = [];
        for (var i in pos_orders){
            orders[pos_orders[i].id] = pos_orders[i];
        }
        self.pos_orders = orders;
        self.order = [];
        // self.list_orders = [];
        for (var i in pos_orders){
            self.order[pos_orders[i].id] = pos_orders[i];
            // self.order[i] = pos_orders[i];
        }

        var domain = [
            ['date_order', '>=', priorDate],
            ['date_order', '<=', todayDate]
        ];
        // rpc.query({
        //     model: 'pos.order',
        //     method: 'search_read',
        //     fields: ['id', 'name', 'session_id', 'pos_reference', 'partner_id', 'return_status', 'amount_total','lines', 'amount_tax', 'return_ref', 'date_order'],
        //     domain: domain,
        // }).then(function(result){
        //     self.list_orders = result;
        // });
    },
});

var DomCache = core.Class.extend({
        init: function(options){
            options = options || {};
            this.max_size = options.max_size || 2000;

            this.cache = {};
            this.access_time = {};
            this.size = 0;
        },
        cache_node: function(key,node){
            var cached = this.cache[key];
            this.cache[key] = node;
            this.access_time[key] = new Date().getTime();
            if(!cached){
                this.size++;
                while(this.size >= this.max_size){
                    var oldest_key = null;
                    var oldest_time = new Date().getTime();
                    for(key in this.cache){
                        var time = this.access_time[key];
                        if(time <= oldest_time){
                            oldest_time = time;
                            oldest_key  = key;
                        }
                    }
                    if(oldest_key){
                        delete this.cache[oldest_key];
                        delete this.access_time[oldest_key];
                    }
                    this.size--;
                }
            }
            return node;
        },
        clear_node: function(key) {
            var cached = this.cache[key];
            if (cached) {
                delete this.cache[key];
                delete this.access_time[key];
                this.size --;
            }
        },
        get_node: function(key){
            var cached = this.cache[key];
            if(cached){
                this.access_time[key] = new Date().getTime();
            }
            return cached;
        },
    });

var ReturnButton = pos_screens.ActionButtonWidget.extend({
    template: 'ReturnButton',
    button_click: function(){
        if (this.pos.get_order().get_orderlines().length === 0){
             this.gui.show_screen('ReturnOrdersWidget');
        }
        else{
          this.gui.show_popup('error',{
                title :_t('Process Only one operation at a time'),
                body  :_t('Process the current order first'),
            });
        }
    },
});

pos_screens.define_action_button({
    'name': 'Return',
    'widget': ReturnButton,
    'condition': function(){
        return this.pos;
    },
});

// models.PosModel = models.PosModel.extend({
//     _save_to_server: function (orders, options) {
//         var result_new = PosModelSuper.prototype._save_to_server.call(this, orders, options);
//         var self = this;
//         var new_order = {};
//         var orders_list = self.pos_orders;

//         for (var i in orders) {
//             var partners = self.partners;
//             var partner = "";
//             for(var j in partners){
//                 if(partners[j].id == orders[i].data.partner_id){
//                     partner = partners[j].name;
//                 }
//             }
//             new_order = {
//                 'amount_tax': orders[i].data.amount_tax,
//                 'amount_total': orders[i].data.amount_total,
//                 'pos_reference': orders[i].data.name,
//                 'return_ref': orders[i].data.return_ref,
//                 'partner_id': [orders[i].data.partner_id, partner],
//                 'return_status':orders[i].data.return_status,
//                 'session_id': [
//                     self.pos_session.id, self.pos_session.name
//                 ]
//             };
//             orders_list.push(new_order);
//             self.pos_orders = orders_list;
//             self.gui.screen_instances.ReturnOrdersWidget.render_list(orders_list);
//         }
//         return result_new;
//     },
// });

var ReturnOrdersWidget = pos_screens.ScreenWidget.extend({
    template: 'ReturnOrdersWidget',

    init: function(parent, options){
        this._super(parent, options);
        this.order_cache = new DomCache();
        this.order_string = "";
        this.pos_reference = "";
        this.customer_string = "";
        this.mobile_string = "";
    },

    auto_back: true,
    renderElement: function () {
        this._super(this);
        var self = this;

    },

    show: function(){
        var self = this;
        this._super();

        this.renderElement();
        this.details_visible = false;

        this.$('.back').click(function(){
            self.gui.back();
        });
        // var pos_orders = this.pos.pos_orders;
        // var pos_orders = this.pos.order;
        // this.render_list(pos_orders);
        // this.render_list(this.pos.list_orders);
        this.render_list(this.pos.order);

        var search_timeout = null;

        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
            this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            this.chrome.widget.keyboard.connect(this.$('.customer-searchbox input'));
            this.chrome.widget.keyboard.connect(this.$('.mobile-searchbox input'));
        }
        this.$('.searchbox input').on('keypress',function(event){
            clearTimeout(search_timeout);
            var query = this.value;
            search_timeout = setTimeout(function(){
                self.perform_search(query,event.which === 13);
            },70);
        });

        this.$('.searchbox .search-clear').click(function(){
            self.clear_search();
        });
        this.$('.customer-searchbox input').on('keypress',function(event){
            clearTimeout(search_timeout);
            var query = this.value;
            search_timeout = setTimeout(function(){
                self.customer_perform_search(query,event.which === 13);
            },70);
        });

        this.$('.customer-searchbox .customer-search-clear').click(function(){
            self.customer_clear_search();
        });

        this.$('.mobile-searchbox input').on('keypress',function(event){
            clearTimeout(search_timeout);
            var query = this.value;
            search_timeout = setTimeout(function(){
                self.mobile_perform_search(query,event.which === 13);
            },70);
        });

        this.$('.mobile-searchbox .mobile-search-clear').click(function(){
            self.mobile_clear_search();
        });
    },
    hide: function () {
        this._super();
        this.new_client = null;
    },
    perform_search: function(query, associate_result){
        var new_orders;
        if(query){
            new_orders = this.search_order(query);

            this.render_list(new_orders);
        }else{
            // var orders = this.pos.pos_orders;
            var orders = this.pos.order;
            this.render_list(orders);
        }
    },
    search_order: function(query){
        var self = this;
        // var orders = this.pos.pos_orders;
        var orders = this.pos.order;
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(' ','.+');
            var re = RegExp("([0-9]+):.*?"+query,"gi");
        }catch(e){
            return [];
        }
        var results = [];
        for(var i = 0, len = orders.length; i < len; i++){
            var r = re.exec(this.order_string);
            if(r){
                var id = Number(r[1]);
                results.push(this.get_order_by_id(id));
            }else{
                break;
            }
        }
        return results;
    },
    // returns the order with the id provided
    get_order_by_id: function (id) {
        // return this.pos.pos_orders[id];
        return this.pos.order[id];
    },
    clear_search: function(){
        // var orders = this.pos.pos_orders;
        // var orders = this.pos.order;
        // var orders = this.pos.list_orders;
        var orders = this.pos.order;
        this.render_list(orders);
        this.$('.searchbox input')[0].value = '';
        this.$('.searchbox input').focus();
    },
    customer_perform_search: function(query, associate_result){
        var new_orders;
        if(query){
            new_orders = this.customer_search_order(query);

            this.render_list(new_orders);
        }else{
            // var orders = this.pos.pos_orders;
            var orders = this.pos.order;
            this.render_list(orders);
        }
    },
    customer_search_order: function(query){
        var self = this;
        // var orders = this.pos.pos_orders;
        var orders = this.pos.order;
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(' ','.+');
            var re = RegExp("([0-9]+):.*?"+query,"gi");
        }catch(e){
            return [];
        }
        var results = [];
        for(var i = 0, len = orders.length; i < len; i++){
            var r = re.exec(this.customer_string);
            if(r){
                var id = Number(r[1]);
                results.push(this.get_order_by_id(id));
            }else{
                break;
            }
        }
        return results;
    },
    customer_clear_search: function(){
        // var orders = this.pos.pos_orders;
        // var orders = this.pos.list_orders;
        var orders = this.pos.order;
        this.render_list(orders);
        this.$('.customer-searchbox input')[0].value = '';
        this.$('.customer-searchbox input').focus();
    },
    mobile_perform_search: function(query, associate_result){
        var new_orders;
        if(query){
            new_orders = this.mobile_search_order(query);

            this.render_list(new_orders);
        }else{
            var orders = this.pos.order;
            this.render_list(orders);
        }
    },
    mobile_search_order: function(query){
        var self = this;
        var orders = this.pos.order;
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(' ','.+');
            var re = RegExp("([0-9]+):.*?"+query,"gi");
        }catch(e){
            return [];
        }
        var results = [];
        for(var i = 0, len = orders.length; i < len; i++){
            var r = re.exec(this.mobile_string);
            if(r){
                var id = Number(r[1]);
                results.push(this.get_order_by_id(id));
            }else{
                break;
            }
        }
        return results;
    },
    mobile_clear_search: function(){
        // var orders = this.pos.order;
        // var orders = this.pos.list_orders;
        var orders = this.pos.order;
        this.render_list(orders);
        this.$('.mobile-searchbox input')[0].value = '';
        this.$('.mobile-searchbox input').focus();
    },
    render_list: function(orders){
        var self = this;
        for(var i = 0, len = orders.length; i < len; i++) {
            if (orders[i]) {
                var order = orders[i];
                var partner = self.pos.db.get_partner_by_id(order.partner_id[0]);
                self.order_string += i + ':' + order.pos_reference + '\n';
                self.customer_string += i + ':' + order.partner_id[1] + '\n';
                if (partner){
                    self.mobile_string += i + ':' + partner.mobile + '\n';
                }
            }
        }
        this.$('.order-list-lines').delegate('.return-button','click',function(event){

            var pos_ref = $(this).data('id');
            var order_new = null;
            for(var i = 0, len = orders.length; i < len; i++) {
                if (orders[i] && orders[i].pos_reference == pos_ref) {
                    order_new = orders[i];
                }
            }
            // $('span.searchbox').css('display', 'none');
            $('.button.return').css('display', 'block');
            self.pos_reference = order_new.pos_reference;
            if (order_new.return_ref){
                  self.gui.show_popup('error',_t('This is a returned order'));
                  self.gui.show_popup('error',{
                    title :_t('Cannot Return'),
                    body  :_t('This order is a returned order'),
                });
            }
            else{
                rpc.query({
                    model: 'pos.order',
                    method: 'get_status',
                    args: [order_new.pos_reference],
                }).then(function(result){
                    if (result){
                          self.gui.show_popup('OrderReturnWidget',{
                            ref: pos_ref
                        });
                    }
                    else{
                        self.gui.show_popup('error',{
                            title :_t('Fully Returned Order'),
                            body  :_t('This order is fully returned'),
                        });
                    }
                });
            }
        });

        var contents = this.$el[0].querySelector('.order-list-lines');
        if (contents){
            contents.innerHTML = "";
            for(var i = 0, len = orders.length; i < len; i++) {
                if (orders[i]) {
                    var order = orders[i];
                    var orderline = this.order_cache.get_node(order.id);
                    if (!orderline) {
                        var clientline_html = QWeb.render('OrderLines', {widget: this, order: order});
                        var orderline = document.createElement('tbody');
                        orderline.innerHTML = clientline_html;
                        orderline = orderline.childNodes[1];
                        if (order.id){
                            this.order_cache.cache_node(order.id, orderline);
                        }
                        else{
                            this.order_cache.cache_node(i, orderline);
                        }
                    }
                    contents.appendChild(orderline);
                }
            }
        }
    },

    close: function(){
        this._super();
    },
});
var OrderReturnWidget = PosBaseWidget.extend({
    template: 'OrderReturnWidget',

    init: function(parent, options){
        this._super(parent, options);
        this.order_cache = new DomCache();
        this.ordernes = "";
        this.pos_reference = "";
        this.client ="";
    },
    show: function (options) {
        var self = this;
        this._super(options);
        var pos_orders = this.pos.pos_orders;
        this.render_list(options);

    },
    close: function(){
        if (this.pos.barcode_reader) {
            this.pos.barcode_reader.restore_callbacks();
        }
    },
    events: {
        'click .button.cancel':  'click_cancel',
        'click .button.confirm': 'click_confirm',
    },

    render_list:function(options){
        var order_new = null;
        $("#table-body").empty();
        $("#disc-table-body").empty();
        var lines = [];
        this.pos_reference = options.ref
        rpc.query({
            model: 'pos.order',
            method: 'get_lines',
            args: [options.ref],
        }).then(function(result){
            lines = result[0];
            this.client = result[1];
            if (lines.length == 1){
                for(var l=0;l < 1; l++){
                    var lineId = lines[l];
                    if (lineId.product == 'Discount'){
                        alert("This order is fully returned")
                        return;
                    }
                }

            }
            $("#table-body").empty();
            for(var j=0;j < lines.length; j++){
                var product_line = lines[j];
                var rows = "";
                var discrows = "";
                var id = product_line.product_id
                var price_unit = product_line.price_unit;
                var name =product_line.product;
                var qty = product_line.qty;
                var line_id = product_line.line_id;
                var discount = product_line.discount;
                var isDiscount = false
                if (name == 'Discount'){
                    discrows += "<tr><td>" + id + "</td><td>" + "Total Discount" +"</td><td>" + Math.abs(price_unit) + "</td></tr>";
                    $(discrows).appendTo("#discount tbody");
                    isDiscount = true
                    var tab = document.getElementById('discount');
                    var discrows = tab.getElementsByTagName("tr");
                    for (var discrow = 0; discrow <1; discrow++) {
                         var disccols = discrows[discrow].cells;
                         disccols[0].style.display = 'none';
                    }
                }
                else{
                    rows += "<tr><td>" + id + "</td><td>" + price_unit +" </td><td>" + name + "</td><td>" + qty + "</td><td>" + discount + "</td><td>" + line_id + "</td></tr>";
                    $(rows).appendTo("#list tbody");
                    var rows = document.getElementById('list').rows;
                    for (var row = 0; row < rows.length; row++) {
                        var cols = rows[row].cells;
                        cols[0].style.display = 'none';
                        cols[1].style.display = 'none';
                        cols[5].style.display = 'none';
                    }
                }
            }

            var table = document.getElementById('list');
            var tr = table.getElementsByTagName("tr");
            for (var i = 1; i < tr.length; i++) {
              var td = document.createElement('td');
              var input = document.createElement('input');
              input.setAttribute("type", "text");
              input.setAttribute("value", 0);
              input.setAttribute("id", "text"+i);
              td.appendChild(input);
              tr[i].appendChild(td);
            }
            if (isDiscount == true){
                var disctable = document.getElementById('discount');
                var rownew = disctable.getElementsByTagName("tr");
                for (var x = 0; x <= rownew.length; x++) {
                    var disctd = document.createElement('td');
                    var inputNew = document.createElement('input');
                    inputNew.setAttribute("type", "text");
                    inputNew.setAttribute("value", 0);
                    inputNew.setAttribute("id", "newtext");
                    disctd.appendChild(inputNew);
                    rownew[x].appendChild(disctd);
                    break;
                }
            }
        });
    },
    click_confirm: function(){
        var self = this;
	    var myTable = document.getElementById('list').tBodies[0];
        var discTable = document.getElementById('discount').tBodies[0];
        var count = 0
        var c = 1
        for (var r=0, n = myTable.rows.length; r < n; r++) {
            var row = myTable.rows[r]
            var return_qty = document.getElementById("text"+c).value
            if (row.cells[3].innerHTML < return_qty){
                count +=1
            }
            c = c+1
        }
        if (count > 0){
             alert('Please check the Returned Quantity,it is higher than purchased')
        }
        else{
            var c = 1
            // OrderSuper.prototype.set_client.call(this, this.client);
            for (var r=0, n = myTable.rows.length; r < n; r++) {
                row = myTable.rows[r]
                var return_qty = document.getElementById("text"+c).value
                var product = this.pos.db.get_product_by_id(row.cells[0].innerHTML);
                if (!product) {
                    return;
                }
                if (return_qty > 0){
                    this.pos.get_order().add_product(product, {
                    price: row.cells[1].innerHTML,
                    quantity: -(return_qty),
                    discount:row.cells[4].innerHTML,
                    merge: false,
                    extras: {pos_ref: this.pos_reference,
                            label:row.cells[5].innerHTML},
                    });

                }
                c = c+1
        }
        }

        if (discTable.rows.length > 0){
            for (var dr=0; dr<1; dr++) {
                var discrow = discTable.rows[dr]
                var disc_amt = document.getElementById("newtext").value
                var discProduct = this.pos.db.get_product_by_id(discrow.cells[0].innerHTML);
                if (!discProduct) {
                    return;
                }
                if(disc_amt > 0){
                    this.pos.get_order().add_product(discProduct, {
                    price: disc_amt,
                    quantity: 1,
                    merge: false,
                    extras: {pos_ref: this.pos_reference},
                    });
                }
            }
        }
        this.gui.close_popup();
        self.gui.show_screen('products');
    },
     click_cancel: function(){
        this.gui.close_popup();
    },

});

var OrderSuper = models.Order;
models.Order = models.Order.extend({
    initialize: function(attributes,options){
        var order = OrderSuper.prototype.initialize.call(this, attributes,options);
        if (typeof(order) != 'undefined'){
            order.return_ref = '';
        }
        return order;
    },
    init_from_JSON: function(json) {
        OrderSuper.prototype.init_from_JSON.call(this, json);
        this.return_ref = json.return_ref;
    },
    export_as_JSON: function() {
        var json_new = OrderSuper.prototype.export_as_JSON.call(this);
        json_new.return_ref = this.get_return_ref();
        return json_new;
    },

    get_return_ref: function(){
         return this.return_ref;
    },

    add_product: function (product, options) {
        OrderSuper.prototype.add_product.call(this, product, options);
        var order    = this.pos.get_order();
        var last_orderline = this.get_last_orderline();
        if (options !== undefined){
            if(options.extras !== undefined){
                for (var prop in options.extras) {
                    if (prop ==='pos_ref'){
                        this.return_ref = options.extras['pos_ref']
                        this.trigger('change',this);
                        var self = this;
                        var curr_client = order.get_client();
                        if (!curr_client) {
                            rpc.query({
                                model: 'pos.order',
                                method: 'get_client',
                                args: [options.extras['pos_ref']],
                            }).then(function(result){
                                if (result){
                                    var partner = self.pos.db.get_partner_by_id(result);
                                    order.set_client(partner);

                                }
                            });
                        }
                    }
                    else if(prop ==='label'){
                        order.selected_orderline.set_order_line_id(options.extras['label']);
                    }
                }
            }
        }
    },
    });
var OrderlineSuper = models.Orderline;
models.Orderline = models.Orderline.extend({
    initialize: function(attr,options){
        OrderlineSuper.prototype.initialize.call(this, attr,options);
        this.line_id = '';
    },
    init_from_JSON: function(json) {
        OrderlineSuper.prototype.init_from_JSON.call(this, json);
        this.line_id  = json.line_id
    },
    clone: function(){
        var orderline = OrderlineSuper.prototype.clone.call(this);
        orderline.line_id = this.line_id;
        return orderline;
    },
    get_line_id: function(){
        return this.line_id;
    },
    set_order_line_id:function(id){
        this.line_id = id;
        this.trigger('change',this);
    },
    export_as_JSON: function(){
        var json = OrderlineSuper.prototype.export_as_JSON.apply(this,arguments);
        json.line_id = this.get_line_id();
        return json;
        },
});

gui.define_screen({name:'ReturnOrdersWidget', widget: ReturnOrdersWidget});
gui.define_popup({name:'OrderReturnWidget', widget: OrderReturnWidget});

});
