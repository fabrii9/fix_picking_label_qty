from collections import defaultdict
from odoo import Command, api, fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    line_product_ids = fields.One2many('product.label.layout.line', 'wizard_id', string='Products')

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        active_ids = self._context.get("active_ids") or self._context.get("active_id")
        active_model = self._context.get("active_model")

        if active_model == 'product.product' and active_ids:
            products = self.env['product.product'].browse(active_ids)
            rec['line_product_ids'] = [
                Command.create({'product_id': p.id, 'quantity': 1})
                for p in products
            ]
        elif active_model == 'product.template' and active_ids:
            templates = self.env['product.template'].browse(active_ids)
            rec['line_product_ids'] = [
                Command.create({'product_id': p.id, 'quantity': 1})
                for p in templates.mapped('product_variant_ids')
            ]
        return rec

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        if self.line_ids:
            quantities = defaultdict(int)
            for line in self.line_ids:
                if line.move_quantity <= 0:
                    continue
                quantities[line.move_id.product_id.id] += int(line.move_quantity)
            data['quantity_by_product'] = dict(quantities)
        elif self.line_product_ids:
            quantities = defaultdict(int)
            for line in self.line_product_ids:
                if line.quantity <= 0:
                    continue
                quantities[line.product_id.id] += int(line.quantity)
            data['quantity_by_product'] = dict(quantities)
        return xml_id, data


class StockPickingZplLines(models.TransientModel):
    _inherit = 'stock.picking.zpl.lines'

    @api.constrains('move_quantity')
    def _check_move_quantity(self):
        # Se elimina la restricción que impide poner cantidades mayores a la original
        pass


class ProductLabelLayoutLine(models.TransientModel):
    _name = 'product.label.layout.line'
    _description = 'Product Label Layout Line'

    wizard_id = fields.Many2one('product.label.layout')
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(default=1, required=True)
