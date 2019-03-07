import sys
import tempfile
import zipfile
from subprocess import run
import os

from pip._internal import main as pipmain

print('preparando instalación...')
EXE_PYTHON = sys.executable

pipmain(['install', 'requests'])
run([EXE_PYTHON, '-m', 'pip', 'install', '--upgrade', 'pip'])
import requests


def instalar_de_zip(nombre, repo, reqs='requísitos.txt'):
    print('instalando ' + nombre)
    url = repo + '/archive/master.zip'
    r = requests.get(url)
    arch_temp = tempfile.mktemp()
    dir_temp = tempfile.mkdtemp()
    with open(arch_temp, 'wb') as f:
        f.write(r.content)
    z = zipfile.ZipFile(arch_temp)
    z.extractall(dir_temp)
    run([EXE_PYTHON, 'setup.py', 'install'], cwd=os.path.join(dir_temp, nombre + '-master'))


paquetes_github = {
    'ennikkai': 'https://github.com/julienmalard/ennikkai',
    'taqdir': 'https://github.com/julienmalard/taqdir',
    'tikon': 'https://github.com/julienmalard/tikon'
}

for nmbr, url in paquetes_github.items():
    instalar_de_zip(nmbr, url)

print('verificando instalación...')
import os

from tikon.ejemplos.prb import red, exper_A
from tikon.estruc.simulador import Simulador
from tikon.ejemplos import en_ejemplos

simul = Simulador(red)

red.cargar_calib(en_ejemplos('calibs Sitio A/red'))
exper_A.cargar_calib(en_ejemplos('calibs Sitio A'))

res = simul.simular(exper=exper_A, n_rep_estoc=15, n_rep_parám=15, vars_interés=True)
print('¡Instalación exitosa!')
