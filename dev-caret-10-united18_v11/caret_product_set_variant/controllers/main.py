# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.caret_united18_website.controllers.main import HidePayment
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website.controllers.main import QueryURL

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

class WebsiteSaleCategory(HidePayment):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="user", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
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

        product_set = request.env['product.set'].search([])
        categ_ids = []
        for pSet in product_set:
            if pSet.category_id.id not in categ_ids:
                categ_ids.append(pSet.category_id.id)

        productSetCategories = request.env['product.category'].search([('id', 'in', categ_ids)])
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
            'productSetCategories': productSetCategories,
            'credit_limit': int(credit)
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route([
        '/product_set/<model("product.category"):categ_id>',
    ], type='http', auth="public", website=True)
    def showProductSet(self, categ_id, **post):
        productSets = request.env['product.set'].search([('category_id', '=', categ_id.id)])
        values = {
            'productSets': productSets
        }
        return request.render("caret_product_set_variant.product_set", values)

    @http.route([
        '/product_set/products/<model("product.set"):set_id>',
    ], type='http', auth="public", website=True)
    def showProducts(self, set_id, **post):
        productSet = request.env['product.set'].browse(set_id.id)
        productTemplateIds = []
        for line in productSet.set_line_ids:
            productTemplateIds.append(line.product_template_id.id)
        products = request.env['product.template'].browse(productTemplateIds)
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}
        values = {
            'products': products,
            'rows': PPR,
            'bins': TableCompute().process(products, PPG),
        }
        return request.render("caret_product_set_variant.set_products", values)

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        productObj = request.env['product.product']
        product = productObj.search([('id', '=', product_id)])
        product_template = request.env['product.template'].browse(product.product_tmpl_id.id)
        restrict_attr = product_template.attrubute_restrict_id

        if restrict_attr:
            restrict_attr_ids = [line.value_ids.ids for line in product_template.attribute_line_ids if restrict_attr == line.attribute_id]
            attrs = []
            for value in restrict_attr_ids[0]:
                product_attrs = product.attribute_value_ids.ids
                if value in product_attrs:
                    stored = value
                    attrs.append(product_attrs)
                if value not in product_attrs:
                    product_attrs[product_attrs.index(stored)] = value
                    attrs.append(product_attrs)
            visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
            attribute_value_ids = []
            for variant in product.product_variant_ids:
                visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
                attribute_value_ids.append([variant.id, visible_attribute_ids])
            for attr in attribute_value_ids:
                if attr[1] in attrs:
                    product_id = attr[0]
                    sale_order._cart_update(
                        product_id=int(product_id),
                        add_qty=add_qty,
                        set_qty=set_qty,
                        attributes=self._filter_attributes(**kw),
                    )
        else:
            sale_order._cart_update(
                product_id=int(product_id),
                add_qty=add_qty,
                set_qty=set_qty,
                attributes=self._filter_attributes(**kw),
            )
        return request.redirect("/shop/cart")
