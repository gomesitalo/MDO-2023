from models import Monoplano
from matplotlib import pyplot
import pandas as pd
import numpy as np
import optimizer
import avl
import os
import random
import pickle
import sys
import shutil

# optimizer.perfis_asa[0] = sys.argv[1]
# optimizer.perfis_eh[0] = sys.argv[2]
# print(optimizer.perfis_asa[0], optimizer.perfis_eh[0])
P_asa = sys.argv[1]
P_eh = sys.argv[2]
print(P_asa, P_eh)

code = P_asa + '-' + P_eh + '-' + str(random.randint(100, 999))
os.mkdir('./avl/configs/'+code+'/')
os.mkdir('./avl/configs/%s/geracao-%d' % (code, 0))

avl.caminho_geometrias = './avl/configs/%s/geracao-%d/' % (code, 0)

media_notas = []
inicial = optimizer.gerar_inicial(50)
media_notas.append(optimizer.mediaAvaliacao(inicial))

candidatos = sorted(inicial, key = lambda a : a.nota, reverse = True)[:optimizer.n_candidatos]
melhor = max(candidatos, key= lambda a : a.nota)
print(melhor.perfil_asa, melhor.perfil_eh, melhor.perfil_ev, "geração 0: %.3f" % (melhor.nota), " | Nota na competição: ", melhor.nota_avaliacao)
print("xcp = %.3f CLmax = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% CP = %.2f pouso = %.2f decolagem = %.2f cma = %.2f arw = %.3f arh = %.3f mtow = %.3f Sst = %.3f" % (melhor.posicoes['cp'][0], melhor.CLmax, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.cp, melhor.x_pouso, melhor.x_decolagem, melhor.CMa *180/3.1416, melhor.ARw, melhor.ARh, melhor.mtow, melhor.Sst))
print("Nome melhor: ", melhor.nome)
print("Média da geração: ", optimizer.mediaAvaliacao(candidatos))
ant = 0
n = 7 # Número de gerações
nota_ant = -1000
notas = []
melhores_geracao = []
name, cauda_ev, cauda_eh = [],[],[] # nome, cauda da ev, cauda da eh  #Modf. em 12/02
gen, nt, Clma, mtow = [],[],[],[] # geração, nota, Clmáx, Mtow  #Modf. em 12/02
sg, land, envg, tipo = [],[],[],[] # dist. de decolagem, dist. de pouso, envergadura, tipo_ev  #Modf. em 12/02
arw, arh, arv, margem = [],[],[],[]


for j in range(n):
    os.mkdir('./avl/configs/%s/geracao-%d' % (code, j+1))
    avl.caminho_geometrias = './avl/configs/%s/geracao-%d/' % (code,j + 1)
    candidatos, atendem_estabilidade = optimizer.reproducao2(candidatos, 0.01)
    melhor = max(candidatos, key= lambda a : a.nota)
    print(melhor.perfil_asa, melhor.perfil_eh, melhor.perfil_ev, "geração %d: %.3f" % (j+1, melhor.nota), " | Nota na competição: ", melhor.nota_avaliacao)
    print("xcp = %.3f CLmax = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% CP = %.2f pouso = %.2f decolagem = %.2f cma = %.2f arw = %.3f arh = %.3f mtow = %.3f Sst = %.3f" % (melhor.posicoes['cp'][0], melhor.CLmax, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.cp, melhor.x_pouso, melhor.x_decolagem, melhor.CMa *180/3.1416, melhor.ARw, melhor.ARh, melhor.mtow, melhor.Sst))
    print("Nome melhor: ", melhor.nome)
    print("Média da geração: ", optimizer.mediaAvaliacao(candidatos))
    media_notas.append(optimizer.mediaAvaliacao(candidatos))
    notas.append(melhor.nota)
    melhores_geracao.append(melhor)
    arq_melhor = open('./avl/configs/%s/geracao-%d-melhor.pyobj' % (code, j + 1), 'wb')
    pickle.dump(melhor, arq_melhor)
    arq_melhor.close()
    avl.criar_arquivo(melhor, False)
    shutil.rmtree('./avl/configs/%s/geracao-%d/' % (code, j + 1))
    if abs(melhor.nota - sum(notas)/10) < 0.5 and len(notas) == 10:
        break
    if len(notas) == 10:
        notas.pop(0)

candidatos.sort(key=lambda a : a.nota, reverse=True)
os.mkdir('./avl/configs/%s/resultado' % code)
avl.caminho_geometrias = './avl/configs/%s/resultado/' % code
i = 1
for melhor in candidatos[:20]:
    print("\n")
    melhor.nome = '%d'%i
    i += 1
    arq_melhor = open('./avl/configs/%s/resultado/%s.pyobj' % (code, melhor.nome), 'wb')
    pickle.dump(melhor, arq_melhor)
    arq_melhor.close()
    print("%s\n  cw = %.3f CL/CD = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% Mtow = %.4f pouso = %.2f decolagem = %.2f perf = %s arw = %.3f arh = %.3f Sst = %.3f " % (melhor.nome, melhor.cw, melhor.CL_CD, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.mtow, melhor.x_pouso, melhor.x_decolagem, melhor.perfil_asa, melhor.ARw, melhor.ARh, melhor.Sst))
    print("perfis asa: ", melhor.geometria_asa)
    print("perfis ev: ", melhor.geometria_ev)
    print("perfis eh: ", melhor.geometria_eh)
    print("Posicoes eh: ", melhor.posicoes["eh"])
    print("Posicoes ev: ", melhor.posicoes["ev"])
    print("Largura: ", melhor.lagura_asa)
    print("Pos eh: ", melhor.pos_eh)
    print("Envergadura: ", melhor.envergadura)
    print("Solo ev: ", melhor.dist_solo_ev)
    avl.criar_arquivo(melhor, False)

