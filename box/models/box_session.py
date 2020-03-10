##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BoxSession(models.Model):
    _name = 'box.session'
    _order = 'id desc'
    _description = 'Sesiones de caja'

    POS_SESSION_STATE = [
        ('opening_control', 'CONTROL DE APERTURA'),  # method action_box_session_open
        ('opened', 'EN PROCESO'),               # method action_box_session_closing_control
        ('closing_control', 'CONTROL DE CIERRE'),  # method action_box_session_close
        ('closed', 'CERRADO & PUBLICADO'),
    ]

    box_id = fields.Many2one(
        'box.box', string='Caja',
        help="Caja física que usará.",
        required=True,
        index=True)

    name = fields.Char(string='ID de la sesión', required=True, readonly=True, default='/')

    user_id = fields.Many2one(
        'res.users', string='Responsable',
        required=True,
        index=True,
        readonly=True,
        states={'opening_control': [('readonly', False)]},
        default=lambda self: self.env.uid)

    start_at = fields.Datetime(string='Fecha Apertura', readonly=True)
    stop_at = fields.Datetime(string='Fecha Cierre', readonly=True, copy=False)

    state = fields.Selection(
        POS_SESSION_STATE, string='Status',
        required=True, readonly=True,
        index=True, copy=False, default='opening_control')
    
    journal_ids = fields.Many2many(
        'account.journal',
        related='box_id.journal_ids',
        readonly=True,
        string='Métodos de pago disponibles')

    _sql_constraints = [('uniq_name', 'unique(name)', "El nombre de esta sesión de caja debe ser único !")]

    box_session_journal_ids = fields.One2many('box.session.journal', 'box_session_id', readonly=True)
    
    # statement_ids = fields.One2many('account.bank.statement', 'pos_session_id', string='Bank Statement', readonly=True)

    cash_control = fields.Boolean(compute='_compute_cash_all', string='Has Cash Control',default=True,readonly=True)
    cash_journal_id = fields.Many2one('account.journal', compute='_compute_cash_all', string='Diario de efectivo', store=True)
    cash_register_id = fields.Many2one('box.session.journal', compute='_compute_cash_all', string='Caja Registradora', store=True)

    cash_register_balance_end_real = fields.Monetary(
        related='cash_register_id.balance_end_real',
        string="Saldo final",
        help="",
        readonly=True)
    cash_register_balance_start = fields.Monetary(
        related='cash_register_id.balance_start',
        string="Saldo inicial",
        help="",
        readonly=True)
    cash_register_total_entry_encoding = fields.Monetary(
        related='cash_register_id.total_entry_encoding',
        string='Total de operaciones en efectivo',
        readonly=True,
        help="")
    cash_register_balance_end = fields.Monetary(
        related='cash_register_id.balance_end',
        digits=0,
        string="Saldo final teórico",
        help="",
        readonly=True)
    cash_register_difference = fields.Monetary(
        related='cash_register_id.difference',
        string='Diferencia',
        help="",
        readonly=True)

    currency_id = fields.Many2one('res.currency', compute='_compute_currency', oldname='currency', string="Currency")

    company_id = fields.Many2one('res.company', related='cash_journal_id.company_id', string='Company', store=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get('account.bank.statement'))

    @api.one
    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id

    @api.depends('box_id', 'box_session_journal_ids')
    def _compute_cash_all(self):
        for session in self:
            session.cash_journal_id = session.cash_register_id = session.cash_control = False
            if session.box_id.cash_control:
                for statement in session.box_session_journal_ids:
                    if statement.journal_id.type == 'cash':
                        session.cash_control = True
                        session.cash_journal_id = statement.journal_id.id
                        session.cash_register_id = statement.id
                # if not session.cash_control and session.state != 'closed':
                #     raise UserError(_("Cash control can only be applied to cash journals."))
    
    @api.model
    def create(self, values):
        # config_id = values.get('config_id') or self.env.context.get('default_config_id')
        box_id = values.get('box_id')
        if not box_id:
            raise UserError(_("You should assign a Point of Sale to your session."))

        # journal_id is not required on the pos_config because it does not
        # exists at the installation. If nothing is configured at the
        # installation we do the minimal configuration. Impossible to do in
        # the .xml files as the CoA is not yet installed.
        box_box = self.env['box.box'].browse(box_id)
        ctx = dict(self.env.context, company_id=box_box.company_id.id)
        # if not box_box.journal_id:
        #     default_journals = box_box.with_context(ctx).default_get(['journal_id'])
        #     if (not default_journals.get('journal_id')):
        #         raise UserError(_("Unable to open the session. You have to assign a sales journal to your point of sale."))
        #     box_box.with_context(ctx).sudo().write({
        #         'journal_id': default_journals['journal_id']})
        # define some cash journal if no payment method exists
        if not box_box.journal_ids:
            Journal = self.env['account.journal']
            journals = Journal.with_context(ctx).search([('type', '=', 'cash')])
            if not journals:
                journals = Journal.with_context(ctx).search([('type', '=', 'cash')])
                # if not journals:
                #     journals = Journal.with_context(ctx).search([('journal_user', '=', True)])
            if not journals:
                raise ValidationError(_("No payment method configured! \nEither no Chart of Account is installed or no payment method is configured for this POS."))
            # journals.sudo().write({'journal_user': True})
            box_box.sudo().write({'journal_ids': [(6, 0, journals.ids)]})

        # import pdb; pdb.set_trace()
        # box_name = box_box.name + self.env['ir.sequence'].with_context(ctx).next_by_code('box.session')
        # import pdb; pdb.set_trace()
        # if values.get('name'):
        #     box_name += ' ' + values['name']
        
        # session_name = box_box.name + '/' + str(box_box.sequence_id.number_next_actual)
        session_name = box_box.name + box_box.sequence_id.next_by_id()

        # import pdb; pdb.set_trace()

        uid = self.env.user.id

        values.update({
            'name': session_name,
            # 'box_session_journal_ids': [(6, 0, statements)],
            'box_id': box_id
        })

        res = super(BoxSession, self.with_context(ctx).sudo(uid)).create(values)
        # if not pos_config.cash_control:

        session_journals = []
        ABS = self.env['box.session.journal']
        # uid = SUPERUSER_ID if self.env.user.has_group('point_of_sale.group_pos_user') else self.env.user.id

        for journal in box_box.journal_ids:
            # set the journal_id which should be used by
            # account.bank.statement to set the opening balance of the
            # newly created bank statement
            ctx['journal_id'] = journal.id
            st_values = {
                'journal_id': journal.id,
                # 'user_id': self.env.user.id,
                # 'name': box_name,
                'box_session_id': res.id
                # ,'balance_start': self.env["account.bank.statement"]._get_opening_balance(journal.id) if journal.type == 'cash' else 0
            }

            session_journals.append(ABS.with_context(ctx).sudo(uid).create(st_values).id)

        values.update({
            'box_session_journal_ids': [(6, 0, session_journals)]
        })

        # res.action_box_session_open()

        return res

    @api.multi
    def action_box_session_open(self):
        # second browse because we need to refetch the data from the DB for cash_register_id
        # we only open sessions that haven't already been opened
        for session in self.filtered(lambda session: session.state == 'opening_control'):
            if session.cash_register_balance_start == 0:
                raise UserError(_("Debe informar el saldo inicial"))
            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            values['state'] = 'opened'
            session.write(values)
            # session.statement_ids.button_open()
        return True

    @api.multi
    def action_box_session_closing_control(self):
        # self._check_box_session_balance()

        for session in self:
            if session.cash_register_balance_end < 0:
                raise UserError(_("El saldo final no puede ser negativo."))
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.box_id.cash_control:
                session.action_box_session_close()

    @api.multi
    def _check_box_session_balance(self):
        # el saldo final real, debería coincidir con el teórico. y sino que cargue el movimiento de ajuste?

        for session in self:
            # if session.cash_register_difference != 0:
            #     raise UserError(_("Para poder cerrar la caja la diferencia entre el saldo inicial y el final debe ser cero."))
            if session.cash_register_balance_end < 0:
                raise UserError(_("El saldo final no puede ser negativo."))
            if session.cash_register_balance_end != session.cash_register_balance_end_real:
                raise UserError(_("El saldo final teórico debe coincidir con el real. Informe correctamente el saldo real o haga el ajuste correspondiente."))


    @api.multi
    def action_box_session_validate(self):
        self._check_box_session_balance()
        self.action_box_session_close()

    @api.multi
    def action_box_session_close(self):
        # Close CashBox
        self.write({'state': 'closed'})
        
        self.env['box.box'].browse(self.box_id.id).write({'last_closed_session_id': self.id})

        # last_close_session_id
        return {
            'type': 'ir.actions.client',
            'name': 'Menu Caja',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('box.menu_box_root').id},
        }

    def box_cash_in(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ingresar Efectivo',
            'view_mode': 'form',
            'res_model': 'box.session.cash.in',
            'target': 'new'  
        }

    def box_cash_out(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Retirar Efectivo',
            'view_mode': 'form',
            'res_model': 'box.session.cash.out',
            'target': 'new'  
        }

    def box_cash_open(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Abrir caja',
            'view_mode': 'form',
            'res_model': 'box.session.cash.open',
            'target': 'new'  
        }
    
    def box_cash_close(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cerrar caja',
            'view_mode': 'form',
            'res_model': 'box.session.cash.close',
            'target': 'new'  
        }