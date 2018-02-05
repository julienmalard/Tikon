from tikon.RAE.Organismo import Organismo


class Organismo(Organismo):

    def actualizar(தன்):
        return super().actualizar()

    def añadir_etapa(தன், பெயர், posición, ecuaciones, lím_error=0.1):
        return super().añadir_etapa(nombre=பெயர், posición=posición, ecuaciones=ecuaciones, lím_error=lím_error)

    def quitar_etapa(தன், பெயர்):
        return super().quitar_etapa(nombre=பெயர்)

    def aplicar_ecuación(தன், etapa, tipo_ec):
        return super().aplicar_ecuación(etapa=etapa, tipo_ec=tipo_ec)

    def victimiza(தன், víctima, etps_símismo=None, etps_víctima=None, método="presa", etp_sale=None):
        return super().victimiza(víctima=víctima, etps_símismo=etps_símismo, etps_víctima=etps_víctima, método=método,
                                 etp_sale=etp_sale)

    def novictimiza(தன், víctima, etps_símismo=None, etps_víctima=None, método="presa"):
        return super().novictimiza(víctima=víctima, etps_símismo=etps_símismo, etps_víctima=etps_víctima, método=método)

    def especificar_apriori(தன், etapa, ubic_parám, rango, certidumbre, org_inter=None, etp_inter=None, dibujar=False):
        return super().especificar_apriori(etapa=etapa, ubic_parám=ubic_parám, rango=rango, certidumbre=certidumbre,
                                           org_inter=org_inter, etp_inter=etp_inter, dibujar=dibujar)

    def verificar_ecs(தன், ecs, etp):
        return super().verificar_ecs(ecs=ecs, etp=etp)
