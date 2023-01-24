# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SeoSeo(models.Model):
    _name = 'seo.seo'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    url_containing = fields.Char('URL containing')
    is_indexed = fields.Boolean(default=False)
