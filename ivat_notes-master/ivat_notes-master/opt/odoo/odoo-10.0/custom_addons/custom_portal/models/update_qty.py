from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class InventoryLineInherit(models.Model):
    _inherit = "stock.inventory.line"
    
    @api.onchange('product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'partner_id', 'package_id','new_qty','theoretical_qty')
    def onchange_quantity_context(self):
        if self.product_id and self.location_id and self.product_id.uom_id.category_id == self.product_uom_id.category_id:  # TDE FIXME: last part added because crash
            self._compute_theoretical_qty()
            print '++++ New Qty ++++',self.new_qty
            print '++ self.theoretical_qty ++',self.theoretical_qty
            self.product_qty = self.theoretical_qty + self.new_qty

    new_qty = fields.Float('New Quantity')
    
    @api.one
    @api.depends('new_qty','theoretical_qty')
    def getUpdatedQty(self):
        if self.product_id and self.location_id and self.product_id.uom_id.category_id == self.product_uom_id.category_id:
            print '++++ New Qty ++++',self.new_qty
            print '++ self.theoretical_qty ++',self.theoretical_qty
            self.product_qty = self.theoretical_qty + self.new_qty
    
    product_qty = fields.Float('Checked Quantity',digits=dp.get_precision('Product Unit of Measure'),
                               compute='getUpdatedQty',store=True,default=False)