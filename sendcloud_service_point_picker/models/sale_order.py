import json
from odoo import fields,api,models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sb_service_point_details = fields.Text('Service Point Details', copy=False, help='Stored response of sendcloud service point when user select service point from front end.')

    def get_details_sendcloud_ecommerce(self,post):
        self.ensure_one()
        res = {'is_sendcloud_service_point_enable': False}
        self.write({'sb_service_point_details':False})
        if post.get('carrier_id',False):
            carrier_id = int(post.get('carrier_id'))
            carrier = self.env['delivery.carrier'].browse(carrier_id)
            shipping_partner = carrier.shipping_partner_id
            if carrier and carrier.delivery_type == 'sendcloud_ts' and shipping_partner:
                public_key = shipping_partner.sendcloud_public_key or ''
                carrier_name = carrier.sendcloud_service_id and carrier.sendcloud_service_id.carrier_id.name or ''
                country_code = self.partner_shipping_id and self.partner_shipping_id.country_id and self.partner_shipping_id.country_id.code or ''
                zip_code = self.partner_shipping_id and self.partner_shipping_id.zip or ''
                res.update({'is_sendcloud_service_point_enable':carrier.is_enable_service_point,
                            'sendcloud_details':{
                                    'order_id' : self.id,
                                    'key':public_key,
                                    'country_code':country_code,
                                    'postcode':zip_code,
                                    'carrier_name':[carrier_name]
                            }
                })
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        return res