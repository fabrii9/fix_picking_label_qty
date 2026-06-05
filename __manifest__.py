{
    'name': 'Fix Etiquetas Picking - Cantidades Editables',
    'version': '1.0.0',
    'category': 'Warehouse',
    'summary': 'Respeta las cantidades manuales al imprimir etiquetas desde un albarán.',
    'description': """
Cuando se imprimen etiquetas de productos desde un picking/recepción, el wizard
permite editar la cantidad por línea. Este módulo hace que esas cantidades
editadas sean respetadas por todos los formatos de etiqueta, incluyendo
Pantum 50x25.
    """,
    'depends': ['stock_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_label_layout_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
