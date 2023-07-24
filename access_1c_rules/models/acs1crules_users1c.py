# -*- coding: utf-8 -*-

from odoo import models, fields


class Users1C(models.Model):
    _name = 'acs1crules.users1c'
    _description = '1C:Enterprise users'

    name = fields.Char(string="1C:Enterprise user name")
    id_1c = fields.Char(string="Internal user code (as in 1C:Enterprise database)")
