# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import logging

logger = logging.getLogger(__name__)

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    def http_request(self,req_type,url,json_data):
        #if not message:
        #    message = "Acción desencadenada correctamente"

        headers = {"Content-Type": "application/json"}
        response={}
        if(req_type == "1"):
            response = requests.post(url, data=json.dumps(json_data), headers=headers)
            logger.info("SIGHORE" + "> Response: " + str(response.json()))







