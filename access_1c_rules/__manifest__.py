# -*- coding: utf-8 -*-
{
    'name': "acs1crules",

    'summary': """
        Defines, stores and returns extended permissions for 1C:Enterprise.""",

    'description': """
        Defines, stores and returns check result of extended access rules for 1C:Enterprise configurations, which has lack of complex document control rules.
        Main goal of this app - proof of concept, and it solves a fairly specific task.
    """,

    'author': "SergeMiletos",
    'website': "http://localhost:8069",
    'license': 'AGPL-3',
    'category': 'Others',
    'application': True,
    'version': '0.9',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/acs1crules_security.xml',
        'security/ir.model.access.csv',
        'views/acs1crules_menu.xml',
        'views/acs1crules_usr1crules_view.xml',
        'views/acs1crules_view_with_button.xml',
        'views/acs1crules_users1c_view.xml',
        'views/acs1crules_users1c_groups_view.xml',
        'reports/acs1crules_report.xml',
        'reports/acs1crules_reportDoubleTable.xml',
    ],
    'qweb': [
        'static/src/xml/colspan.xml',
    ],
    'assets': {
        'web.assets_backend': [
           'access_1c_rules/static/src/js/tree_button.js',
        ],
        'web.assets_qweb': [
            'access_1c_rules/static/src/xml/tree_button.xml',
        ], 
    }
}