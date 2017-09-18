from pprint import pprint
import numpy as np
import csv

from tikon.Proyectos.Opisina_arenosella.Red_Opisina import Red_coco
from tikon.Proyectos.Opisina_arenosella.a_prioris import a_prioris
from tikon.Matemáticas.Experimentos import Experimento

dib_aprioris = False
dib_valid_perf = True
proyecto = 'Artificial'


# Funciones útiles
def _aplicar_a_prioris(red, d_a_pr):
    for org in red.organismos.values():
        try:
            for a_priori in d_a_pr[org.nombre]:
                a_priori['certidumbre'] = 1  # Usamos los a prioris especificados como límites teoréticos.
                org.especificar_apriori(dibujar=dib_aprioris, **a_priori)
        except KeyError:
            pass


def _sacar_vals_paráms(red):

    dic_egr = {}

    etps_interés = [i for i in range(len(red.etapas)) if all(i not in f.values() for f in red.fantasmas.values())]

    for n_etp in etps_interés:

        d_etp = red.etapas[n_etp]
        etp = d_etp['nombre']
        org = d_etp['org']

        if org not in dic_egr:
            dic_egr[org] = []

        d_val = {'etapa': etp, 'ubic_parám': None, 'val': None, }
        for categ, d_categ in red.coefs_act_númzds.items():
            for s_categ, d_s_categ in d_categ.items():
                for tipo_ec, d_t_ec in d_s_categ.items():
                    for parám, val_p in d_t_ec.items():

                        d_val_fin = d_val.copy()
                        d_val_fin['ubic_parám'] = [categ, s_categ, tipo_ec, parám]

                        try:
                            n_rel_etp = red.ecs[categ][s_categ][tipo_ec].index(n_etp)
                        except ValueError:
                            if n_etp in red.parasitoides['juvs']:
                                if categ == 'Transiciones' and \
                                                tipo_ec == red.etapas[n_etp]['dic']['ecs']['Transiciones'][s_categ]:
                                    n_ad_parás = red.parasitoides['juvs'][n_etp]
                                    n_etp_fant = red.parasitoides['adultos'][n_ad_parás]['n_fants'][-1]
                                    n_rel_etp = red.ecs[categ][s_categ][tipo_ec].index(n_etp_fant)
                                    d_val_fin['val'] = val_p[0, n_rel_etp]
                                    dic_egr[org].append(d_val_fin)
                                continue

                            else:
                                continue

                        if len(val_p.shape) == 2:  # Si no hay interacciones...
                            d_val_fin['val'] = val_p[0, n_rel_etp]
                            dic_egr[org].append(d_val_fin)
                        else:
                            for i in range(val_p.shape[2]):
                                val = val_p[0, n_rel_etp, i]
                                if not np.isnan(val):
                                    d_val_inter = d_val_fin.copy()
                                    d_val_inter['org_inter'] = red.etapas[i]['org']
                                    d_val_inter['etp_inter'] = red.etapas[i]['nombre']
                                    d_val_inter['val'] = val
                                    dic_egr[org].append(d_val_inter)
    return dic_egr


def _gen_a_prioris(vals, prec):
    d_a_pr = {}
    for org, l_a_pr in vals.items():

        if org not in a_prioris:
            continue

        if org not in d_a_pr:
            d_a_pr[org] = []

        for d_v in l_a_pr:
            dic = d_v.copy()
            etp = dic['etapa']
            u_p = dic['ubic_parám']

            a_pr_orgnl = next((d_a for d_a in a_prioris[org] if d_a['etapa'] == etp and d_a['ubic_parám'] == u_p), None)
            if a_pr_orgnl is None:
                continue
            rango = a_pr_orgnl['rango']
            dim_rango = rango[1] - rango[0]

            val = dic.pop('val')
            dic['rango'] = (max(rango[0], val - dim_rango * (100 - prec) / 100),
                            min(rango[1], val + dim_rango * (100 - prec) / 100))
            dic['certidumbre'] = 1

            d_a_pr[org].append(dic)

    return d_a_pr


