# -*- encoding: utf-8 -*-
##############################################################################
#
#    external_adapter_partner
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

class external_adapter_partner(osv.osv):
    """añadimos los nuevos campos"""
    
    _name = "external.adapter.partner"
   
    def login(self, cr, uid, username, password):
        partner_model = self.pool.get('res.partner')
        args = [("web_username","=",username)]

        partner_id = partner_model.search(cr, uid, args)

        if partner_id:
            partner = partner_model.browse(cr, uid, partner_id)[0]

            if partner.web_access:

                if partner.web_password == password:
                    response = {
                        "status": 200,
                        "message": "ok",
                        "data": {
                            "id": partner.id,
                            "webUsername": partner.web_username,
                            "name": partner.name,
                            "pricelistId": partner.property_product_pricelist
                        }
                    }
                else:
                    response = {
                        "status": 401,
                        "message": "incorrect password"
                    }
            else:
                response = {
                "status": 401,
                "message": "user not authorized"
            }
        else:
            response = {
                "status": 401,
                "message": "user not found"
            }

        return response
