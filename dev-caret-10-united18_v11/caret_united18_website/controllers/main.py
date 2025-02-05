# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from collections import OrderedDict
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.website_sale_stock.controllers.main import WebsiteSale as WebsiteSaleStock
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal as Portal
from odoo.addons.purchase.controllers.portal import CustomerPortal
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.controllers import main as web_controller
import logging
from odoo.addons.http_routing.models.ir_http import slug


_logger = logging.getLogger(__name__)


PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

class United18DotCom(web_controller.Website):

    #@http.route('/', type='http', auth="none")
    #def index(self, s_action=None, db=None, **kw):
        #return request.redirect("https://www.united18.com")
        # redirect_with_hash
    @http.route('/.well-known/acme-challenge/PvIz61uZd1AD92uGjugr6hcz9nf2ZqQajQUdeutoLA0', type='http', auth='none')
    def verify1(self, s_action=None, db=None, **kw):
        return 'PvIz61uZd1AD92uGjugr6hcz9nf2ZqQajQUdeutoLA0.hl2Twjg5KmD9jIidrl2l8t94q8GjAoMlbBXjFMNgkq8'

    @http.route('/.well-known/acme-challenge/CAIDYrtGW8dO3zA4PuD8NaBAVI2La5_C11uWA6ZP9iY', type='http', auth='none')
    def verifywww(self, s_action=None, db=None, **kw):
        return 'CAIDYrtGW8dO3zA4PuD8NaBAVI2La5_C11uWA6ZP9iY.hl2Twjg5KmD9jIidrl2l8t94q8GjAoMlbBXjFMNgkq8'

