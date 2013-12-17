# -*- encoding: utf-8 -*-
##############################################################################
#
#    res_partner
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

class res_partner(osv.osv):
    """añadimos los nuevos campos"""
    
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {   
        'web_username': fields.char('Username'),
        'web_password': fields.char('Password'),
        'web_access': fields.boolean(string='Access')
    }

    _sql_constraints = [
        ('web_username_unique', 'unique(web_username)', 'web_username already exists!')
    ]

