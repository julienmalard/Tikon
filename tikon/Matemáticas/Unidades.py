

class Unidad(object):
    """

    """

    def __init__(símismo, texto):
        """

        :param texto:
        :type texto: str
        """

        símismo.unidades = {}

        unidades = símismo.texto_a_unidades(texto)

        símismo.agregar(símismo.unidades, unidades)

    def __mul__(símismo, otro):
        """

        :param otro:
        :type otro: str | Unidad
        :return:
        """

        if type(otro) is str:
            dic_unid = símismo.texto_a_unidades(texto=otro)
        elif type(otro) is Unidad:
            dic_unid = otro.unidades
        else:
            raise TypeError

        símismo.agregar(símismo.unidades, dic_unid)

        return símismo

    def __str__(símismo):

        texto = ''
        for u, e in sorted(símismo.unidades.items()):
            texto += u + str(e)

        return texto

    def __truediv__(símismo, otro):
        pass

    @staticmethod
    def agregar(dic_orig, dic_nuevo):
        """

        :param dic_nuevo:
        :type dic_nuevo: dict

        """

        for u in dic_nuevo:
            if u not in dic_orig:
                dic_orig[u] = 0

            dic_orig[u] += dic_nuevo[u]

    @staticmethod
    def texto_a_unidades(texto):
        """

        :param texto:
        :type texto: str

        :return:
        :rtype: dict
        """

        dic_final = {}
        l_dic = [dic_final]

        paréntesis = 0
        unid = ''
        exp = '0'
        fase = 'u'

        def agregar_unid(d):
            if unid not in d:
                d[unid] = 0
            d[unid] += int(exp)

        def mult(d, x):
            for u in d:
                d[u] *= x

        for n, i in enumerate(texto):

            if i.isalpha():
                if fase == 'e':
                    agregar_unid(l_dic[-1])
                    unid = ''
                    exp = ''
                elif fase == 'p':
                    mult(l_dic[-1], str(exp))
                    exp = '0'
                unid += i
                fase = 'u'

            elif i.isnumeric() or i == '-' or i == '.':
                fase = 'e'
                exp += i

            elif i == '(':
                paréntesis += 1
                l_dic.append({})

            elif i == ')':
                paréntesis -= 1
                fase = 'p'
                unid = exp = '0'

                if paréntesis < 0:
                    raise ValueError

            if n == len(texto):
                if fase == 'e':
                    agregar_unid(l_dic[-1])
                elif fase == 'p':
                    raise NotImplementedError

                if paréntesis > 0:
                    raise ValueError

        return dic_final


if __name__ == '__main__':
    a = Unidad('m3s-1')
    print('a:', a)
    b = 's2'
    print('a*b:', a*b)
