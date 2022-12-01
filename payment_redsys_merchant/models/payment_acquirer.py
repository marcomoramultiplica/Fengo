# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import http, api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools import config
from odoo.addons.payment_redsys_merchant.const import currency_dict, redsys_lang


class PaymentAcquirerRedsys(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('redsys', 'Redsys')], ondelete={'redsys': 'set default'})
    redsys_merchant_code = fields.Char("Merchant Code", required_if_provider='redsys', groups='base.group_user')
    redsys_merchant_key = fields.Char("Merchant Key", required_if_provider='redsys', groups='base.group_user')
    redsys_transaction_type = fields.Char('Transtaction Type', default='0', required_if_provider='redsys', readonly=True)
    redsys_merchant_terminal = fields.Char("Merchant Terminal", default='001', required_if_provider='redsys', help="Terminal number assigned by your bank.", groups='base.group_user')
    redsys_pay_method = fields.Char("Payment Methods", default="T")
    redsys_signature_version = fields.Char("Signature Version", default='HMAC_SHA256_V1', readonly=True)
    redsys_merchant_lang = fields.Selection(redsys_lang, "Merchant Consumer Language", default="2")

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in currency_dict:
            acquirers = acquirers.filtered(lambda a: a.provider != 'redsys')

        return acquirers

    def _redsys_get_api_url(self):
        """ Provide Post Url For Redsys Payment Form ."""
        self.ensure_one()
       
        if self.state == "enabled":
            url = "https://sis.redsys.es/sis/realizarPago"
        else:
            url = "https://sis-t.redsys.es:25443/sis/realizarPago"
        return url

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'redsys':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_redsys_merchant.payment_method_redsys').id
