# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from . import models
from . import controllers
from odoo.addons.payment import reset_payment_acquirer

def pre_init_check(cr):
    from openerp.service import common
    from openerp.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='15.0':raise Warning('Module support Odoo series 15.0 found {}.'.format(server_serie))
    return True

def uninstall_hook(cr, registry):
    reset_payment_acquirer(cr, registry, 'redsys')
