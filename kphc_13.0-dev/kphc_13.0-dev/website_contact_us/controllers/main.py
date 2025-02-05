from odoo import http, api, fields, models, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm

class WebsiteForm(WebsiteForm):
    def insert_record(self, request, model, values, custom, meta=None):
        if 'is_cide_form : true' in custom:
            if 'name' not in values:
                if 'school_university' in values:
                    values['name'] = values.get('contact_name') + ' ' + values.get('school_university')
                else:
                    values['name'] = values.get('contact_name')
            record_id = super(WebsiteForm, self).insert_record(request, model, values, custom, meta)

            # Ivastanin: If to override fault forms
            if values.get('email_from'):
                template_id = request.env['ir.model.data'].sudo().get_object_reference('website_contact_us', 'website_cide_contact_mail')[1]
                mail_id = request.env['mail.template'].sudo().browse(template_id).send_mail(int(record_id), force_send=True)

            mailing_contact = request.env['mailing.contact'].sudo().search([
                ('name', '=', values.get('name')), ('email', '=', values.get('email_from'))])
            mailing_list = request.env.ref('website_contact_us.back_to_school_mailing_list')
            if mailing_contact:
                if mailing_list.id not in mailing_contact.list_ids.ids:
                    mailing_contact.list_ids = [(4, mailing_list.id)]
            else:
                mailing_contact = request.env['mailing.contact'].sudo().create({
                    'name': values.get('name'),
                    'email': values.get('email_from'),
                    'mobile': values.get('mobile'),
                    'list_ids': [(6, 0, [mailing_list.id])]
            })
            return record_id
        else:
            super(WebsiteForm, self).insert_record(request, model, values, custom, meta)

class CrmLead(http.Controller):

    @http.route('/cide-back-to-school', type="http", auth="public", website=True)
    def cide_back_to_school(self):
        return http.request.render('website_contact_us.create_lead', {})

    @http.route('/thank-you-back-to-school', type="http", auth="public", website=True)
    def create_lead(self):
        return request.render("website_contact_us.lead_thanks", {})
