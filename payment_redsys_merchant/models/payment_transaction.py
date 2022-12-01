# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
import urllib
import json
import base64
import hashlib
import hmac
from werkzeug import urls

from odoo.tools.float_utils import float_compare

from odoo import _, api, fields, models, http
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_redsys_merchant.const import currency_dict
from odoo.addons.payment_redsys_merchant.controllers.main import RedsysController

_logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import DES3
except ImportError:
    _logger.info("\n Payment Redsys:.......ERROR.>> Missing dependency (pycryptodome)..Please Install if first using command.'pip3 install pycryptodome'............")


class PaymentTransactionRedsys(models.Model):
    _inherit = 'payment.transaction'

    redsys_txnid = fields.Char('Transaction ID')

    @staticmethod
    def encodeInBase64(dataString):
        base64Bytes = base64.b64encode(dataString.encode())
        base64String = base64Bytes.decode()
        return base64String

    @staticmethod
    def _decodeFromBase64(encodedParams):
        base64Bytes = base64.b64decode(encodedParams)
        params = json.loads(base64Bytes.decode())
        return params

    def _generate_merchant_parameters(self, acquirer):
        base_url = acquirer.get_base_url()
        currency_code = currency_dict.get(self.currency_id.name, False)
        # currency_code = '978'

        if not currency_code:
            msg = "Currency <" + currency_code + "> not Found" if currency_code else "Currency <" + currency_code + "> not Found in Currency dict"
            raise ValidationError(msg)

        params = {
            "Ds_Merchant_Amount"            : str(int( self.amount * 100 )),
            "Ds_Merchant_Currency"          : currency_code or '978',
            "Ds_Merchant_MerchantCode"      : str(acquirer.redsys_merchant_code) or "999008881",
            "Ds_Merchant_Order"             : self.reference or False,
            "Ds_Merchant_Terminal"          : str(acquirer.redsys_merchant_terminal) or "001",
            "Ds_Merchant_TransactionType"   : int(acquirer.redsys_transaction_type) or "0",
            'Ds_Merchant_MerchantUrl'       : urls.url_join(base_url, RedsysController._redsys_url_notifications),
            "Ds_Merchant_ConsumerLanguage"  : (acquirer.redsys_merchant_lang or "001"),
            "Ds_Merchant_Paymethods"        : acquirer.redsys_pay_method or "T",
            "Ds_Merchant_UrlOk"             : urls.url_join(base_url, RedsysController._redsys_url_ok),
            "Ds_Merchant_UrlKo"             : urls.url_join(base_url, RedsysController._redsys_url_ko),
        }
        base64String = PaymentTransactionRedsys.encodeInBase64(json.dumps(params, separators=(",", ":")))
        return base64String

    @staticmethod
    def _generateDsSignature(secret_key, encodedParam):
        params = PaymentTransactionRedsys._decodeFromBase64(encodedParam)
        if 'Ds_Merchant_Order' in params:
            order = str(params['Ds_Merchant_Order'])
        else:
            order = str(urllib.parse.unquote(params.get('Ds_Order', 'Not found')))
        cipher = DES3.new(
            key=base64.b64decode(secret_key),
            mode=DES3.MODE_CBC,
            IV=b'\0\0\0\0\0\0\0\0')
        diff_block = len(order) % 8
        zeros = diff_block and (b'\0' * (8 - diff_block)) or b''
        key = cipher.encrypt(str.encode(order + zeros.decode()))
        if isinstance(encodedParam, str):
            encodedParam = encodedParam.encode()
        dig = hmac.new(
            key=key,
            msg=encodedParam,
            digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'redsys':
            return res
        acquirer = self.acquirer_id
        tx_values = self._generate_merchant_parameters(acquirer)
        redsys_values = {
            'Ds_SignatureVersion': str(acquirer.redsys_signature_version),
            'Ds_MerchantParameters': tx_values,
            'Ds_Signature': PaymentTransactionRedsys._generateDsSignature(acquirer.redsys_merchant_key, tx_values),
            'api_url': acquirer._redsys_get_api_url(),
        }
        return redsys_values

    @staticmethod
    def merchant_params_form_data(data):
        parameters = data.get('Ds_MerchantParameters', '')
        return json.loads(base64.b64decode(parameters).decode())

    @staticmethod
    def _get_redsys_status(status_code):
        if 0 <= status_code <= 100:
            return "done"
        elif status_code <= 203:
            return "pending"
        elif 912 <= status_code <= 9912:
            return "cancel"
        else:
            return "error"

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'redsys':
            return tx

        parameters = PaymentTransactionRedsys.merchant_params_form_data(data)
        reference = urllib.parse.unquote(parameters.get('Ds_Order', ''))
        pay_id = parameters.get('Ds_AuthorisationCode')
        shasign = data.get('Ds_Signature', '').replace('_', '/').replace('-', '+')

        if not reference or not pay_id or not shasign:
            raise ValidationError(
                "Redsys: " + _(
                    "Received data with missing reference (%(ref)s) or pay_id (%(pay)s) or shasign (%(sign)s)",
                    ref=reference, pay=pay_id, sign=shasign,
                )
            )

        tx = self.search([('reference', '=', reference), ('provider', '=', 'redsys')])
        if not tx:
            raise ValidationError(
                "Redsys: " + _("No transaction found matching reference %s.", reference)
            )

        latest_tx = tx[0]
        shasign_check = PaymentTransactionRedsys._generateDsSignature(latest_tx.acquirer_id.redsys_merchant_key, data.get('Ds_MerchantParameters', ''))
        if shasign_check != shasign:
            raise ValidationError(
                "Redsys: " + _(
                    "Invalid shasign: received %(sign)s, computed %(computed)s.",
                    sign=shasign, computed=shasign_check
                )
            )
        return tx

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'redsys':
            return
        
        parameters = self.merchant_params_form_data(data)
        status_code = int(parameters.get('Ds_Response', '29999'))
        state = PaymentTransactionRedsys._get_redsys_status(status_code)
        vals = {
            'redsys_txnid': parameters.get('Ds_AuthorisationCode'),
            'acquirer_reference': parameters.get('Ds_AuthorisationCode'),
        }
        state_message = ""
        if state == 'done':
            vals['state_message'] = _('Ok: %s') % parameters.get('Ds_Response')
            self._set_done()
        elif state == 'pending':  # 'Payment error: code: %s.'
            state_message = _('Error: %s [%s]')
            self._set_pending()
        elif state == 'cancel':  # 'Payment error: bank unavailable.'
            state_message = _('Bank Error: %s [%s]')
            self._set_canceled()
        else:
            state_message = _('Redsys: feedback error %s [%s]')
            self._set_error(state_message)
        if state_message:
            vals['state_message'] = state_message % ( parameters.get('Ds_Response'), parameters.get('Ds_ErrorCode'))
            if state == 'error':
                _logger.warning(vals['state_message'])
        self.write(vals)
