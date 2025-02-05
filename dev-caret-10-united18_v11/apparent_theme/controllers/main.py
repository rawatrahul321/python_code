# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import io
import functools
import base64
import imghdr

from odoo.modules import get_resource_path
import odoo.modules.registry

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.web import controllers as webcontroller

db_monodb = http.db_monodb


class BrandBinary(webcontroller.main.Binary):

    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
        '/web/static/src/img/favicon.ico'
    ], type='http', auth="none", cors="*")
    def company_logo(self, dbname=None, **kw):
        imgname = 'logo'
        imgext = '.png'
        print('came here')
        placeholder = functools.partial(
            get_resource_path, 'apparent_theme', 'static', 'src', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname + imgext))
        else:
            try:
                # create an empty registry
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    company = int(kw['company']) if kw and kw.get('company') else False
                    if company:
                        cr.execute("""SELECT logo_web, write_date
                                        FROM res_company
                                       WHERE id = %s
                                   """, (company,))
                    else:
                        cr.execute("""SELECT c.logo_web, c.write_date
                                        FROM res_users u
                                   LEFT JOIN res_company c
                                          ON c.id = u.company_id
                                       WHERE u.id = %s
                                   """, (uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_base64 = base64.b64decode(row[0])
                        image_data = io.BytesIO(image_base64)
                        imgext = '.' + (imghdr.what(None, h=image_base64) or 'png')
                        response = http.send_file(image_data, filename=imgname + imgext, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname + imgext))

        return response
