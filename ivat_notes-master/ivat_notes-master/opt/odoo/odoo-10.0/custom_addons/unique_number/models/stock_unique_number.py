from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockUniqueNumber(models.Model):
    _name = 'stock.unique.number'
    _inherit = ['mail.thread']
    _description = 'Unique Serial Number'
    
    name = fields.Char(
        'Unique Serial Number', default=lambda self: self.env['ir.sequence'].next_by_code('stock.unique.serial'),
        required=True, help="Unique Serial Number")
    ref = fields.Char('Internal Reference', help="Internal reference number in case it differs from the manufacturer's unique serial number")
    
    quant_ids = fields.One2many('stock.unique.traceability', 'traceability_id',string= 'Traceability')
    create_date = fields.Datetime('Creation Date')
    product_qty = fields.Integer('Quantity',default=1)
    use_unused_barcode = fields.Boolean('Use / Unused Barcode',default=False,help='When True i.e. Checked means Already Used And When False i.e. Unchecked Means Ready to Use')
    responible_user = fields.Many2one('res.users','Responsible User',default=lambda self: self.env.user)
    
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name)', 'The Serial number must be unique !'),
    ]
    
class QuantTraceability(models.Model):
    _name = "stock.unique.traceability"
    _description = "Stock unique Traceability"
    
    name = fields.Char('Description')
    traceability_id = fields.Many2one('stock.unique.number', 'Unique Serial Number')
    source_location = fields.Many2one('stock.location', 'Source Location')
    destination_location = fields.Many2one('stock.location', 'Destination Location')
    product_id = fields.Many2one('product.product', 'Product')
    date = fields.Datetime('Date')
    status = fields.Char('Status')
    work_order = fields.Char('Work Order')
    concern_user = fields.Many2one('res.users','Responsible User')
    rework = fields.Boolean('Re - Work')
    scrap = fields.Boolean('Scrap')
    
    