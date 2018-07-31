# -*- coding: utf-8 -*-
{
    'name': "tvp_complementos",

    'summary': """
        Se requiere complementar y editar los apartados de Empleados y Contratos de
        el área de Recursos Humanos""",

    'description': """
        Complementos en el área de empleados y contratos de manera directa
    """,

    'author': "TVPromo :: Edgar Ocampo",
    'website': "http://www.tvp.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/complementos_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
}