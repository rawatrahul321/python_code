# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from binascii import unhexlify
from hashlib import sha256
import hmac
import logging
import urllib
import werkzeug
import pprint

from odoo import api, fields, models,_,tools
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_mastercard.controllers.main import WkMasterCardController
from odoo.tools.float_utils import float_compare
from odoo.http import request

_logger = logging.getLogger(__name__)


CURRENCY_CODE_MAPS = {
    "BHD": 3,
    "CVE": 0,
    "DJF": 0,
    "GNF": 0,
    "IDR": 0,
    "JOD": 3,
    "JPY": 0,
    "KMF": 0,
    "KRW": 0,
    "KWD": 3,
    "LYD": 3,
    "OMR": 3,
    "PYG": 0,
    "RWF": 0,
    "TND": 3,
    "UGX": 0,
    "VND": 0,
    "VUV": 0,
    "XAF": 0,
    "XOF": 0,
    "XPF": 0,
}


class AcquirerMasterCard(models.Model):
    _inherit = 'payment.acquirer'

    _mastercard_submitUrl = '' 

    provider = fields.Selection(
        selection_add=[('mastercard',  'Master Card')]
    )
    mastercard_merchant_id = fields.Char(
        string='Merchant Id',
        required_if_provider='mastercard',
        groups='base.group_user'
    )
    mastercard_merchant_access_code = fields.Char(
         string='Access Code',
         required_if_provider='mastercard',
         groups='base.group_user'
     )
    mastercard_hash_secret = fields.Char(
        string='Hash Secret',
        required_if_provider='mastercard',
        groups='base.group_user'
    )
    
    
    @api.model
    def _mastercard_convert_amount(self, amount, currency):
        """
        Mastercard requires the amount to be multiplied by 10^k,
        where k depends on the currency code.
        """
        k = CURRENCY_CODE_MAPS.get(currency.name, 2)
        paymentAmount = int(tools.float_round(amount, k) * (10**k))
        return paymentAmount


    @api.model
    def generate_mastercard_hash(self,values,inout='IN'):
        """ Generate   Hash For Payment Validation."""
        _hash = ''
        if inout == 'IN':
            for key in sorted(values):
                _hash +="&%s=%s"%((key), (str(values[key])))
        elif inout == 'OUT':
            for key in sorted(values):
                if (key !='vpc_SecureHash' and key !='vpc_SecureHashType' and (key[0:4]=='vpc_' or key[0:5]=='user_')):
                    _hash +="&%s=%s"%((key), (str(values[key])))
        _hash=_hash.strip('&')
        key  = unhexlify(str(self.mastercard_hash_secret or ''))
        secure_hash = hmac.new(key, _hash.encode(), sha256).hexdigest()
        return secure_hash.upper()
            


    
    def mastercard_get_form_action_url(self):
        """ Provide Post Url For MasterCard Payment Form ."""
        self.ensure_one()
        return 'https://migs.mastercard.com.au/vpcpay?%s'% self._mastercard_submitUrl


    def _generate_url(self,key,value):

        if len(value)==0:
            return False
        
        if len(key)== 0:
            return False
        
        if self._mastercard_submitUrl=='':
            self._mastercard_submitUrl+=''+key+'='+value
        elif self._mastercard_submitUrl!='':
            self._mastercard_submitUrl+='&'+key+'='+value
        
        return True

    
    def mastercard_form_generate_values(self, values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        paymentAmount = self._mastercard_convert_amount(values['amount'], values['currency'])
        reference = values.get('reference')
        mastercard_tx_values = dict(values)
        
        vpc_ReturnURL = WkMasterCardController._returnUrl

        vals = {
            'vpc_AccessCode'        :  self.mastercard_merchant_access_code,
            'vpc_Amount'            : '%d' % paymentAmount,
            'vpc_Command'           : 'pay',
            'vpc_Currency'          : values['currency'].name,
            'vpc_Locale'            : values['partner_lang'],
            "vpc_MerchTxnRef"       : reference,
            'vpc_Merchant'          : self.mastercard_merchant_id,
            "vpc_OrderInfo"         : reference+'_'+''.join(values['partner_name'].split(' ')),
            "vpc_ReturnURL"         : '%s' % urllib.parse.urljoin(base_url, vpc_ReturnURL),
            "vpc_Version"           : '1',
        }

        vals['vpc_SecureHash'] = self.generate_mastercard_hash(vals,inout='IN')
        vals['vpc_SecureHashType'] = 'SHA256'
        vals['Title'] = 'Mastercard_VPC_3_Party_Transaction'
        
        for key,value in vals.items():
            if len(value)>0:
                self._generate_url(key,value)
        
        mastercard_tx_values.update(vals)

        return mastercard_tx_values



class TxMasterCard(models.Model):
    _inherit = 'payment.transaction'
    _mastercard_valid_tx_status = ['0']
    _mastercard_cancel_tx_status = ['A','B','C','D','E','F','I','L','N','P','R','T','U','V']
    _mastercard_reject_tx_status = ['1','2','3','4','5','6', '7','8','9']

    mastercard_txnid = fields.Char('Master Card Transaction ID')

    @api.model
    def _mastercard_form_get_tx_from_data(self, data):
        """ Given a data dict coming from Mastercard, verify it and find the related
        transaction record. """

        reference = data.get('vpc_MerchTxnRef')
        hashkey = data.get('vpc_SecureHash')
        transactionNo = data.get('vpc_TransactionNo')

        if not reference or not hashkey or not transactionNo:
            error_msg = _('MasterCard Payment: received data with missing reference (%s) or Transaction No (%s) or HashKey (%s) or payment has not been captured ' % (reference,transactionNo,hashkey))
            raise ValidationError(error_msg)
        tx_ids = self.search([('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            message = tx_ids and 'Multiple order found'or 'No order found'
            error_msg = _('MasterCard: Received data for reference %s .%s.' % (
                reference, message))
            raise ValidationError(error_msg)

        if data.get('vpc_SecureHash',None):
            shasign_check = tx_ids.acquirer_id.generate_mastercard_hash(data,inout='OUT')
            if shasign_check != hashkey:
                raise ValidationError(_('MasterCard: invalid shasign, received %s, computed %s, for data %s') % (hashkey, shasign_check, data))

        return tx_ids[0]

    
    def _mastercard_form_get_invalid_parameters(self, data):

        invalid_parameters = []
        if self.acquirer_reference and data.get('vpc_MerchTxnRef') != self.acquirer_reference:
            invalid_parameters.append(('Transaction Reference', data.get(
                'vpc_MerchTxnRef'), self.acquirer_reference))

        if float_compare(float(data.get('vpc_Amount', '0.0')) / 1000, self.amount, 2) != 0:
            invalid_parameters.append(
                ('Amount', data.get('vpc_Amount'), '%.2f' % self.amount))

        return invalid_parameters

    
    def _mastercard_form_validate(self,  data):
        """ Set Transaction status on basis of Received Data """
        status_code = data.get('vpc_TxnResponseCode')
        state=None
        if status_code in self._mastercard_valid_tx_status:
            state = 'done'
            self._set_transaction_done()
        elif status_code in self._mastercard_reject_tx_status:
            state = 'error'
            error_msg = _(data.get('vpc_Message'))
            self._set_transaction_error(error_msg)
        elif status_code in self._mastercard_cancel_tx_status:
            state = 'cancel'
            self._set_transaction_cancel()
        state = state and state or 'error'

        vals = dict(
            state=state,
            acquirer_reference=data.get('vpc_OrderInfo', None),
            mastercard_txnid=data.get('vpc_TransactionNo', None),
            date=fields.Datetime.now(),
        )
        if state != 'done':
            vals.update(state_message=_('MasterCard: Feedback %s'%(pprint.pformat(data))))
        return self.write(vals)
