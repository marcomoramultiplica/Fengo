# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import logging

logger = logging.getLogger(__name__)

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    def http_request(self,req_type,json_valores,json_data):
        #if not message:
        #    message = "Acción desencadenada correctamente"
        url_base = "http://116.203.95.235/test/api/ElementoGestion/"
        api_key = '51c75f1cdbef22aa8aac655f9e06c4f96a0f85a1'
        headers = {"Content-Type": "application/json"}
      
        if(req_type == "1"):
            empresa = json_valores['empresa']
            codigo_fam = json_valores['codigo_fam']
            nombre_fam = json_valores['nombre_fam']
            codigo_sub = json_valores['codigo_sub']
            nombre_sub = json_valores['nombre_sub']
            codigo_item = json_valores['codigo_item']
            nombre_item = json_valores['nombre_item']

            url_fam = url_base + 'Familia/'+empresa+"/"+codigo_fam+"?api_key="+api_key
            url_sub = url_base + 'Subfamilia/'+empresa+"/"+codigo_sub+"?api_key="+api_key
            url_item = url_base + 'Articulo/'+codigo_item+"/"+empresa+"?api_key="+api_key
            url_item_get = url_base + 'Articulo/'+empresa+"/"+codigo_item+"?api_key="+api_key
            response = requests.get(url_fam, headers=headers)
            logger.info("SIGHORE" + "> Response bus: " + str(response.content))
            datos = response.content
            if('error' in datos):
                json_info = {"codigo":codigo_fam,"nombre":nombre_fam}
                response_create = requests.post(url_fam, headers=headers , json=json_info)
                logger.info("SIGHORE" + "> Response create: " + str(response_create.content))
            
            response_sub = requests.get(url_sub,headers=headers ) 
            logger.info("SIGHORE" + "> Response sub: " + str(response_sub.content))
            datos_sub = response_sub.content
            if('error' in datos_sub):
                json_info_sub = {"codigo":codigo_sub,"nombre":nombre_sub,"familia":codigo_fam}
                response_create_sub = requests.post(url_sub, headers=headers , json=json_info_sub)
                logger.info("SIGHORE" + "> Response create sub: " + str(response_create_sub.content))
                
            json_item = {"desc_ticket":nombre_item,"desc_prov":nombre_item,"desc_larga":nombre_item,"desc_corta":nombre_item,"codigo":codigo_item,"familia":codigo_fam,"subfamilia":codigo_sub}
            response_item = requests.post(url_item, headers=headers, json=json_item)
            logger.info("SIGHORE" + "> Response create_item: " + str(response_item.content))
        
        if(req_type == "2"):
            codigo_edit = json_valores['codigo_edit']
            empresa_edit = json_valores['empresa_edit']
            url_edit = url_base + "Articulo/" +codigo_edit + "/" +empresa_edit+"?api_key="+api_key
            response_edit = requests.put(url_edit,headers=headers,json=json_data)
            logger.info("SIGHORE" + "> Response EDIT_item: " + str(response_edit.content))
        
        if(req_type == "3"):
            codigo_delete = json_valores['codigo_delete']
            empresa_delete = json_valores['empresa_delete']
            url_delete = url_base + "Articulo/" +codigo_delete+ "/" +empresa_delete+"?api_key="+api_key
            response_delete = requests.delete(url_delete,headers=headers)
            logger.info("SIGHORE" + "> Response DELETE_item: " + str(response_delete.content))
            
