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
import calendar

class external_adapter_sale_order(osv.osv):
    """añadimos los nuevos campos"""
    
    _name = "external.adapter.sale.order"
   
    def get_by_partner(self, cr, uid, partner_id, fields):
        order_model = self.pool.get('sale.order')
        stock_model = self.pool.get('stock.picking.out')
        args = [("partner_id","=",partner_id)]

        order_ids = order_model.search(cr, uid, args)

        orders = {}

        if order_ids:
            fields.append("picking_ids")
            orders = order_model.read(cr, uid, order_ids, fields)
            for order in orders:
                if order["picking_ids"]:
                    sched_dates = stock_model.read(cr, uid, order["picking_ids"], ["min_date"])
                    sched_dates.sort(key=lambda x: datetime.strptime(x["min_date"], '%Y-%m-%d %H:%M:%S'), reverse=True)
                    order["sched_date"] = sched_dates[0]["min_date"].partition(" ")[0]
        
        return orders

    def get_by_partner_and_month(self, cr, uid, partner_id, fields):
        order_model = self.pool.get('sale.order')
        
        orders = {}
        
        year = datetime.now().year
        for month in range(1,13):
            date_from = datetime(year,month,1).strftime("%Y-%m-%d")
            date_to = datetime(year,month,calendar.monthrange(year,month)[1]).strftime("%Y-%m-%d")        
            args = [("partner_id","=",partner_id),('date_order','>=',date_from), ('date_order','<',date_to)]
            order_ids = order_model.search(cr, uid, args)
            orders[str(month)] = order_model.read(cr, uid, order_ids, fields)

        return orders

    def get_order(self, cr, uid, order_id, fields):
        order_model = self.pool.get('sale.order')
        line_model = self.pool.get('sale.order.line')
        product_model = self.pool.get('product.product')

        order = order_model.read(cr, uid, [order_id], fields)[0]       

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

    def create_order(self, cr, uid, lines, pricelist_id, partner_id):
        order_model = self.pool.get('sale.order')        
        partner_model = self.pool.get('res.partner')

        address_invoice_id = partner_model.address_get(cr, uid, [partner_id], ['invoice'])['invoice']
        address_shipping_id = partner_model.address_get(cr, uid, [partner_id], ['delivery'])['delivery']

        # Crear pedido
        value = {
            "partner_id": partner_id,
            "date_order": datetime.now(),
            "pricelist_id": pricelist_id, 
            "partner_invoice_id": address_invoice_id,
            "partner_shipping_id": address_shipping_id
        }
        order_id = order_model.create(cr, uid, value)

        # Rellenar lineas
        self._createSaleOrderLines(cr, uid, order_id, lines, pricelist_id, partner_id)       

        return order_id

    def write_order(self, cr, uid, order_id, lines, pricelist_id, partner_id, fields):
        order_model = self.pool.get('sale.order')
        line_model = self.pool.get('sale.order.line')        
        
        order = order_model.read(cr, uid, [order_id], fields)[0]       

        # Borrar lineas
        line_model.unlink(cr, uid, order["order_line"])  

        # Rellenar lineas              
        return self._createSaleOrderLines(cr, uid, order_id, lines, pricelist_id, partner_id)

    def get_invoice_pdf(self, cr, uid, order_id, partner_id):
        order_model = self.pool.get('sale.order')
        attach_model = self.pool.get('ir.attachment')
        
        order = order_model.read(cr, uid, order_id, ["invoice_ids"])[0]

        pdfs = []
        
        for invoice_id in order["invoice_ids"]:                        
            args = [("partner_id", "=", partner_id), ("res_id", "=", invoice_id)]

            docs_ids = attach_model.search(cr, uid, args)

            if len(docs_ids) > 0:
                att = attach_model.read(cr, uid, docs_ids[0], ['datas', 'name'])[0]	
                pdfs.append(att)
                
        return pdfs


    def _createSaleOrderLines(self, cr, uid, order_id, lines, pricelist_id, partner_id):
        ext_prod_model = self.pool.get('external.adapter.product')
        line_model = self.pool.get('sale.order.line')
        prod_model = self.pool.get('product.product') 
        company_model = self.pool.get('res.company') 

        # Rellenar todos los valores a excepción del precio
        for line in lines:
            
            value = {
                "product_id": line["product_id"],
                "name": line["product_name"],
                "product_uom_qty": Decimal(line["product_uom_qty"]),
                "order_id": order_id
            }

            prod =  prod_model.read(cr, uid, [line["product_id"]], ["parent_prod_id", "cost_price"])[0]            

            if prod["parent_prod_id"]:
                # Se obtiene el precio del producto padre
                prod_id = prod["parent_prod_id"][0]                
            else:
                prod_id = line["product_id"]
            
            product_price = ext_prod_model.get_pricelist(cr, uid, [prod_id], pricelist_id, partner_id)[prod_id][pricelist_id]
            
            # Aplicar descuento web
            company = company_model.read(cr, uid, [1], ["web_discount"])[0]

            if company["web_discount"]:
                discount = company["web_discount"]
                value["price_unit"] = product_price * (1-discount/100)
            else:
                value["price_unit"] = product_price

            value["purchase_price"] = prod["cost_price"]

            line_model.create(cr, uid, value)

            line["price_unit"] = value["price_unit"]

        return lines
