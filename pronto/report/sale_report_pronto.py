from odoo import tools
from odoo import api, fields, models


class SaleReportPronto(models.Model):
    _name = "sale.report.pronto"
    _description = "Sales Analysis Report PRONTO"
    _auto = False
    _rec_name = 'name'
    _order = 'id desc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done', 'paid']

    name = fields.Char('Número de pedido', readonly=True)
    date = fields.Datetime('Fecha de presupuesto', readonly=True)
    confirmation_date = fields.Datetime('Fecha de confirmación', readonly=True)
    product_id = fields.Many2one('product.product', 'Producto', readonly=True)
    # product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    # product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    # qty_delivered = fields.Float('Qty Delivered', readonly=True)
    # qty_to_invoice = fields.Float('Qty To Invoice', readonly=True)
    # qty_invoiced = fields.Float('Qty Invoiced', readonly=True)
    # partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    # company_id = fields.Many2one('res.company', 'Company', readonly=True)
    # user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    # price_total = fields.Float('Total', readonly=True)
    # price_subtotal = fields.Float('Untaxed Total', readonly=True)
    # untaxed_amount_to_invoice = fields.Float('Untaxed Amount To Invoice', readonly=True)
    # untaxed_amount_invoiced = fields.Float('Untaxed Amount Invoiced', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Plantilla de producto', readonly=True)
    categ_id = fields.Many2one('product.category', 'Categoría', readonly=True)
    # nbr = fields.Integer('# of Lines', readonly=True)
    # pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
    # analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    # team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True, oldname='section_id')
    # country_id = fields.Many2one('res.country', 'Customer Country', readonly=True)
    # commercial_partner_id = fields.Many2one('res.partner', 'Customer Entity', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Estado', readonly=True)
    # weight = fields.Float('Gross Weight', readonly=True)
    # volume = fields.Float('Volume', readonly=True)

    discount = fields.Float('% Descuento', readonly=True)
    # discount_amount = fields.Float('Discount Amount', readonly=True)

    order_id = fields.Many2one('sale.order', '# Pedido', readonly=True)
    line_id = fields.Many2one('sale.order.line', '# Linea', readonly=True)

    costo_total_pesos = fields.Float('Costo total en pesos', readonly=True)
    precio_total_pesos = fields.Float('Precio total en pesos', readonly=True)
    porcentaje = fields.Float('Porcentaje', readonly=True, group_operator='avg')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            l.id as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            s.name as name,
            s.date_order as date,
            s.confirmation_date as confirmation_date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            s.analytic_account_id as analytic_account_id,
            s.team_id as team_id,
            p.product_tmpl_id,
            partner.country_id as country_id,
            partner.commercial_partner_id as commercial_partner_id,
            l.discount as discount,
            s.id as order_id, 
            l.id as line_id,
            l.costo_total_pesos as costo_total_pesos, 
            l.precio_total_pesos as precio_total_pesos, 
            CASE WHEN l.costo_total_pesos > 0 and l.precio_total_pesos > 0 THEN  (l.precio_total_pesos / l.costo_total_pesos - 1) * 100 ELSE 0 END as porcentaje
        """

        for field in fields.values():
            select_ += field

        from_ = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause

        # groupby_ = """
        #     l.product_id,
        #     l.order_id,
        #     t.uom_id,
        #     t.categ_id,
        #     s.name,
        #     s.date_order,
        #     s.confirmation_date,
        #     s.partner_id,
        #     s.user_id,
        #     s.state,
        #     s.company_id,
        #     s.pricelist_id,
        #     s.analytic_account_id,
        #     s.team_id,
        #     p.product_tmpl_id,
        #     partner.country_id,
        #     partner.commercial_partner_id,
        #     l.discount,
        #     s.id %s
        # """ % (groupby)

        # return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

        return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL)' % (with_, select_, from_)

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))