from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import base64
from io import BytesIO
from xlrd import open_workbook

class ProductPricelistWizard(models.TransientModel):
    _name = 'product.pricelist.wizard'
    _description = 'Actualización de precios'

    pricelist_id = fields.Many2one('product.pricelist',string='Lista de precios')
    excel_file_for_import = fields.Binary("Archivo")

    @api.model
    def default_get(self, field_names):
        defaults = super(
            ProductPricelistWizard, self).default_get(field_names)
        defaults['pricelist_id'] = self.env.context['active_id']
        return defaults
    
    def do_update(self):
        try:
            inputx = BytesIO()
            inputx.write(base64.decodestring(self.excel_file_for_import))
            book = open_workbook(file_contents=inputx.getvalue())
        except TypeError as e:
            raise UserError(u'ERROR: {}'.format(e))

        sheet = book.sheets()[0]
        
        modificaciones = 0
        altas = 0
        for i in list(range(sheet.nrows)):
            default_code = sheet.cell(i, 0).value
            product = self.env['product.template'].search([('default_code','=',default_code)])
            if not product:
                raise UserError("El producto con código %s no existe. No se realizará ninguna actualización." % default_code)

            pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id','=',self.pricelist_id.id),('product_tmpl_id','=',product.id)])
            # import pdb;pdb.set_trace()
            if len(pricelist_item) > 1:
                raise UserError("El precio del producto con código %s esta cargado %s veces en esta lista. No se realizará ninguna actualización." % (default_code,len(pricelist_item)))

            new_price = sheet.cell(i, 1).value
            if pricelist_item:
                # este control no tiene sentido. si no se aplica a producto, no va a tener el campo product_tmpl_id informado y no va a pasar por acá
                # if not (pricelist_item.applied_on == '1_product'):
                #     raise UserError("El precio del producto con código %s no esta configurado como 'Aplicar sobre producto'. No se realizará ninguna actualización." % default_code)

                if not (pricelist_item.compute_price == 'fixed'):
                    raise UserError("El precio del producto con código %s no esta configurado como 'fijo'. No se realizará ninguna actualización." % default_code)

                pricelist_item.update({'fixed_price': new_price})
                modificaciones += 1
            else:
                vals = {'pricelist_id': self.pricelist_id.id,
                        'applied_on': '1_product',
                        'product_tmpl_id': product.id,
                        'compute_price': 'fixed',
                        'fixed_price': new_price}
                
                self.env['product.pricelist.item'].create(vals)
                altas += 1

        self.env.user.notify_success(message="Modificaciones: %s Altas: %s" % (modificaciones,altas))
        # raise Warning(_("Modificaciones: %s Altas: %s" % (modificaciones,altas)))

        return

    