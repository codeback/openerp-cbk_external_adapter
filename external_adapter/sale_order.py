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
