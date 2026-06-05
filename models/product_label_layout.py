from collections import defaultdict
from odoo import Command, api, fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    line_product_ids = fields.One2many('product.label.layout.line', 'wizard_id', string='Products')

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        # Si venimos de productos (la accion pasa default_product_ids o default_product_tmpl_ids)
        if not rec.get('line_product_ids') and not rec.get('line_ids'):
            product_ids = self._context.get('default_product_ids') or []
            product_tmpl_ids = self._context.get('default_product_tmpl_ids') or []

            if product_ids:
                products = self.env['product.product'].browse(product_ids).exists()
                rec['line_product_ids'] = [
                    (0, 0, {'product_id': p.id, 'quantity': 1})
                    for p in products
                ]
            elif product_tmpl_ids:
                templates = self.env['product.template'].browse(product_tmpl_ids).exists()
                variants = templates.mapped('product_variant_ids').exists()
                rec['line_product_ids'] = [
                    (0, 0, {'product_id': p.id, 'quantity': 1})
                    for p in variants
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
