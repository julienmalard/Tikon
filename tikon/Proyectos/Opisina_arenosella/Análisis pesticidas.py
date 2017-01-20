from tikon.NuevaParcela import Parcela
from tikon.Cultivo.NuevoCultivo import Cultivo
from tikon.RAE.RedAE import Red

red_cocos = Red(nombre='Campos coco sencillo', proyecto='Opisina_arenosella')
cocos = Cultivo('Coco')

parc = Parcela(nombre='Control', cultivo=cocos, red=red_cocos)
parc.simular()