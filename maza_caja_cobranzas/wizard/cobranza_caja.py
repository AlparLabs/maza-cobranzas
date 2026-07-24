# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class CobranzaCajaWizard(models.TransientModel):
    """Cobranza rápida desde la caja para facturas de venta industrial.

    Flujo pensado para la cajera:
      1. Elige el cliente → ve saldo y facturas pendientes.
      2. Elige facturas puntuales o imputa al saldo de la cuenta.
      3. Elige el método (mismos conceptos que el mostrador).
      4. Cobrar → crea el account.payment posteado, concilia contra las
         facturas elegidas y lo etiqueta con canal 'caja_industria'.

    Cheques: si el diario elegido opera cheques de terceros (l10n_latam),
    NO se cobra en silencio — se abre el formulario nativo de pago
    prefilleado para cargar número/banco/vencimiento, y el cheque queda en
    la cartera de terceros como siempre.
    """
    _name = 'maza.cobranza.caja.wizard'
    _description = 'Cobranza de Caja (venta industrial)'

    partner_id = fields.Many2one(
        'res.partner', string='Cliente', required=True,
        domain=[('customer_rank', '>', 0)])
    saldo_pendiente = fields.Monetary(
        string='Saldo de cuenta corriente', compute='_compute_saldo',
        currency_field='currency_id')
    aplicar = fields.Selection(
        [('facturas', 'Facturas puntuales'), ('saldo', 'Al saldo de la cuenta')],
        string='Imputar a', default='facturas', required=True)
    invoice_ids = fields.Many2many(
        'account.move', string='Facturas a cobrar',
        domain="[('partner_id', '=', partner_id),"
               " ('move_type', '=', 'out_invoice'),"
               " ('state', '=', 'posted'),"
               " ('payment_state', 'in', ('not_paid', 'partial'))]")
    total_seleccionado = fields.Monetary(
        string='Total seleccionado', compute='_compute_total_seleccionado',
        currency_field='currency_id')
    journal_id = fields.Many2one(
        'account.journal', string='Método de cobro', required=True,
        domain=[('type', 'in', ('bank', 'cash'))])
    es_cheque = fields.Boolean(compute='_compute_es_cheque')
    amount = fields.Monetary(string='Importe cobrado', required=True,
                             currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    payment_date = fields.Date(
        string='Fecha', default=fields.Date.context_today, required=True)
    memo = fields.Char(string='Referencia')

    # ─── Computes ────────────────────────────────────────────────────────────
    @api.depends('partner_id')
    def _compute_saldo(self):
        for w in self:
            if not w.partner_id:
                w.saldo_pendiente = 0.0
                continue
            lineas = self.env['account.move.line'].search([
                ('partner_id', '=', w.partner_id.commercial_partner_id.id),
                ('account_id.account_type', '=', 'asset_receivable'),
                ('parent_state', '=', 'posted'),
                ('full_reconcile_id', '=', False),
            ])
            w.saldo_pendiente = sum(lineas.mapped('amount_residual'))

    @api.depends('invoice_ids', 'aplicar', 'saldo_pendiente')
    def _compute_total_seleccionado(self):
        for w in self:
            if w.aplicar == 'facturas':
                w.total_seleccionado = sum(w.invoice_ids.mapped('amount_residual'))
            else:
                w.total_seleccionado = w.saldo_pendiente

    @api.depends('journal_id')
    def _compute_es_cheque(self):
        for w in self:
            w.es_cheque = bool(w.journal_id.inbound_payment_method_line_ids.filtered(
                lambda l: l.code == 'new_third_party_checks'))

    @api.onchange('invoice_ids', 'aplicar')
    def _onchange_sugerir_importe(self):
        # Sugerir el total de lo elegido; la cajera puede cobrar parcial.
        if self.total_seleccionado > 0:
            self.amount = self.total_seleccionado

    # ─── Acción principal ────────────────────────────────────────────────────
    def action_cobrar(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError('El importe a cobrar debe ser mayor a cero.')
        if self.aplicar == 'facturas' and not self.invoice_ids:
            raise UserError('Elegí al menos una factura, o cambiá a "Al saldo de la cuenta".')

        vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'memo': self.memo or (
                'Cobranza caja: ' + ', '.join(self.invoice_ids.mapped('name'))
                if self.invoice_ids else 'Cobranza caja (a cuenta)'),
            'maza_canal': 'caja_industria',
        }

        # Cheques: abrir el formulario NATIVO prefilleado para cargar los
        # datos del cheque (número, banco, vencimiento). La localización AR
        # se encarga de dejarlo en la cartera de terceros.
        if self.es_cheque:
            metodo = self.journal_id.inbound_payment_method_line_ids.filtered(
                lambda l: l.code == 'new_third_party_checks')[:1]
            vals['payment_method_line_id'] = metodo.id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cobranza con cheque',
                'res_model': 'account.payment',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_%s' % k: v for k, v in vals.items()},
            }

        pago = self.env['account.payment'].create(vals)
        pago.action_post()

        # Conciliar contra las facturas elegidas (en orden, hasta agotar el
        # importe). Si es "al saldo", queda como crédito sin imputar y Odoo
        # lo ofrece al pagar cualquier factura del cliente.
        if self.aplicar == 'facturas':
            lineas_pago = pago.move_id.line_ids.filtered(
                lambda l: l.account_id.account_type == 'asset_receivable'
                and not l.reconciled)
            for factura in self.invoice_ids.sorted('invoice_date_due'):
                if not lineas_pago.filtered(lambda l: not l.reconciled):
                    break
                lineas_fact = factura.line_ids.filtered(
                    lambda l: l.account_id.account_type == 'asset_receivable'
                    and not l.reconciled)
                (lineas_pago + lineas_fact).reconcile()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cobranza registrada',
            'res_model': 'account.payment',
            'res_id': pago.id,
            'view_mode': 'form',
            'target': 'current',
        }
