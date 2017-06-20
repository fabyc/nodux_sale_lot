#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval

__all__ = ['SaleLine', 'SaleLot']
__metaclass__ = PoolMeta


class SaleLine:
    __name__ = 'sale.line'

    product_type = fields.Function(fields.Char('Product Type'),
        'on_change_with_product_type')
    lot = fields.One2Many('sale.lot', 'line', 'Lot',
        states={
            'invisible': ((Eval('type') != 'line')
                | (Eval('product_type') == 'service')),
            },
        depends=['type', 'product', 'product_type'])

    @fields.depends('product')
    def on_change_with_product_type(self, name=None):
        if not self.product:
            return
        return self.product.type

    @fields.depends('product', 'lot', 'description')
    def on_change_lot(self):
        res = {}
        description=""
        if self.lot and self.product:
            if self.description:
                for l in self.lot:
                    if l.lot:
                        if l.lot.number in self.description:
                            pass
                        else:
                            description = " "+l.lot.number+" "
                if description != "":
                    res['description'] = self.description+description
            else:
                for l in self.lot:
                    if l.lot:
                        description = " "+l.lot.number+" "
                if description != "":
                    res['description'] = " Series"+description
        return res

    def get_move(self, shipment_type):
        move = super(SaleLine, self).get_move(shipment_type)
        if move and self.lot:
            for lote in self.lot:
                if lote.lot:
                    move.lot = lote.lot
                    lot = lote.lot
                    lot.used_lot = 'used'
                    lot.save()
        return move


class SaleLot(ModelSQL, ModelView):
    'Serie de Producto'
    __name__ = 'sale.lot'

    line = fields.Many2One('sale.line', 'Line')

    lot = fields.Many2One('stock.lot', 'Lot',
        domain=[
            ('used_lot', '=', 'no_used'),
            ])
    sequence = fields.Integer('Sequence')

    @classmethod
    def __setup__(cls):
        super(SaleLot, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))
