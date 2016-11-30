# Un documento con todas las distribuciones a prioris necesarias para el modelo de O. arenosella

a_prioris = {

    'O. arenosella_senc': [dict(etapa='adulto',
                                ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                                # Huevos por adulto / días de vida
                                rango=((152-26*1.96)/(53.1+.2*1.96), (152+26*1.96)/(53.1-.2*1.96)),
                                certidumbre=.95),
                           dict(etapa='adulto',
                                ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                                org_inter=Coco, etp_inter='planta',
                                rango=(1/(1823e-6+(100e-6*1.96)), 1/(1823e-6-(100e-6*1.96))),
                                certidumbre=.95),
                           dict(etapa='adulto',
                                ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                                org_inter=Coco, etp_inter='planta',
                                rango=(1823e-6+(100e-6*1.96), 1823e-6-(100e-6*1.96)),
                                certidumbre=.95,),
                           dict(etapa='adulto',
                                ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                                org_inter=Coco, etp_inter='planta',
                                rango=((1823e-6-(100e-6*1.96))**2, (1823e-6+(100e-6*1.96))**2),
                                certidumbre=.95)  # Para hacer
                           ],

    'Parasitoide_senc': [dict(etapa='adulto',
                              ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                              rango=(6/15, 164/9),
                              certidumbre=0.95),
                         dict(etapa='adulto',
                              ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                              org_inter=O_arenosella_senc, etp_inter='adulto',
                              rango=(1, 10),
                              certidumbre=0.95),
                         dict(etapa='adulto',
                              ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                              org_inter=O_arenosella_senc, etp_inter='adulto',
                              rango=(20, 164),
                              certidumbre=.95),
                         dict(etapa='adulto',
                              ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                              org_inter=O_arenosella_senc, etp_inter='adulto',
                              rango=(20 ** 2, 164 ** 2),
                              certidumbre=.95),  # para hacer

                         ],

    'O. arenosella': [dict(etapa='huevo',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_1',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_1',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_1',
                           ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_1',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_1',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_2',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_2',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_2',
                           ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_2',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
                           rango=(),
                           certidumbre=0.95,
                           ),
                      dict(etapa='juvenil_2',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_3',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_3',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_3',
                           ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_3',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_3',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_4',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_4',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_4',
                           ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_4',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_4',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_5',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_5',
                           ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_5',
                           ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_5',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
                           rango=(),
                           certidumbre=0.95),
                      dict(etapa='juvenil_5',
                           ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
                           rango=(),
                           certidumbre=0.95)
                      ]

}
