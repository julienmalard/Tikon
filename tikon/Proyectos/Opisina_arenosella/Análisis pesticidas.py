from tikon.NuevaParcela import Parcela
from tikon.Cultivo.NuevoCultivo import Cultivo
from tikon.RAE.RedAE import Red
from tikon.Manejo.Aplicación import Insecticida


red_cocos = Red(nombre='Campos coco sencillo', proyecto='Opisina_arenosella')
cocos = Cultivo('Coco')

parc = Parcela(nombre='Control', cultivo=cocos, red=red_cocos)

insecticida = Insecticida('90%')
insecticida.estab_mortalidad(.90)

parc.aplicar(insecticida, día=[25, 50])
parc.simular()

parc.limpiar_aplicaciones()

específico = Insecticida('Específico')
específico.estab_mortalidd('Plagas', 0.90)

parc.aplicar(específico, día=[25, 50])
parc.simular()

parc.limpiar_especificados()
parc.aplicar_auto(insecticida, plaga='O. arenosella', densidad=20000)
parc.simular()

parc.limpiar_aplicaciones()
parc.aplicar_auto(específico, plaga='O. arenosella', densidad=20000)
parc.simular()
