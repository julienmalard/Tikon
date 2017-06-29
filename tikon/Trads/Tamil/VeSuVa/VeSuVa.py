from tikon.RAE import RedAE

class வேளாண்_சுழ்_வலை(RedAE.Red):
    def __init__(தாங்கள், பெயர், திட்டம், உயிரனங்கள்):
        super().__init__(nombre=பெயர், proyecto=திட்டம், organismos=உயிரனங்கள்)

    def உயிரினம்_நீக்க(தாங்கள், உயிரினம்):
        return super().quitar_org(organismo=உயிரினம்)

    def calibrar(தாங்கள், பெயர்=None, aprioris=None, சோதனை=None, படி=1, n_iter=10000, quema=100, extraer=10,
                 dibujar=False):
        return super().calibrar(nombre=பெயர், aprioris=aprioris, exper=சோதனை, paso=படி,
                                n_iter=n_iter, quema=quema, extraer=extraer, dibujar=dibujar)

    def சோதனை_சேருக(தாங்கள், சோதனை, விவரங்கள்):
        super().añadir_exp(experimento=சோதனை, corresp=விவரங்கள்)

    def நடக்க(símismo, சோதனை, படி=1, கடைசியான_நேரம்=None, n_rep_parám=100, n_rep_estoc=100, calibs='Todos',
              usar_especificadas=False, விவரங்கள்=True, ஒவியம்=True, directorio_dib=None, காமி்க்க=True,
              ஒவிய_அமைப்புகள்=None):
        super().simular(exper=சோதனை, paso=படி, tiempo_final=கடைசியான_நேரம், n_rep_parám=n_rep_parám,
                        n_rep_estoc=n_rep_estoc, calibs=calibs, usar_especificadas=usar_especificadas,
                        detalles=விவரங்கள், dibujar=ஒவியம், directorio_dib=directorio_dib, mostrar=காமி்க்க,
                        opciones_dib=ஒவிய_அமைப்புகள்)

    def பரிசோதனை(símismo, சோதனை, calibs=None, படி=1, n_rep_parám=100, n_rep_estoc=100, usar_especificadas=False,
                விவரங்கள்=True, ஒவியம்=True, காமிக்க=False, ஒவிய_அமைப்புகள்=None):
        return super().validar(exper=சோதனை, calibs=calibs, paso=படி, n_rep_parám=n_rep_parám,
                               n_rep_estoc=n_rep_estoc, usar_especificadas=usar_especificadas,
                               detalles=விவரங்கள், dibujar=ஒவியம்,
                               mostrar=காமிக்க, opciones_dib=ஒவிய_அமைப்புகள்)

    def உயிரினம்_சேருக(símismo, உயிரினம்):
        return super().añadir_org(organismo=உயிரினம்)
