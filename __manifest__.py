{
    'name': 'Caffeine Discount',
    'version': '17.0.1.0.0',
    'summary': (
        'Caffeine Discount is a loyalty and discount management module for coffee '
        'shops. It allows customers to earn rewards, manage discounts, and benefit '
        'from personalized loyalty programs to enhance their experience.'
    ),
    'category': 'Sales',
    'author': 'Artemius-K',
    'website': 'https://github.com/artrak/caffeine_discount.git',
    'license': 'OPL-1',

    'depends': [
        'base',
        'product',
        'sale',
        'point_of_sale',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [
        # 'security/caffeine_discount_groups.xml'
        'security/ir.model.access.csv',
        # 'security/caffeine_discount_security.xml'

        'wizard/discount_dates_wizard_views.xml',

        'views/client_views.xml',
        'views/barista_views.xml',
        'views/product_views.xml',
        'views/order_views.xml',
        'views/order_line_views.xml',
        'views/discount_views.xml',
        'views/menu.xml',


        'data/product_category_data.xml',

        'report/order_report_template.xml',

    ],

    'demo': [
        'demo/client_demo.xml',
        'demo/barista_demo.xml',
        'demo/product_demo.xml',
        'demo/discount_demo.xml',
        'demo/order_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/caffeine_discount/static/src/css/style.css',  # Шлях до вашого CSS
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png'
    ],
}
