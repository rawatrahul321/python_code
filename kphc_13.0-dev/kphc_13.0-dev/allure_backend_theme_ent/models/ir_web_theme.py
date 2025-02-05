# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from lxml import etree

import base64
import json
from odoo import _, api, fields, models, SUPERUSER_ID

ROOT_VARS = {
    '$brand-primary': "--brand-primary",
    '$brand-secondary': "--brand-secondary",
    '$button-box': "--button-box",
    '$heading': "--heading",
    '$Label': "--Label",
    '$Label-value': "--Label-value",
    '$link': "--link",
    '$notbook': "--notbook",
    '$tooltip': "--tooltip",
    '$border': "--border",
    '$menu-main-title': "--menu-main-title",
    "--font-color": "var(--Label-value)",
}


class IrWebTheme(models.Model):
    _name = "ir.web.theme"
    _description = "Theme Properties"

    leftbar_color = fields.Char(string='Custom Color', required=True, default="#875a7b")
    menu_color = fields.Char(string='Menu', required=True, default="#666666")
    border_color = fields.Char(string='Border', required=True, default="#cccccc")
    buttons_color = fields.Char(string='Buttons Color', required=True, default="#00a09d")
    button_box = fields.Char(string='Button Box', required=True, default="#666666")
    heading_color = fields.Char(string='Heading Color', required=True, default="#2f3136")
    label_color = fields.Char(string='Label', required=True, default="#666666")
    label_value_color = fields.Char(string='Label Value Color', required=True, default="#666666")
    link_color = fields.Char(string='Link Color', required=True, default="#00a09d")
    panel_title_color = fields.Char(string='Panel Title Color', required=True, default="#2f3136")
    tooltip_color = fields.Char(string='Tooltip Color', required=True, default="#875a7b")

    ttype = fields.Selection([
            ('builtin', "Built In"),
            ('custom', "Customised"),
        ], default='builtin', string="Type")

    base_form_tabs = fields.Selection([
        ('horizontal_tabs','Horizontal'),
        ('vertical_tabs','Vertical',),
        ], default='vertical_tabs')
    tab_configration = fields.Selection([
        ('open_tabs','Open'),
        ('close_tabs','Close',),
        ], default='open_tabs')
    base_menu = fields.Selection([
        ('base_menu','Horizontal'),
        ('theme_menu','Vertical'),
        ], default='theme_menu')
    font_type_values = fields.Selection([
        ('roboto','Roboto'),
        ('open_sans','Open Sans'),
        ('alice','Alice'),
        ('abel','Abel'),
        ('montserrat','Montserrat'),
        ('lato','Lato'),
        ], default='roboto')
    mode = fields.Selection([
        ('light_mode_on', 'Light'),
        ('night_mode_on', 'Night'),
        ('normal_mode_on', 'Normal'),
        ], default='normal_mode_on')
    base_menu_icon = fields.Selection([
        ('base_icon','Base'),
        ('3d_icon','3d'),
        ('2d_icon','2d'),
        ], default='3d_icon')

    @api.model
    def get_current_theme(self):
        return self.env['ir.config_parameter'].sudo().get_param("allure_backend_theme_ent.selected_theme")

    @api.model
    def get_default_theme(self):
        default_theme_id = self.env.ref('allure_backend_theme_ent.theme_6', raise_if_not_found=False)
        if not default_theme_id:
            default_theme_id = self.search([('ttype', '=', 'builtin')], limit=1)
        return default_theme_id

    @api.model
    def create_and_settingup_theme(self, values):
        theme_id = self.create(values)
        theme_id.save_theme_assets()
        return theme_id.id

    def remove_and_settingup_default(self):
        self.ensure_one()
        need_to_reload = False
        theme_to_remove = self.id
        # Remove
        self.unlink()

        # Setting up default theme
        current_theme_id = self.get_current_theme()
        if theme_to_remove == int(current_theme_id):
            default_theme_id = self.get_default_theme()
            default_theme_id.save_theme_assets()
            need_to_reload = True
        return need_to_reload

    def write(self, values):
        """Check ensure one because of record will create only
        from theme dashboard."""
        self.ensure_one()
        res = super(IrWebTheme, self).write(values)
        fields = self._get_css_variables_fields()
        fields.append('mode')
        if list(set(fields).intersection(
                set(values.keys())
            )):
            self.save_theme_assets(values.get('mode', False))
        return res

    def save_theme_assets(self, mode='normal_mode_on'):
        self.ensure_one()
        scss_vars_data = self.get_theme_variables_data()
        scss_vars_str = str()
        root_vars_str = str()
        pattern = lambda k,v: "%s: %s;\n" % (k, v) # convert values to scss format
        for k, v in scss_vars_data.items():
            scss_vars_str += pattern(k, v)
            if ROOT_VARS.get(k):
                root_vars_str += pattern(ROOT_VARS.get(k), v)

        scss_vars_str += """\n:root {
            %s
        }""" % (root_vars_str)

        url = '/allure_backend_theme_ent/static/src/scss/variables.scss'
        custom_url = self.env['web_editor.assets'].make_custom_asset_file_url('/allure_backend_theme_ent/static/src/scss/variables.scss', 'web.assets_backend')
        file_type = 'scss'
        datas = base64.b64encode((scss_vars_str or "\n").encode("utf-8"))

        # Check if the file to save had already been modified
        custom_attachment = self.env['web_editor.assets']._get_custom_attachment(custom_url)
        if custom_attachment:
            # If it was already modified, simply override the corresponding
            # attachment content
            custom_attachment.write({"datas": datas})
        else:
            # If not, create a new attachment to copy the original scss/js file
            # content, with its modifications
            new_attach = {
                'name': url.split("/")[-1],
                'type': "binary",
                'mimetype': (file_type == 'js' and 'text/javascript' or 'text/scss'),
                'datas': datas,
                'url': custom_url,
            }
            new_attach.update(self.env['web_editor.assets']._save_asset_attachment_hook())
            self.env["ir.attachment"].create(new_attach)

            # Create a view to extend the template which adds the original file
            # to link the new modified version instead
            file_type_info = {
                'tag': 'link' if file_type == 'scss' else 'script',
                'attribute': 'href' if file_type == 'scss' else 'src',
            }

            def views_linking_url(view):
                """
                Returns whether the view arch has some html tag linked to
                the url. (note: searching for the URL string is not enough as it
                could appear in a comment or an xpath expression.)
                """
                tree = etree.XML(view.arch)
                return bool(tree.xpath("//%%(tag)s[@%%(attribute)s='%(url)s']" % {
                    'url': url,
                } % file_type_info))

            IrUiView = self.env["ir.ui.view"]
            views_to_inherits = IrUiView.get_related_views('web.assets_backend', bundles=True).filtered(views_linking_url)
            for view_to_xpath in views_to_inherits:
                view_key = 'web.assets_backend.%s.%s_%s' % (view_to_xpath.xml_id.split('.')[0], file_type, self._table)
                if not IrUiView.search_count([('key', '=', view_key)]):
                    new_view = {
                        'name': custom_url,
                        'key': view_key,
                        'mode': "extension",
                        'inherit_id': view_to_xpath.id,
                        'arch': """
                            <data inherit_id="%(inherit_xml_id)s" name="%(name)s">
                                <xpath expr="//%%(tag)s[@%%(attribute)s='%(url_to_replace)s']" position="attributes">
                                    <attribute name="%%(attribute)s">%(new_url)s</attribute>
                                </xpath>
                            </data>
                        """ % {
                            'inherit_xml_id': view_to_xpath.xml_id,
                            'name': custom_url,
                            'url_to_replace': url,
                            'new_url': custom_url,
                        } % file_type_info
                    }
                    IrUiView.sudo().create(new_view)
        self.env['ir.config_parameter'].sudo().set_param("allure_backend_theme_ent.selected_theme", self.id)
        self.env["ir.qweb"].clear_caches()

    def fields_by_scss_vars(self):
        return {
            "$brand-primary": 'leftbar_color',
            "$brand-secondary": 'buttons_color',
            "$button-box": 'button_box',
            "$heading": 'heading_color',
            "$Label": 'label_color',
            "$Label-value": 'label_value_color',
            "$link": 'link_color',
            "$notbook": 'panel_title_color',
            "$tooltip": 'tooltip_color',
            "$border": 'border_color',
            "$menu-main-title": 'menu_color'
        }

    def _get_css_variables_fields(self):
        return list(self.fields_by_scss_vars().values())

    def get_theme_variables_data(self):
        self.ensure_one()
        fields_by_scss_vars = self.fields_by_scss_vars()
        fields = list(fields_by_scss_vars.values())
        data = dict()

        def get_key(val):
            for key, value in fields_by_scss_vars.items():
                if val == value:
                    return key

        for field, value in self.read(fields)[0].items():
            if field in fields:
                data[get_key(field)] = value
        return data

    @api.model
    def get_json_themes(self):
        data = dict()
        search_fields = list()
        for k, v in dict(self._fields).items():
            if self._fields[k].type not in ("date", "datetime"):
                search_fields.append(k)
        themes_data = self.search_read([], search_fields)
        selected_theme_id = self.get_current_theme()
        if not selected_theme_id:
            selected_theme_id = self.get_default_theme().id
        if not isinstance(selected_theme_id, int):
            selected_theme_id = int(selected_theme_id)
        default_user_theme = next((d for d in themes_data if d['id'] == selected_theme_id), None)
        default_user_theme['selected'] = True
        data.update({
                'themes': themes_data,
                'users_config': self.env['res.users'].get_users_themes()
            })
        return json.dumps(data)
