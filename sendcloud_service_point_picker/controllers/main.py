# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleSendCloudDelivery(WebsiteSale):

    def _update_website_sale_delivery_return(self, order, **post):
        res = super(WebsiteSaleSendCloudDelivery, self)._update_website_sale_delivery_return(order, **post)
        res.update(order.get_details_sendcloud_ecommerce(post))
        return res

    @http.route(['/shop/update_service_point_details'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_service_point_details(self, **post):
        if post.get('order_id',False):
            order = request.env['sale.order'].sudo().browse(post.get('order_id'))
            order.write({'sb_service_point_details':post.get('sb_service_point_details',False)})
        return True