# -*- coding: utf-8 -*-

from odoo import models, fields


class Users1CGroups(models.Model):
    _name = 'acs1crules.users1c_groups'
    _description = 'Access groups of 1C:Enterprise users'

    name = fields.Char(string="Access group name")
    users1c_ids = fields.Many2many('acs1crules.users1c',string='Group members')
