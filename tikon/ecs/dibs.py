import seaborn as sns


def dibujar_dist(dist, nombre, ejes=None, argsll=None):
    args_base = dict(
        color='#99CC00', cut=0, shade=True
    )
    if argsll:
        args_base.update(argsll)

    puntos = dist.obt_vals(10000)

    return sns.kdeplot(puntos, ax=ejes, **args_base).set_title(nombre)
