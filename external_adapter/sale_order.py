# -*- encoding: utf-8 -*-
##############################################################################
#
#    external_adapter_sale_order
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
from decimal import Decimal
import pdb

class external_adapter_sale_order(osv.osv):
    """añadimos los nuevos campos"""
    
    _name = "external.adapter.sale.order"
   
    def get_by_partner(self, cr, uid, partner_id, fields):
        order_model = self.pool.get('sale.order')
        args = [("partner_id","=",partner_id)]

        order_ids = order_model.search(cr, uid, args)

        orders = {}

        if order_ids:
            orders = order_model.read(cr, uid, order_ids, fields)
        
        return orders

    def get_order(self, cr, uid, order_id, fields):
        order_model = self.pool.get('sale.order')
        line_model = self.pool.get('sale.order.line')
        product_model = self.pool.get('product.product')

        order = order_model.read(cr, uid, [int(order_id)], fields)[0]       

        lines = {}

        fields = ["product_uom_qty", "price_unit", "price_subtotal"]
        fields.append("product_id")

        if order["order_line"]:
            lines = line_model.read(cr, uid, order["order_line"], fields)            
            for line in lines:
                product = product_model.read(cr, uid, line["product_id"][0], ["name_template", "image_small"])
                line["product_name"] = product["name_template"]
                line["product_image"] = product["image_small"]
        
        return {"order": order, "lines": lines}


    def write_order(self, cr, uid, order_id, lines, pricelist_id, partner_id, fields):
        order_model = self.pool.get('sale.order')
        line_model = self.pool.get('sale.order.line')
        ext_prod_model = self.pool.get('external.adapter.product')
        prod_model = self.pool.get('product.product')
        
        order = order_model.read(cr, uid, [int(order_id)], fields)[0]       

        # Borrar lineas
        line_model.unlink(cr, uid, order["order_line"])                

        # Rellenar todos los valores a excepción del precio
        for line in lines:
            
            value = {
                "product_id": line["product_id"],
                "name": line["product_name"],
                "product_uom_qty": Decimal(line["product_uom_qty"]),
                "order_id": int(order_id)
            }

            prod =  prod_model.read(cr, uid, [line["product_id"]], ["parent_prod_id", "cost_price"])[0]            

            if prod["parent_prod_id"]:
                # Se obtiene el precio del producto padre
                prod_id = prod["parent_prod_id"][0]                
            else:
                prod_id = line["product_id"]
            
            product_price = ext_prod_model.get_pricelist(cr, uid, [prod_id], pricelist_id, partner_id)[prod_id][pricelist_id]
            value["price_unit"] = product_price
            value["purchase_price"] = prod["cost_price"]

            line_model.create(cr, uid, value)

        return True
  