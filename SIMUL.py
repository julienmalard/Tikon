# import CULTIVO as mod_cultivo
# import PLAGAS as mod_plagas

import CULTIVO, PLAGAS

def predecir(mod_cultivo, mod_plagas, paso):
    plagas = PLAGAS.mod_plagas.incr(paso)
    cultivo = CULTIVO.mod_cultivos.incr(paso)



##f = file('obj.save', 'wb')
##cPickle.dump(my_obj, f, -1)
##f.close()
##
##f = file('objects.save', 'wb')
##for obj in [obj1, obj2, obj3]:
##    cPickle.dump(obj, f, protocol=cPickle.HIGHEST_PROTOCOL)
##f.close()
##
##
##f = file('objects.save', 'rb')
##loaded_objects = []
##for i in range(3):
##    loaded_objects.append(cPickle.load(f))
##f.close()
##
##import CPickle
##
##
##def __getstate__(self):
##    return (self.W, self.b)
##
##def __setstate__(self, state):
##    W, b = state
##    self.W = W
##    self.b = b
##
##
########
##
##class Fruits: pass
##
##banana = Fruits()
##
##banana.color = 'yellow'
##banana.value = 30
##
##import pickle
##
##with open("Fruits.obj","wb") as i:
##    pickle.dump(banana,i)
##
##with open("Fruits.obj",'rb') as file:
##    object_file = pickle.load(file)
##
##print(object_file.color, object_file.value, sep=', ')
### yellow, 30
##
