from collections import defaultdict
from odoo import models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        # Si venimos de un picking y hay líneas editables, usamos esas cantidades
        if self.picking_id and self.line_ids:
            quantities = defaultdict(int)
            for line in self.line_ids:
                if line.move_quantity <= 0:
                    continue
                quantities[line.move_id.product_id.id] += int(line.move_quantity)
            data['quantity_by_product'] = dict(quantities)
        return xml_id, data
