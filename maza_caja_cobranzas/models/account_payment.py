# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Canal por el que ingresó el cobro. Es LA etiqueta que permite que el
    # cierre de lote diario (tablero) concilie mostrador + industria: el
    # posnet y el QR son compartidos entre ambos canales.
    maza_canal = fields.Selection(
        [
            ('mostrador', 'Mostrador (PDV)'),
            ('caja_industria', 'Caja — cobranza industria'),
            ('admin', 'Administración'),
        ],
        string='Canal de cobro',
        index=True,
        help='Mostrador: cobros del punto de venta. Caja — industria: facturas '
             'del canal industrial cobradas en la caja del mostrador. '
             'Administración: cobranzas registradas fuera de la caja '
             '(transferencias y cheques que envían los clientes).',
    )
