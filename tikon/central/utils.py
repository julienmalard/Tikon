from tikon.utils import EJE_PARÁMS, EJE_ESTOC, EJE_PARC


def gen_coords_base(n_rep_estoc, n_rep_paráms, parc):
    return {EJE_PARÁMS: range(n_rep_paráms), EJE_ESTOC: range(n_rep_estoc), EJE_PARC: parc}