class PurchasePortal(CustomerPortal):
    """overwrite purchase portal and show purchase order on website in my account menu """

    def _prepare_portal_layout_values(self):
        values = super(PurchasePortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['purchase_count'] = request.env['purchase.order'].search_count([
            '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('company_id', 'in', [partner.company_id.id]),
            ('state', 'in', ['purchase', 'done', 'cancel'])
        ])
        return values

    @http.route(['/my/purchase', '/my/purchase/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_purchase_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']

        domain = [
            '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('company_id', 'in', [partner.company_id.id]),
        ]

        archive_groups = self._get_archive_groups('purchase.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['purchase', 'done', 'cancel'])]},
            'purchase': {'label': _('Purchase Order'), 'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        purchase_count = PurchaseOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/purchase",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=purchase_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'purchase',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/purchase',
        })
        return request.render("purchase.portal_my_purchase_orders", values)

class CustomerPortal(Portal):

    """ overwrite purchase portal and show requests of quotation on website in my account menu """

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['po_quotation_count'] = request.env['purchase.order'].search_count([
                ('company_id', 'in', [partner.company_id.id]),
                ('state', 'in', ['sent', 'cancel'])
        ])
        return values

    @http.route(['/my/quotation', '/my/quotation/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotation(self, page=1, date_begin=None, date_end=None, sortby=None,filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']

        domain = [
            '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('company_id', 'in', [partner.company_id.id]),
        ]

        archive_groups = self._get_archive_groups('purchase.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['sent', 'cancel'])]},
            'quotation': {'label': _('Purchase Order'), 'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        po_quotation_count = PurchaseOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotation",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=po_quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders,
            'page_name': 'quotation',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/quotation',
        })
        return request.render("caret_united18_website.portal_my_purchase_quotation", values)

    @http.route(['/my/quotation/<int:order_id>'], type='http', auth="user", website=True)
    def portal_quotation_page(self, order_id=None, access_token=None, **kw):
        order = request.env['purchase.order'].browse(order_id)
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            return request.redirect('/my')
        values = {
            'order': order.sudo(),
        }
        return request.render("caret_united18_website.portal_quotation_page", values)

class TableCompute(object):
# overwrite this class for use in /shop 

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products, ppg=PPG):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in products:
            x = min(max(p.website_size_x, 1), PPR)
            y = min(max(p.website_size_y, 1), PPR)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos // PPR, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // PPR) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos // PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // PPR) + y2][(pos % PPR) + x2] = False
            self.table[pos // PPR][pos % PPR] = {
                'product': p, 'x': x, 'y': y,
                'class': " ".join(x.html_class for x in p.website_style_ids if x.html_class)
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // PPR))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows

class HidePayment(WebsiteSale):
    """ This is skip payment option in sale order process from website side """

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="user", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        print("shopp=========================",category)
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}
        domain = self._get_search_domain(search, category, attrib_values)
        keep = QueryURL('/shop', category=category and int(category),
                         search=search, attrib=attrib_list, order=post.get('order'))
        compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

        request.context = dict(request.context,
                                pricelist=pricelist.id,
                                partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if category:
            category = request.env['product.public.category'].browse(int(category))
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([('parent_id', '=', False)])
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)

        # my code start from here
        if post.get('order'):
            products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
        else:
            products = Product.search(domain,limit=ppg, offset=pager['offset'], order='website_product_qty desc')
        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            selected_products = Product.search(domain, limit=False)
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)
        credit = 0.0
        company_id = request.env.user.company_id
        if company_id.parent_id:
            total_credit,total_sale = request.env['sale.order'].check_credit_limit(company_id.partner_id,
                                                            [('partner_id', '=', company_id.partner_id.id),
                                                             ('state', 'in', ['draft','sent','sale','done'])])
            print("total_credit,total_sale=============",total_credit,total_sale)
            credit = company_id.partner_id.credit_limit_custom - (total_sale - total_credit)
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
            'credit_limit': int(credit)
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route('/shop/cart/add_to_cart/update', type='json', auth="user", website=True)
    def add_to_cart_update(self, access_token=None, **post):
        prod_id = int(post.get('prod_id'))
        qty = int(post.get('pro_qty'))
        prod_spec = post.get('prod_spec')
        res = super(HidePayment, self).cart_update(prod_id,qty)
        sale_order = request.website.sale_get_order()
        if sale_order and prod_spec:
            for line in sale_order.order_line:
                if line.product_id.id == prod_id:
                    line.write({'product_specification': prod_spec})
        return res

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            print("redirection=======================")
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            print("/shop/address================")
            return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)
        values = self.checkout_values(**post)

        # my code
        error = {}
        for line in order.order_line:
            product_tmp_id = line.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()
            actual_qty = product_tmp_id.website_product_qty
            if line.product_uom_qty > actual_qty:
                error.update({str(line.product_id.name)+' available quantity in stock': actual_qty})
        if error:
            values.update({'error':error})

        msg = 0
        if order:
            partner = order.partner_id
            total_credit,total_sale = order.check_credit_limit(partner,
                                                            [('partner_id', '=', partner.id),
                                                             ('state', 'in', ['draft','sent','sale','done'])])
            total = total_sale - total_credit
            print("total_credit,total_sale=============",total_credit,total_sale,total,partner.credit_limit_custom)
            if total > partner.credit_limit_custom:

                msg = int(partner.credit_limit_custom - total)
                print("inside msg=====================",msg)
        values.update({'website_sale_order': order,
                        'credit_limit': msg,
                        })
        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        print("last=========================")
        return request.redirect('/shop/confirm_order')
        # return request.render("website_sale.checkout", values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.env.ref('website_sale.extra_info_option')
        if post.get('description'):
            po = request.env['purchase.order'].search([('so_reference','=',order.id)])
            if po:
                po.sudo().notes = post.get('description')
                order.note = post.get('description')
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/confirmation")

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
        for line in order.order_line:
            product_tmp_id = line.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()
            actual_qty = product_tmp_id.website_product_qty
            if line.product_uom_qty > actual_qty:
                return request.redirect("/shop/checkout")
        request.website.sale_reset()
        # my code
        credit = 0
        if sale_order_id:
            order.sudo().force_quotation_send()
            partner = order.partner_id
            credit_amount, total_amount = order.check_credit_limit(partner,
                                                            [('partner_id', '=', partner.id),
                                                            ('state', 'in', ['draft','sent','sale','done'])])
            credit = partner.credit_limit_custom - (total_amount - credit_amount)
            print(credit)
            return request.render("website_sale.confirmation", {'order': order,
                                                                'credit_limit': int(credit)})
        else:
            return request.redirect('/shop')

    @http.route('/check/product_qty', type='json', auth="public", website=True)
    def check_product_qty(self, **post):
        order = request.website.sale_get_order()
        prod_id = {}
        print("prod_id1===================",prod_id)
        prod_unpublished = {}
        for line in order.order_line:
            product_tmp_id = line.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()
            actual_qty = product_tmp_id.website_product_qty
            print("line.product_uom_qty===========",line.product_uom_qty,order)
            if line.product_uom_qty and not product_tmp_id.website_published:
                line.product_uom_qty = 0.0
                print("line.product_uom_qty====insode",line.product_uom_qty)
                prod_id.update({str(line.product_id.name) : ' unpublished, please remove it in cart'})
            if product_tmp_id.website_published and (line.product_uom_qty > actual_qty):
                prod_id.update({str(line.product_id.name)+' available quantity in stock': actual_qty})
        print("prod_id===================",prod_id)
        if prod_id:
            return prod_id
        return False

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                return request.render('website.404')
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session['sale_order_id']):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session['sale_order_id']:  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price
        credit = 0.0
        company_id = request.env.user.company_id
        if company_id.parent_id:
            total_credit,total_sale = request.env['sale.order'].check_credit_limit(company_id.partner_id,
                                                            [('partner_id', '=', company_id.partner_id.id),
                                                             ('state', 'in', ['draft','sent','sale','done'])])
            print("total_credit,total_sale=============",total_credit,total_sale)
            credit = company_id.partner_id.credit_limit_custom - (total_sale - total_credit)

        values.update({
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
            'credit_limit': int(credit)
        })
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.cart", values)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        print("/shop/product called==================")
        product_context = dict(request.env.context,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)
        credit = 0.0
        company_id = request.env.user.company_id
        if company_id.parent_id:
            total_credit,total_sale = request.env['sale.order'].check_credit_limit(company_id.partner_id,
                                                            [('partner_id', '=', company_id.partner_id.id),
                                                             ('state', 'in', ['draft','sent','sale','done'])])
            print("total_credit,total_sale=============",total_credit,total_sale)
            credit = company_id.partner_id.credit_limit_custom - (total_sale - total_credit)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'credit_limit': int(credit),
        }
        return request.render("website_sale.product", values)


class WebsiteSaleStock(WebsiteSaleStock):
    """ This is skip payment option in sale order process from website side """

    def get_attribute_value_ids(self, product):
        res = super(WebsiteSaleStock, self).get_attribute_value_ids(product)

        # my code( available quantity show on website)
        available_qty = product.website_product_qty
        _logger.warning('available_qty %s', available_qty)

        for values in range(len(res)):
            for value in range(len(res[values])):
                if dict == type(res[values][value]):
                    if 'virtual_available' in res[values][value].keys():
                        res[values][value].update({'virtual_available': available_qty})
                        return res
        return res

