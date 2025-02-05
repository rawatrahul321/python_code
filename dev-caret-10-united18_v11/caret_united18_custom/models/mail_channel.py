# -*- coding: utf-8 -*-

import uuid

from odoo import _, api, models
from odoo.osv import expression

class Channel(models.Model):

    _inherit = 'mail.channel'

    # Enable chat for all users of all company
    @api.model
    def channel_get(self, partners_to, pin=True):
        """ Get the canonical private channel between some partners, create it if needed.
            To reuse an old channel (conversation), this one must be private, and contains
            only the given partners.
            :param partners_to : list of res.partner ids to add to the conversation
            :param pin : True if getting the channel should pin it for the current user
            :returns a channel header, or False if the users_to was False
            :rtype : dict
        """
        if partners_to:
            partners_to.append(self.env.user.partner_id.id)
            # determine type according to the number of partner in the channel
            self.env.cr.execute("""
                SELECT P.channel_id as channel_id
                FROM mail_channel C, mail_channel_partner P
                WHERE P.channel_id = C.id
                    AND C.public LIKE 'private'
                    AND P.partner_id IN %s
                    AND channel_type LIKE 'chat'
                GROUP BY P.channel_id
                HAVING COUNT(P.partner_id) = %s
            """, (tuple(partners_to), len(partners_to),))
            result = self.env.cr.dictfetchall()
            if result:
                # get the existing channel between the given partners
                channel = self.browse(result[0].get('channel_id'))
                # pin up the channel for the current partner
                if pin:
                    self.env['mail.channel.partner'].search([('partner_id', '=', self.env.user.partner_id.id), ('channel_id', '=', channel.id)]).write({'is_pinned': True})
            else:
                # create a new one
                channel = self.create({
                    'channel_partner_ids': [(4, partner_id) for partner_id in partners_to],
                    'public': 'private',
                    'channel_type': 'chat',
                    'email_send': False,
                    'name': ', '.join(self.env['res.partner'].sudo().browse(partners_to).mapped('name')),
                })
                # broadcast the channel header to the other partner (not me)
                channel.sudo()._broadcast(partners_to)
            return channel.sudo().channel_info()[0]
        return False
