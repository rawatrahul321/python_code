# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, tools, _
from odoo.http import request
from ast import literal_eval
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_product_domain(self):
        res = super(Website, self).sale_product_domain()
        res.append(("website_published", "=", True))
        return res

    def check_restrict(self, product):
        product = self.env['product.template'].browse(product)
        if product.website_product_qty_restrict:
            diff = fields.Datetime.from_string(fields.Datetime.now()) - fields.Datetime.from_string(product.restrict_date_start)
            if (diff.days * 24 * 3600 + diff.seconds) < (product.restrict_time*60*60):
                return True
            else:
                return False

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_id_for_available_stock = fields.Many2one("res.users", string="User For Product Stock")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_id_for_available_stock = literal_eval(ICPSudo.get_param('caret_united18_website.user_id_for_available_stock', default='False'))
        if user_id_for_available_stock and not self.env['res.users'].sudo().browse(user_id_for_available_stock).exists():
            user_id_for_available_stock = False

        res.update(
            user_id_for_available_stock=user_id_for_available_stock,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("caret_united18_website.user_id_for_available_stock", repr(self.user_id_for_available_stock.id))

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        line_id = values.get('line_id')
        for line in self.order_line:
            if line.product_id.type == 'product' and line.product_id.inventory_availability in ['always', 'threshold']:
                cart_qty = sum(self.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
                # check stock availability
                available_stock = line.product_id.product_tmpl_id.website_product_qty
                if cart_qty > available_stock and (line_id == line.id):
                    qty = available_stock - cart_qty
                    new_val = super(SaleOrder, self)._cart_update(line.product_id.id, line.id, qty, 0, **kwargs)
                    values.update(new_val)

                    # Make sure line still exists, it may have been deleted in super()_cartupdate because qty can be <= 0
                    if line.exists() and new_val['quantity']:
                        line.warning_stock = _('You ask for %s products but only %s is available') % (cart_qty, new_val['quantity'])
                        values['warning'] = line.warning_stock
                    else:
                        self.warning_stock = _("Some products became unavailable and your cart has been updated. We're sorry for the inconvenience.")
                        values['warning'] = self.warning_stock
        return values
