import pprint
import werkzeug

from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


class RedsysController(http.Controller):
    _redsys_url_ok = '/payment/redsys/result/ok'
    _redsys_url_ko = '/payment/redsys/result/ko'
    _redsys_url_notifications = '/payment/redsys/result/ko'

    @http.route([
        '/payment/redsys/return',
        '/payment/redsys/cancel',
        '/payment/redsys/error',
        '/payment/redsys/reject',
    ], type='http', auth='none', csrf=False)
    def redsys_return(self, **post):
        _logger.info('Redsys: entering form_feedback with post data %s', pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo()._handle_feedback_data('redsys', post)
        return_url = post.pop('return_url', '') or '/shop'
        return werkzeug.utils.redirect(return_url)

    @http.route([
        _redsys_url_notifications,
        _redsys_url_ok,
        _redsys_url_ko,
        ], type='http', auth='public', methods=['GET', 'POST'], website=True,csrf=False)
    def redsys_result(self, **post):
        if post:
            _logger.info('Redsys result: entering form_feedback with post data %s', pprint.pformat(post))
            request.env['payment.transaction'].sudo()._handle_feedback_data('redsys', post)
        return request.redirect('/payment/status')
