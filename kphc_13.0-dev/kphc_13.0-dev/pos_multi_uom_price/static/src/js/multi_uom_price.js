odoo.define('pos.multi_uom_price', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _super_orderline = models.Orderline.prototype;

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        scan_product: function(parsed_code) {
            var selectedOrder = this.get_order();
            var check_uom = false;
            for (var i = 0; i < this.product.length; i++) {
                if (parsed_code.base_code === this.product[i].barcode) {
                    var product_id = this.db.get_product_by_id(parseInt(this.product[i].pro_id[0]));
                    selectedOrder.add_product(product_id, {
                        price: this.product[i].price
                    });
                    var line = this.get_order().get_selected_orderline();
                    if (line.product.id === product_id.id) {
                        line.set_uom(this.product[i].uom_id);
                        line.set_unit_price(this.product[i].price);
                        line.price_manually_set = true;
                    }
                    check_uom = true;
                    break;
                }
            }
            var product = this.db.get_product_by_barcode(parsed_code.base_code);
            if (!check_uom) {
                if (!product) {
                    return false;
                }
                if (parsed_code.type === 'price') {
                    selectedOrder.add_product(product, {
                        price: parsed_code.value
                    });
                } else if (parsed_code.type === 'weight') {
                    selectedOrder.add_product(product, {
                        quantity: parsed_code.value,
                        merge: false
                    });
                } else if (parsed_code.type === 'discount') {
                    selectedOrder.add_product(product, {
                        discount: parsed_code.value,
                        merge: false
                    });
                } else {
                    selectedOrder.add_product(product);
                }
            }
            return true;
        },
    });

    //
    // At POS Startup, load the uom price
    //
    models.load_models({
        model: 'product.multi.uom.price',
        fields: ['uom_id', 'product_id', 'price', 'barcode', 'pro_id'],
        loaded: function(self, product) {
            //	    console.log(" 20 20 20 20 20 20 self = ", self);
            self.uom_price = {};
            if (product.length) {
                self.product = product;
                for (var i = 0; i < product.length; i++) {
                    if (!self.uom_price[product[i].product_id[0]]) {
                        self.uom_price[product[i].product_id[0]] = {};
                        self.uom_price[product[i].product_id[0]].uom_id = new Array();
                    }
                    self.uom_price[product[i].product_id[0]].uom_id[product[i].uom_id[0]] = product[i].price;
                }
            }
        },
    });
    //
    // EHF Extendemos el modelo Orderline con nuevas funciones
    //
    models.Orderline = models.Orderline.extend({
        // EHF Agregamos el uom a la raíz de la linea
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this, attr, options);
            if (options.json) {
                if (this.uom_id) {
                    return;
                } else {
                    this.uom_id = this.product.uom_id;
                    return;
                }
            }
            this.uom_id = options.product.uom_id;
        },
        // sustituimos la función original
        // regresamos la unidad de medida del producto que está en la raíz
        get_unit: function() {
            if (this.uom_id) {
                var unit_id = this.uom_id;
            } else {
                var unit_id = this.product.uom_id;
            }
            if (!unit_id) {
                return undefined;
            }
            unit_id = unit_id[0];
            if (!this.pos) {
                return undefined;
            }
            return this.pos.units_by_id[unit_id];
        },
        //cambiamos el uom del artículo
        set_uom: function(uom_id) {
            this.order.assert_editable();
            this.uom_id = uom_id;
            this.trigger('change', this);
        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.call(this);
            json.uom_id = this.uom_id[0];
            return json;
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this, arguments);
            this.uom_id = {
                0: this.pos.units_by_id[json.uom_id].id,
                1: this.pos.units_by_id[json.uom_id].name
            };
            this.price_manually_set = true;
        },
    });

    var UOMButton = screens.ActionButtonWidget.extend({
        template: 'UOMButton',
        button_click: function() {
            var list = [];
            var line = this.pos.get_order().get_selected_orderline();
            if (line) {
                var uom = line.pos.uom_price[line.product.product_tmpl_id];
                if (uom) {
                    var uom = Object.keys(uom.uom_id);
                    for (var i = 0; i < uom.length; i++) {
                        list.push({
                            label: line.pos.units_by_id[uom[i]].display_name,
                            item: uom[i]
                        });
                    }
                    this.gui.show_popup('selection', {
                        title: 'UOM',
                        list: list,
                        confirm: function(uom_id) {
                            uom_id = {
                                0: line.pos.units_by_id[uom_id].id,
                                1: line.pos.units_by_id[uom_id].name
                            };
                            line.set_uom(uom_id);
                            line.set_unit_price(line.pos.uom_price[line.product.product_tmpl_id].uom_id[uom_id[0]]);
                            line.price_manually_set = true;
                        },
                    });
                }
            }
        },
    });
    screens.define_action_button({
        'name': 'uom',
        'widget': UOMButton,
    });

});