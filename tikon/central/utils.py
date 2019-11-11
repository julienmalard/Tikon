EJE_PARÁMS = 'paráms'
EJE_ESTOC = 'estoc'
EJE_TIEMPO = 'tiempo'
EJE_PARC = 'parcela'
EJE_DEST = 'dest'
EJE_COORD = 'coord'


def gen_coords_base(n_rep_estoc, n_rep_paráms, parc):
    return {EJE_PARÁMS: range(n_rep_paráms), EJE_ESTOC: range(n_rep_estoc), EJE_PARC: parc}
