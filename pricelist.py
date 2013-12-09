# -*- encoding: utf-8 -*-
##############################################################################
#
#    cbk_crm_information: CRM Information Tab
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

class cbk_product_pricelist(osv.osv):
    """añadimos los nuevos campos"""
    
    _name = "cbk.product.pricelist"
    
    def price_get_multi(self, cr, uid, pricelist_ids, products_by_qty_by_partner, context=None):

        pl_model = self.pool.get('product.pricelist')

        results = pl_model.price_get_multi(cr, uid, pricelist_ids, products_by_qty_by_partner, context)

        return json.dumps(results)