import io
import os
import sys
import zipfile
from subprocess import run

import requests

EXE_PYTHON = sys.executable
EXE_PIP = os.path.join(os.path.split(EXE_PYTHON)[0], 'pip')


def instalar_de_zip(nombre, repo):
    run([EXE_PIP, 'install' + 'git+' + repo + '.git@master'])


def instalar_con_pip(nombre, repo):
    url = repo + '/archive/master.zip'
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()


paquetes_github = {
    'ennikkai': 'https://github.com/julienmalard/ennikkai',
    'taqdir': 'https://github.com/julienmalard/taqdir'
}

for nmbr, url in paquetes_github.items():
    instalar_de_zip(nmbr, url)

instalar_con_pip('tikon', 'https://github.com/julienmalard/tikon')