def _simul_a_exp(red):

    preds = red.predics['Pobs']

    etps_interés = [i for i, _ in enumerate(red.etapas) if all(i not in f.values() for f in red.fantasmas.values())]

    archivo = 'temp.csv'

    with open(archivo, 'w', newline='') as arch_csv:
        escritorcsv = csv.writer(arch_csv)
        escritorcsv.writerow(['Día'] + ['Etapa %i' % i for i in range(len(etps_interés))])
        for día in range(preds.shape[-1]):
            l_vals = [día] + list(preds[0, 0, 0, etps_interés, día])
            escritorcsv.writerow(l_vals)

    exper = Experimento(nombre='Simulado', proyecto=proyecto)
    exper.agregar_orgs(archivo=archivo, col_tiempo='Día')

    return exper


def _agregar_exp(red, exper):
    etps_interés = [i for i in range(len(red.etapas)) if all(i not in f.values() for f in red.fantasmas.values())]

    corresp = {}
    for etp in etps_interés:
        org = red.etapas[etp]['org']
        nombre = red.etapas[etp]['nombre']

        if org not in corresp:
            corresp[org] = {}

        corresp[org][nombre] = ['Etapa %i' % etp]

    red.añadir_exp(exper, corresp=corresp)


# Aplicar a prioris
_aplicar_a_prioris(red=Red_coco, d_a_pr=a_prioris)
Coco = Red_coco.organismos['Coco']
Coco.estimar_densidad(rango=(38000e6, 42000e6), certidumbre=0.95)

# Por el momento, tenemos que conectar con un experimento aunque no lo usemos. Para hacer: Esto tendrá que cambiar
Exper = Experimento(nombre='Sitio A', proyecto=Red_coco.proyecto)
Exper.agregar_orgs(archivo='Oarenosella_A.csv', col_tiempo='Día', factor=655757.1429 / 500)
Red_coco.añadir_exp(Exper, corresp={'O. arenosella': {'juvenil_1': ['Estado 1'],
                                                      'juvenil_2': ['Estado 2'],
                                                      'juvenil_3': ['Estado 3'],
                                                      'juvenil_4': ['Estado 4'],
                                                      'juvenil_5': ['Estado 5'],
                                                      'pupa': ['Pupa']},
                                    'Parasitoide larvas': {'juvenil': ['Para_larva_abs']},
                                    'Parasitoide pupas': {'juvenil': ['Para_pupa_abs']}})

# Generar una simulación con UNA repetición paramétrica (y estocástica)
Red_coco.simular(exper=Exper, nombre='Datos artificiales', n_rep_parám=1, n_rep_estoc=1,
                 mostrar=False, detalles=False, usar_especificadas=True)

# Extraer las predicciones de la simulación y copiarlas a un nuevo Experimento
Exper_artificial = _simul_a_exp(Red_coco)

# Extraer los valores "verdaderos" de los parámetros
vals_paráms = _sacar_vals_paráms(red=Red_coco)
a_pr_verd = _gen_a_prioris(vals=vals_paráms, prec=100)

# Aplicar a prioris restringidos basados en los valores aplicados para la simulación
_aplicar_a_prioris(red=Red_coco, d_a_pr=a_pr_verd)

# Validar con estos valores
_agregar_exp(red=Red_coco, exper=Exper_artificial)
valid_perfecta = Red_coco.validar(nombre='Valid con verdaderos', exper=Exper_artificial, usar_especificadas=True,
                                  detalles=False, dibujar=dib_valid_perf)
print('Validación Perfecta\n********************')
pprint(valid_perfecta)


# Intentar calibrar, y validar, con rangos de menos en menos restringidos
for p in range(100, 0, -10):
    a_pr = _gen_a_prioris(vals=vals_paráms, prec=p)
    _aplicar_a_prioris(red=Red_coco, d_a_pr=a_pr)
    Red_coco.calibrar(nombre='Calib con prec. {}'.format(p), exper=Exper_artificial,
                      quema=0, n_iter=5, dibujar=True)
    Red_coco.guardar_calib(descrip='Calib con datos artificiales, precisión de {}'.format(p),
                           utilizador='Julien Malard', contacto='julien.malard@mail.mcgill.ca')
    valid = Red_coco.validar(nombre='Valid con calib prec. {}'.format(p), exper=Exper_artificial,
                             usar_especificadas=True, detalles=False, guardar=True)

    print('Resultados de validación después de calib con precisión de {}%:\n============='.format(p))
    pprint(valid)