melhores_geracao.sort(key=lambda a : a.nota, reverse=True)
os.mkdir('./avl/configs/%s/melhores_geracao' % code)
avl.caminho_geometrias = './avl/configs/%s/melhores_geracao/' % code
i = 1 #Contador do Nº de gerações
gerações = { #Modf. em 12/02
    'Nome':[],
    'Geração':[],
    'Média_geração':[],
    'Clmax':[],
    'MTOW':[],
    'Decolagem':[],
    'Pouso':[],
    'Envergadura':[],
    'Tipo_ev':[],
    'ME':[],
    'Volume EV':[],
    'Volume EH':[],
    'ARh':[],
    'ARv':[],
    'ARw':[],
    'Melhor_nota':[],
}
for melhor in melhores_geracao:
    print("\n")
    name.append(melhor.nome), cauda_eh.append(melhor.VH), cauda_ev.append(melhor.VV) #Modf. em 13/02
    gen.append(i), nt.append(melhor.nota_avaliacao), Clma.append(melhor.CLmax), mtow.append(melhor.mtow) #Modf. em 14/02
    sg.append(melhor.x_decolagem), land.append(melhor.x_pouso), envg.append(melhor.envergadura) #Modf. em 12/02
    margem.append(melhor.ME) #Modf. em 14/02
    arw.append(melhor.ARw), arv.append(melhor.ARv), arh.append(melhor.ARh)
    tipo.append(melhor.tipo_ev) #Modf. em 12/02
    i += 1
    arq_melhor = open('./avl/configs/%s/resultado/%s.pyobj' % (code, melhor.nome), 'wb')
    pickle.dump(melhor, arq_melhor)
    arq_melhor.close()
    print("%s\n  cw = %.3f CL/CD = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% Mtow = %.4f pouso = %.2f decolagem = %.2f perf = %s arw = %.3f arh = %.3f Sst = %.3f " % (melhor.nome, melhor.cw, melhor.CL_CD, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.mtow, melhor.x_pouso, melhor.x_decolagem, melhor.perfil_asa, melhor.ARw, melhor.ARh, melhor.Sst))
    print("perfis asa: ", melhor.geometria_asa)
    print("perfis ev: ", melhor.geometria_ev)
    print("perfis eh: ", melhor.geometria_eh)
    print("Posicoes ev: ", melhor.posicoes["ev"])
    print("Posicoes eh: ", melhor.posicoes["eh"])
    print("Altura: ", melhor.altura)
    print("Largura: ", melhor.lagura_asa)
    print("Pos eh: ", melhor.pos_eh)
    print("Envergadura: ", melhor.envergadura)
    print("Solo ev: ", melhor.dist_solo_ev)
    avl.criar_arquivo(melhor, False)

gerações['Nome'] = name #Modf. em 12/02
gerações['Geração'] = gen
gerações['Média_geração'] = media_notas[1:n+1]
gerações['Clmax'] = Clma = [i for i in reversed(Clma)]
gerações['MTOW'] = mtow = [i for i in reversed(mtow)]
gerações['Decolagem'] = sg = [i for i in reversed(sg)]
gerações['Pouso'] = land = [i for i in reversed(land)]
gerações['Envergadura'] = envg = [i for i in reversed(envg)]
gerações['Tipo_ev'] = tipo = [i for i in reversed(tipo)]
gerações['ME'] = margem = [i for i in reversed(margem)]
gerações['Volume EV'] = cauda_ev = [i for i in reversed(cauda_ev)]
gerações['Volume EH'] = cauda_eh = [i for i in reversed(cauda_eh)]
gerações['ARw'] = arw = [i for i in reversed(arw)]
gerações['ARv'] = arv = [i for i in reversed(arv)]
gerações['ARh'] = arh = [i for i in reversed(arh)]
gerações['Melhor_nota'] = nt = [i for i in reversed(nt)]

print(gerações)
gerações_df = pd.DataFrame(data=gerações) #Modf. em 12/02
print() # Salta uma linha
print(gerações_df) #Modf. em 12/02
gerações_df.to_excel(r'C:\Users\italo\OneDrive\Desktop\Códigos Python, MATLAB, Arduino e VHDL\Códigos Python\MDO 2023\Base de dados\Dados do terminal\Geração_'+code+'.xlsx', index=False)

size = 5.0
x = np.arange(0, len(media_notas), 1)
y = media_notas
pyplot.figure(figsize=(2*size,size))
pyplot.xlabel('Geração', fontsize=16)
pyplot.ylabel('Média de notas', fontsize=16)
pyplot.title(label="Evolução da média de notas")
pyplot.plot(x,y)
pyplot.grid()
pyplot.savefig('Evolução da avaliação.png', format = 'png')