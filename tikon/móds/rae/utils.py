import typing

if typing.TYPE_CHECKING:
    from tikon.móds.rae.red import RedAE

EJE_COH = 'coh'
EJE_ETAPA = 'etapa'
EJE_VÍCTIMA = 'víctima'

RES_POBS = 'Pobs'
RES_EDAD = 'Edad'
RES_CREC = 'Crecimiento'
RES_DEPR = 'Depredación'
RES_REPR = 'Reproducción'
RES_MRTE = 'Muerte'
RES_TRANS = 'Transición'
RES_MOV = 'Movimiento'
RES_ESTOC = 'Estoc'
RES_COHORTES = 'Cohortes'

contexto: list['RedAE'] = []
