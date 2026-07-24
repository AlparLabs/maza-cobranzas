# -*- coding: utf-8 -*-
{
    'name': 'Maza · Cobranzas de Caja',
    'version': '19.0.0.1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Cobranza rápida de facturas de venta industrial desde la caja (Electricidad Maza)',
    'description': """
Pantalla única de cobranza para la caja del mostrador: la cajera busca el
cliente, elige facturas puntuales o imputa al saldo, y cobra con los mismos
conceptos del punto de venta (efectivo, Mercado Pago, transferencia, tarjeta,
cheque diferido a cartera de terceros).

Cada cobro queda etiquetado con su CANAL (mostrador / caja-industria /
administración) para que el cierre de lote diario del tablero concilie solo.

Estado: MVP v0.1 — para validar en el entorno de STAGING de Odoo SH antes de
producción. Los cobros con cheque abren el formulario nativo de pago con la
localización argentina (l10n_latam_check) prefilleado: no se reimplementa la
cartera de cheques.
    """,
    'author': 'AlparData',
    'website': 'https://www.alpardata.com.ar',
    'license': 'LGPL-3',
    'depends': ['account', 'l10n_latam_check'],
    'data': [
        'security/maza_cobranzas_security.xml',
        'security/ir.model.access.csv',
        'wizard/cobranza_caja_views.xml',
    ],
    'installable': True,
    'application': False,
}
