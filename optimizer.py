import random
from models import Monoplano
from avl import criar_arquivo
from operator import attrgetter
from classe_desempenho import desempenho
# from random import *

n_selecionados = 500 # reprodução 1
n_filhos = 30
n_candidatos = 40

c_min_w = 0.2
c_max_w = 0.6

b_min_h = 0.1
c_min_h = 0.1
b_max_h = 2
c_max_h = 0.4
ht_max = 0.6

b_min_v = 0.1
c_min_v = 0.1
b_max_v = 0.5
c_max_v = 0.4

lambda_min_v = 0.4
lambda_max_v = 0.95

pos_cp_min = 0.2
pos_cp_max = 0.35

iw_max = 7
ih_max = -7


offset_max = 0.15
n_sect = 3
# dist_nariz = 0.295 
# soma_dims = 3.2 - dist_nariz

altura_max = 0.6
b_min_w = 1.5 #envergadura min
b_max_w = 2.3 #envergadura max
dist_solo_ev_min = 0.15

perfis_asa = ['Asa_1', 'Asa_2', 'Asa_3', 'Asa_4']
perfis_eh = ['EH_1', 'EH_2', 'EH_3']
perfis_ev = ['EV_1', 'EV_2', 'EV_3']

# gera aleatpriamente, entre os extremos máximos e minimos os valores dos parâmetros da aeronave
def gerar_inicial(total):
    aeronaves = []
    contador = 0
    while len(aeronaves) < total:
        #print("ok1")
        o1 = random.uniform(0, offset_max)
        #o2 = random.uniform(o1,offset_max)
        cr = random.uniform(c_min_w, c_max_w)
        #cint = random.uniform(c_min_w, cr - o1)
        ct = random.uniform(c_min_w, cr - o1)
        br = random.uniform((b_min_w/2), (b_max_w/2) - 0.1)
        bt = random.uniform(0.1, b_max_w/2 - br)
        b = br + bt
        #bint = random.uniform(((b - br)*0.3) + br, ((b - br)*0.7) + br)
        
        geometria_asa = [(0, cr, 0), (br, cr, 0), (b, ct, o1)] #(bint, cint, o1),

        bh = random.uniform(b_min_h/2, b_max_h/2)
        ch = random.uniform(c_min_h, c_max_h)

        geometria_eh = [(0, ch, 0), (bh, ch, 0)]

        crv = random.uniform(ch, c_max_v)
        lambda_v = random.uniform(lambda_min_v, lambda_max_v)
        ctv = lambda_v*crv
        bv = random.uniform(b_min_v, bh)

        geometria_ev = [(0, crv, 0), (bv, ctv, crv-ctv)]

        iw = round(random.uniform(0, iw_max))
        ih = round(random.uniform(ih_max, 0))

        ht = random.uniform(0, ht_max)
        lt = random.uniform(cr, 1.5 - ch)

        pos_cp = round(random.uniform(pos_cp_min, pos_cp_max)*cr, 2)

        posicoes = {'asa': (0, 0), 'eh': (lt, ht),
                    'ev': (lt, ht), 'cp': (pos_cp, 0)}
        perfil_asa = random.choice(perfis_asa)
        perfil_eh = random.choice(perfis_eh)
        perfil_ev = random.choice(perfis_ev)
        try:
            aeronave = Monoplano(geometria_asa, perfil_asa, iw, geometria_eh, perfil_eh, ih, geometria_ev, perfil_ev, posicoes)
            if verifica_cond(aeronave):
                contador += 1
                #print(contador)
                aeronaves.append(aeronave)
        except Exception as e:
            #print(e)
            continue
    return aeronaves


def variar(aeronave, sigma):  # função para variar os paramestros de uma aeronave
    while True:
        #print("Variar")
        geometria_asa = aeronave.geometria_asa.copy()
        geometria_eh = aeronave.geometria_eh.copy()
        geometria_ev = aeronave.geometria_ev.copy()

        br, cr, o1x = geometria_asa[1]
        b, ct, o1y = geometria_asa[2]
        bt = b - br

        ch, bh = geometria_eh[0][1], geometria_eh[1][0]
        crv, ctv, bv = ch, geometria_ev[1][1], geometria_ev[1][0]
        pos_cp = aeronave.posicoes['cp'][0]

        o1 = round(trunc_gauss(o1y, sigma, 0, offset_max), 3)
        #o2 = round(trunc_gauss(o2y, sigma, o1, offset_max), 3)
        cr = round(trunc_gauss(cr, sigma, c_min_w, c_max_w), 3)
        ct = round(trunc_gauss(ct, sigma, c_min_w, cr - o1), 3)
        #cint = round(trunc_gauss(cint, sigma, c_min_w, cr - o1), 3)
        br = round(trunc_gauss(br, sigma, (b_min_w/2), (b_max_w/2) - 0.1), 3)
        bt = round(trunc_gauss(bt, sigma, 0.1, b_max_w/2 - bt), 3)
        b = round(bt + br, 3) 
        b = round(trunc_gauss(b, sigma, 0.1, 1.15), 3)

        ch = round(trunc_gauss(ch, sigma, c_min_h, c_max_h), 3)
        bh = round(trunc_gauss(bh, sigma, b_min_h/2, b_max_h/2), 3)

        #bint = round(trunc_gauss(bint, sigma,((b - br)*0.3) + br, ((b - br)*0.7) + br), 3)

        lambda_v = ctv/crv
        lambda_v = trunc_gauss(lambda_v, sigma, lambda_min_v, lambda_max_v)
        crv = round(trunc_gauss(crv, sigma, ch, c_max_v), 3)
        ctv = round(lambda_v*crv, 3)
        bv = round(trunc_gauss(bv, sigma, b_min_h, bh), 3)

        iw = round(trunc_gauss(aeronave.iw, sigma*50, 0, iw_max))
        ih = round(trunc_gauss(aeronave.ih, sigma*50, ih_max, 0))

        ht = round(aeronave.posicoes['eh'][1], 3)
        ht = round(trunc_gauss(ht, sigma, 0, cr), 3)

        lt = round(aeronave.posicoes['eh'][0], 3)
        lt = round(trunc_gauss(lt, sigma, cr, 1.5 - ch), 3)

        pos_cp = round(trunc_gauss(pos_cp, sigma, pos_cp_min*cr, pos_cp_max*cr), 3)

        geometria_asa = [(0, cr, 0), (br, cr, 0), (b, ct, o1)] #(bint, cint, o1),
        geometria_eh = [(0, ch, 0), (bh, ch, 0)]
        geometria_ev = [(0, crv, 0), (bv, ctv, crv-ctv)]

        posicoes = {'asa': (0, 0), 'eh': (lt, ht),
                    'ev': (lt, ht), 'cp': (pos_cp, 0)}
        try:
            aeronave_1 = Monoplano(geometria_asa, aeronave.perfil_asa, iw, geometria_eh, aeronave.perfil_eh, ih, geometria_ev, aeronave.perfil_ev, posicoes)
            if verifica_cond(aeronave_1):
                #print("ok1")
                aeronave = aeronave_1
                break
        except Exception as e:
            #print(e)
            continue
    return aeronave


