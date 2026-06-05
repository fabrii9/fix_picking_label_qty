from collections import defaultdict
from odoo import Command, api, fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    line_product_ids = fields.One2many('product.label.layout.line', 'wizard_id', string='Products')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.line_product_ids and not rec.line_ids:
                if rec.product_ids:
                    rec.line_product_ids = [
                        Command.create({'product_id': p.id, 'quantity': 1})
                        for p in rec.product_ids
                    ]
                elif rec.product_tmpl_ids:
                    rec.line_product_ids = [
                        Command.create({'product_id': p.id, 'quantity': 1})
                        for p in rec.product_tmpl_ids.mapped('product_variant_ids')
                    ]
        return records

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
