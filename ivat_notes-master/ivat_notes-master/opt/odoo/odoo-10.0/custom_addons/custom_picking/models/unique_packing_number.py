from odoo import api, fields, models, _

class UniquePackingNumber(models.Model):
    _name = 'unique.packing.number'
    _inherit = ['mail.thread']
    _description = 'Unique Packing Number'
    
    name = fields.Char(
        'Unique Serial Number', default=lambda self: self.env['ir.sequence'].next_by_code('stock.unique.serial'),
        required=True, help="Unique Serial Number")
    ref = fields.Char('Internal Reference')
    
    line_ids = fields.One2many('packing.unique.traceability', 'traceability_id',string= 'Traceability')
    create_date = fields.Datetime('Creation Date')
    product_qty = fields.Integer('Quantity',default=1)
    use_unused_barcode = fields.Boolean('Use / Unused Barcode',default=False,help='When True i.e. Checked means Already Used And When False i.e. Unchecked Means Ready to Use')
    responible_user = fields.Many2one('res.users','Responsible User',default=lambda self: self.env.user)
    
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name)', 'The Packing Serial number must be unique !'),
    ]
    
class QuantTraceability(models.Model):
    _name = "packing.unique.traceability"
    _description = "Packing unique Traceability"
    
    name = fields.Char('Description')
    traceability_id = fields.Many2one('unique.packing.number', 'Unique Serial Number')
    product_id = fields.Many2one('product.product', 'Product')
    date = fields.Datetime('Date')
    status = fields.Char('Status')
    concern_user = fields.Many2one('res.users','Responsible User')
    total_qty = fields.Float("Total PC's")
    