def gerarFilho(pai, mae, sigma, indiceMutacao):
    variar = 0
    while True:
        #print("GerarF")
        geometria_asaPai = pai.geometria_asa.copy()
        geometria_ehPai = pai.geometria_eh.copy()
        geometria_evPai = pai.geometria_ev.copy()
        geometria_asaMae = mae.geometria_asa.copy()
        geometria_ehMae = mae.geometria_eh.copy()
        geometria_evMae = mae.geometria_ev.copy()
        posicoes_Mae = mae.posicoes.copy()

        try: 
            aeronave = Monoplano(geometria_asaPai, pai.perfil_asa, mae.iw, geometria_ehMae, mae.perfil_eh, pai.ih, geometria_evPai, pai.perfil_ev, posicoes_Mae)
            if indiceMutacao > random.random():
                aeronave = variar(aeronave, sigma)
            #print("Retorno por reprodução")
            return aeronave
        except:
            variar += 1
            if variar >= 4:
                #print("Certo")
                return pai
            else:
                continue

def reproducao(gerados, sigma):  # função de reprodução recebe aeronaves
    pais = sorted(gerados, key=lambda a: a.nota, reverse=True)[:n_selecionados]
    filhos = []
    for pai in pais:
        for i in range(int(len(gerados)/len(pais)) - 1):
            filhos.append(variar(pai, sigma))
        filhos.append(pai)
    return filhos

def trunc_gauss(mu, sigma, bottom, top):
    a = random.gauss(mu, sigma)
    if a >= top:
        return top
    if a <= bottom:
        return bottom
    return a

def mediaAvaliacao(aeronaves):
    media = 0
    for aeronave in aeronaves:
        media += aeronave.nota_avaliacao
    return (media/(len(aeronaves)))

def sortear(pais, indice_a_ignorar = -1):
    sigma = len(pais)/50
    continua = True
    while continua:
        indice_sorteado = int(random.gauss(0, sigma))
        if indice_sorteado < 0: indice_sorteado = 0
        elif indice_sorteado > len(pais)-1: indice_sorteado = len(pais)-1
        if indice_sorteado != indice_a_ignorar:
            continua = False
    return indice_sorteado

def selecaoRoleta(pais):
    #ordenados = sorted(pais,  key=attrgetter('nota'), reverse=True)
    indice_pai = sortear(pais)
    indice_mae = sortear(pais, indice_pai)
    pai = pais[indice_pai]
    mae = pais[indice_mae]
    return pai, mae

def reproducao2(populacao, sigma, mutacao = 0.4):
    #candidatos = sorted(populacao, key = lambda a : a.nota_avaliacao, reverse = True)[:int(n_filhos/2)]
    ordenados = sorted(populacao,  key=attrgetter('nota'), reverse=True)
    atendem_estabilidade = []
    filhos = []
    contador = 0
    while len(filhos) < int(n_filhos/2):
        pai, mae = selecaoRoleta(ordenados)
        filho = gerarFilho(pai, mae, sigma, mutacao)
        if verifica_cond(filho): 
            filhos.append(filho)
            if verifica_cond_est(filho): 
                atendem_estabilidade.append(filho)
    while len(filhos) < n_filhos:
        filho = variar(ordenados[contador], sigma)
        if verifica_cond(filho): 
            filhos.append(filho)
            #print("Contaodor reprodução: ", contador)
            if verifica_cond_est(filho): 
                atendem_estabilidade.append(filho)
        contador += 1
    return filhos, atendem_estabilidade

def verifica_cond(aeronave):
    retorno = True
    if aeronave.altura > altura_max:
        retorno = False
    if aeronave.envergadura > b_max_w:
        retorno = False
    if aeronave.dist_solo_ev < dist_solo_ev_min:
        retorno = False
    return retorno

def verifica_cond_est(aeronave):
    retorno = False
    if aeronave.ME >= 0.05 and aeronave.ME <= 0.15: 
        if aeronave.atrim >= 3 and aeronave.atrim <= 12:
            if aeronave.Sst >= 1:
                retorno = True 
    return retorno