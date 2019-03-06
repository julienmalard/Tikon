import os
import sys
import tempfile
import zipfile
from subprocess import run

print('preparando instalación...')
EXE_PYTHON = sys.executable
EXE_PIP = os.path.join(os.path.split(EXE_PYTHON)[0], 'scripts/pip')

run([EXE_PIP, 'install', 'requests'])
run([EXE_PYTHON, '-m', 'pip', 'install', '--upgrade', 'pip'])
import requests


def instalar_con_pip(nombre, repo):
    print('instalando ' + nombre)
    run([EXE_PIP, 'install', 'git+' + repo + '.git@master'])


def instalar_de_zip(nombre, repo):
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
    'taqdir': 'https://github.com/julienmalard/taqdir'
}

for nmbr, url in paquetes_github.items():
    instalar_de_zip(nmbr, url)

instalar_con_pip('tikon', 'https://github.com/julienmalard/tikon')

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
