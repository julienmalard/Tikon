import os

CURRENT_DIR = os.path.dirname(__file__)
file_path = os.path.join(CURRENT_DIR, 'test.txt')
f=open(file_path,'w')
f.write('testing the script')
f.close()

print (__file__)


carpeta = __file__
print (carpeta)

import fibon
