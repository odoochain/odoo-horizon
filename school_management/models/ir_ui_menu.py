# Copyright 2024 Neodiensis
#     License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
#from pprint import pprint
from odoo import fields, models

_logger = logging.getLogger(__name__)

class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    display_in_home_menu = fields.Boolean(name="Displayed in home menu", default=False)

    def load_web_menus(self, debug):
        web_menus = super().load_web_menus(debug)
        new_web_menus = {} #dict
        selection = self.search([('display_in_home_menu', '=', True)]).ids

        for key, web_menu in web_menus.items():
            try:
                selection.index(web_menu["id"])
                display_in_home_menu = True
            except ValueError:
                display_in_home_menu = False
            web_menu["displayInHomeMenu"] = display_in_home_menu
            new_web_menus[key] = web_menu

        return new_web_menus
        