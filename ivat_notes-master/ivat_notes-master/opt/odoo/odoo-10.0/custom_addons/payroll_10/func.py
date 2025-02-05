# from openerp.osv import fields, osv
from odoo.osv import  osv
from odoo import api


class hr_employee(osv.Model):
    _inherit = 'hr.employee'
    _order = 'emp_code'
    
    @api.model   
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            emp_code = record.emp_code
            if emp_code:
                name =  "[%s] %s" % (emp_code ,name)
            else:
                name =  "%s" % (name)
            res.append((record.id, name))
        return res
    @api.model
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('emp_code','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('name','=',name)]+ args, limit=limit, context=context)
                
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('emp_code',operator,name)], limit=limit, context=context))
                if len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
                ids = list(ids)
#            if not ids:
#                ptrn = re.compile('(\[(.*?)\])')
#                res = ptrn.search(name)
#                if res:
#                    ids = self.search(cr, user, [('name','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
