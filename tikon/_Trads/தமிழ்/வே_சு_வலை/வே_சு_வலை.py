from tikon.RAE import RedAE


class வேளாண்_சுழ்_வலை(RedAE.Red):
    def __init__(தாங்கள், பெயர், திட்டம், உயிரனங்கள்):
        super().__init__(nombre=பெயர், proyecto=திட்டம், organismos=உயிரனங்கள்)

    def உயிரினம்_நீக்க(தாங்கள், உயிரினம்):
        return super().quitar_org(organismo=உயிரினம்)

    def அளவிடு(தாங்கள், பெயர்=None, முதல்_நிகழ்வெண்_பரவல்=None, சோதனை=None,
               படி=1, திரும்ப_எண்=10000, எரி=100, சேமிக்க=10,
               ஒவியம்=False):
        return super().calibrar(nombre=பெயர், aprioris=முதல்_நிகழ்வெண்_பரவல், exper=சோதனை, paso=படி,
                                n_iter=திரும்ப_எண், quema=எரி, extraer=சேமிக்க, dibujar=ஒவியம்)

    def சோதனை_சேருக(தாங்கள், சோதனை, விவரங்கள்):
        super().añadir_exp(experimento=சோதனை, corresp=விவரங்கள்)

    def நடக்க(தாங்கள், சோதனை, படி=1, கடைசியான_நாள்=None, பண்பளவு_திரும்ப_எண்=100,
              சமவாய்ப்பு_திரும்ப_எண்=100,
              அளவிடுகள்='Todos', குறிப்பிடபட்ட_பயன்_செய்ய=False,
              விவரங்கள்=True, ஒவியம்=True, ஒவியம்_கோப்புறை=None, காமி்க்க=True,
              ஒவிய_அமைப்புகள்=None):
        super().simular(exper=சோதனை, paso=படி, tiempo_final=கடைசியான_நாள்,
                        n_rep_parám=பண்பளவு_திரும்ப_எண்,
                        n_rep_estoc=சமவாய்ப்பு_திரும்ப_எண், calibs=அளவிடுகள்,
                        usar_especificadas=குறிப்பிடபட்ட_பயன்_செய்ய,
                        detalles=விவரங்கள், dibujar=ஒவியம், directorio_dib=ஒவியம்_கோப்புறை, mostrar=காமி்க்க,
                        opciones_dib=ஒவிய_அமைப்புகள்)

    def செல்லுபடியாக்கு(தாங்கள், சோதனை, அளவிடுகள்=None, படி=1,
                        பண்பளவு_திரும்ப_எண்=100, சமவாய்ப்பு_திரும்ப_எண்=100,
                        குறிப்பிடபட்ட_பயன்_செய்ய=False,
                        விவரங்கள்=True, ஒவியம்=True, காமிக்க=False, ஒவிய_அமைப்புகள்=None):
        return super().validar(exper=சோதனை, calibs=அளவிடுகள், paso=படி,
                               n_rep_parám=பண்பளவு_திரும்ப_எண்,
                               n_rep_estoc=சமவாய்ப்பு_திரும்ப_எண்,
                               usar_especificadas=குறிப்பிடபட்ட_பயன்_செய்ய,
                               detalles=விவரங்கள், dibujar=ஒவியம்,
                               mostrar=காமிக்க, opciones_dib=ஒவிய_அமைப்புகள்)

    def உயிரினம்_சேருக(தாங்கள், உயிரினம்):
        return super().añadir_org(organismo=உயிரினம்)
