from tikon.RAE.RedAE import Red


class Red(Red):

    def añadir_org(தன், organismo):
        return super().añadir_org(organismo=organismo)

    def quitar_org(தன், organismo):
        return super().quitar_org(organismo=organismo)

    def actualizar(தன்):
        return super().actualizar()

    def dibujar(தன், mostrar=True, directorio=None, exper=None, n_líneas=0, incert="componentes"):
        return super().dibujar(mostrar=mostrar, directorio=directorio, exper=exper, n_líneas=n_líneas, incert=incert)

    def incrementar(தன், paso, i, detalles, mov=False, extrn=None):
        return super().incrementar(paso=paso, i=i, detalles=detalles, mov=mov, extrn=extrn)

    def añadir_exp(தன், experimento, corresp=None, corresp_pobs=None, corresp_crec=None, corresp_repr=None,
                   corresp_trans=None, corresp_muertes=None):
        return super().añadir_exp(experimento=experimento, corresp=corresp, corresp_pobs=corresp_pobs,
                                  corresp_crec=corresp_crec, corresp_repr=corresp_repr, corresp_trans=corresp_trans,
                                  corresp_muertes=corresp_muertes)

    def especificar_apriori(தன்):
        return super().especificar_apriori()
