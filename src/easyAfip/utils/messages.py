from enum import Enum
from typing import Tuple, List


# ------------------------------
# Enums
# ------------------------------

class FECAEResultEnum(Enum):
    APROBADO = 'A'
    RECHAZADO = 'R'
    PARCIAL = 'P'

    @classmethod
    def get_by_value(cls, value):
        for result in cls:
            if result.value == value:
                return result
        raise ValueError(f"Not existst a result with value {value}")

# ------------------------------
# Messages
# ------------------------------

class FEError:
    def __init__(self, code, msg) -> None:
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"FEError(code={self.code}, msg={self.msg})"

class FEBaseResponse:
    def __init__(self) -> None:
        self.errors = None

    def __str__(self):
        return f"errors={', '.join([error.__str__() for error in self.errors])}"

class FECompUltimoAutorizadoResponse:
    def __init__(self, pto_vta, cbte_tipo, nro_cbte) -> None:
        self.pto_vta = pto_vta
        self.cbte_tipo = cbte_tipo
        self.nro_cbte = nro_cbte
    
    def __str__(self):
        return f"FECompUltimoAutorizadoResponse(pto_vta={self.pto_vta}, cbte_tipo={self.cbte_tipo}, nro_cbte={self.nro_cbte})"


class FECompTotXRequestResponse:
    def __init__(self, reg_x_req) -> None:
        self.reg_x_req = reg_x_req

    def __str__(self):
        return f"FECompTotXRequestResponse(reg_x_req={self.reg_x_req})"


class CbteAsoc:
    def __init__(self, tipo, pto_vta, nro, cuit=None, cbte_fch=None):
        self.tipo = tipo
        self.pto_vta = pto_vta
        self.nro = nro
        self.cuit = cuit
        self.cbte_fch = cbte_fch

class Tributo:
    def __init__(self, id, base_imp, alic, importe, desc=None):
        self.id = id
        self.base_imp = base_imp
        self.alic = alic
        self.importe = importe
        self.desc = desc

class AlicIva:
    def __init__(self, id, base_imp, importe):
        self.id = id
        self.base_imp = base_imp
        self.importe = importe

class Opcional:
    def __init__(self, id=None, valor=None):
        self.id = id
        self.valor = valor

class Comprador:
    def __init__(self, doc_tipo, doc_nro, porcentaje):
        self.doc_tipo = doc_tipo
        self.doc_nro = doc_nro
        self.porcentaje = porcentaje

class PeriodoAsoc:
    def __init__(self, fch_desde=None, fch_hasta=None):
        self.fch_desde = fch_desde
        self.fch_hasta = fch_hasta

class Actividad:
    def __init__(self, id):
        self.id = id

class FECAEDetRequest:
    def __init__(self, concepto=None, doc_tipo=None, doc_nro=None, cbte_desde=None, cbte_hasta=None, imp_total=None,
                 imp_tot_conc=None, imp_neto=None, imp_op_ex=None, imp_trib=None, imp_iva=None, mon_id=None,
                 mon_cotiz=None, cbte_fch=None, fch_serv_desde=None, fch_serv_hasta=None, fch_vto_pago=None,
                 cbtes_asoc=None, tributos=None, iva=None, opcionales=None, compradores=None, periodo_asoc=None,
                 actividades=None):
        self.concepto = concepto
        self.doc_tipo = doc_tipo
        self.doc_nro = doc_nro
        self.cbte_desde = cbte_desde
        self.cbte_hasta = cbte_hasta
        self.cbte_fch = cbte_fch
        self.imp_total = imp_total
        self.imp_tot_conc = imp_tot_conc
        self.imp_neto = imp_neto
        self.imp_op_ex = imp_op_ex
        self.imp_trib = imp_trib
        self.imp_iva = imp_iva
        self.fch_serv_desde = fch_serv_desde
        self.fch_serv_hasta = fch_serv_hasta
        self.fch_vto_pago = fch_vto_pago
        self.mon_id = mon_id
        self.mon_cotiz = mon_cotiz
        self.cbtes_asoc = cbtes_asoc if cbtes_asoc else []
        self.tributos = tributos if tributos else []
        self.iva = iva if iva else []
        self.opcionales = opcionales if opcionales else []
        self.compradores = compradores if compradores else []
        self.periodo_asoc = periodo_asoc
        self.actividades = actividades if actividades else []

    def __str__(self):
        return (f"FECAEDetRequest(concepto={self.concepto}, doc_tipo={self.doc_tipo}, doc_nro={self.doc_nro}, "
                f"cbte_desde={self.cbte_desde}, cbte_hasta={self.cbte_hasta}, cbte_fch={self.cbte_fch}, "
                f"imp_total={self.imp_total}, imp_tot_conc={self.imp_tot_conc}, imp_neto={self.imp_neto}, "
                f"imp_op_ex={self.imp_op_ex}, imp_trib={self.imp_trib}, imp_iva={self.imp_iva}, "
                f"fch_serv_desde={self.fch_serv_desde}, fch_serv_hasta={self.fch_serv_hasta}, "
                f"fch_vto_pago={self.fch_vto_pago}, mon_id={self.mon_id}, mon_cotiz={self.mon_cotiz}, "
                f"cbtes_asoc={self.cbtes_asoc}, tributos={self.tributos}, iva={self.iva}, "
                f"opcionales={self.opcionales}, compradores={self.compradores}, periodo_asoc={self.periodo_asoc}, "
                f"actividades={self.actividades})")


class FECAEDetResponse:
    def __init__(self, concepto: int = None, doc_tipo: int = None, doc_nro: str = None, cbte_desde: int = None, cbte_hasta: int = None, cbte_fch: str = None, resultado: FECAEResultEnum = None):
        self.concepto = concepto
        self.doc_tipo = doc_tipo
        self.doc_nro = doc_nro
        self.cbte_desde = cbte_desde
        self.cbte_hasta = cbte_hasta
        self.cbte_fch = cbte_fch
        self.resultado = resultado
        self.cae = None
        self.cae_fch_vto = None
        self.obs_l = None

    def __str__(self):
        return (f"FECAEDetResponse(concepto={self.concepto}, doc_tipo={self.doc_tipo}, doc_nro={self.doc_nro}, "
                f"cbte_desde={self.cbte_desde}, cbte_hasta={self.cbte_hasta}, cbte_fch={self.cbte_fch}, "
                f"resultado={self.resultado}, cae={self.cae}, cae_fch_vto={self.cae_fch_vto} errors={', '.join([obs.__str__() for obs in self.obs_l]) if self.obs_l else ''})")


class FECAESolicitarResult(FEBaseResponse):
    def __init__(self):
        super().__init__()
        self.cuit = None
        self.pto_vta = None
        self.cbte_tipo = None
        self.fecha_proceso = None
        self.cant_reg = None
        self.resultado = None
        self.reproceso = None
        self.details = []

    def __str__(self):
        return (f"FECAESolicitarResult(cuit={self.cuit}, pto_vta={self.pto_vta}, cbte_tipo={self.cbte_tipo}, "
                f"fecha_proceso={self.fecha_proceso}, cant_reg={self.cant_reg}, resultado={self.resultado}, "
                f"reproceso={self.reproceso}, details={', '.join([str(detail) for detail in self.details])}, {super().__str__()})")




# Exceptions

class WSFEVException(Exception):
    def __init__(self, message: str, result: List[Tuple[int, str]] = None) -> None:
        super().__init__(message)
        self.result = result