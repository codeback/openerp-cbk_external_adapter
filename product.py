# -*- encoding: utf-8 -*-
##############################################################################
#
#    external_adapter_product
#    Copyright (c) 2013 Codeback Software S.L. (http://codeback.es)    
#    @author: Miguel García <miguel@codeback.es>
#    @author: Javier Fuentes <javier@codeback.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
import json
import pdb

class external_adapter_product(osv.osv):
    """añadimos los nuevos campos"""
    
    _name = "external.adapter.product"
   
    def get_products(self, cr, uid, pricelist_id, partner_id, args, fields, context=None):  

        prod_model = self.pool.get('product.product')

        if context == None:
            context = {}

        context['lang'] = "es_ES"

        if not args:
            args = []

        args += [("web_visible","=",True)]                
        prod_ids = prod_model.search(cr, uid, args)

        fields.append("parent_prod_id")
        prods = prod_model.read(cr, uid, prod_ids, fields, context=context)        

        for prod in prods:
            if prod["parent_prod_id"]:
                # Se obtiene el precio del producto padre
                prod_id = prod["parent_prod_id"][0]                
            else:
                prod_id = prod["id"]

            product_price = self.get_pricelist(cr, uid, [prod_id], pricelist_id, partner_id)[prod_id][pricelist_id]
            prod["price"] = "{0:.2f}".format(product_price)

        return prods

    def get_related_products(self, cr, uid, prod_id, fields, context=None):        
        args = [("web_visible","=",True), ("parent_prod_id","=",prod_id)]
        prod_model = self.pool.get('product.product')
        prod_ids = prod_model.search(cr, uid, args)
        return prod_model.read(cr, uid, prod_ids, fields)        

    def get_pricelist(self, cr, uid, prod_ids, pricelist_id, partner_id, context=None):

        pl_model = self.pool.get('product.pricelist')

        products_by_qty_by_partner = []
        qty = 1

        for prodId in prod_ids:
            products_by_qty_by_partner.append((prodId, qty, partner_id))

        return pl_model.price_get_multi(cr, uid, [pricelist_id], products_by_qty_by_partner, context)
