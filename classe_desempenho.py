# Classe de Desempenho do MDO 2023

import math as m
from classe_curvas import curvas

class desempenho:

    def __init__(self, g, mu, K, Clmax, Cdmin, hw, bw, Sw, rho, prop):
        self.g = g
        self.mu = mu
        self.K = K
        self.Clmax = Clmax
        self.Cdmin = Cdmin
        self.hw = hw
        self.bw = bw
        self.Sw = Sw
        self.rho = rho
        self.prop = prop
        self.Mtow = desempenho.mtow(self)
        self.W = self.Mtow*self.g
        pass

    def vel_estol(self): # Velocidade na qual a aeronave entra em 'stall'
        return m.sqrt((2*(self.W))/(self.rho*self.Sw*self.Clmax))
        
    def vel_liftoff(self): # Velocidade estimada para decolagem "Vlof" (ANDERSON, 2015)
        return 1.2*desempenho.vel_estol(self)

    def vel_liftoff_070(self): # Velocidade ideal estimada para a subida "Vlof/raiz(2)"
        return (desempenho.vel_liftoff(self))/m.sqrt(2)

    def vel_aprroch(self): # Velocidade com que a aeronave se aproxima da pista de pouso (FAR Part-23)
        return 1.3*desempenho.vel_estol(self)

    def vel_landing(self): # Velocidade ideal estimada durante o pouso "Vappr/raiz(2)"
        return (desempenho.vel_aprroch(self)/m.sqrt(2))

    def vel_max_alcance(self): # Velocidade de máximo alcance, tração mínima requerida ou de máxima eficiência aerodinâmica
        return ((2*(self.W)/(self.rho*self.Sw))**0.5)*(((self.K)/self.Cdmin)**0.25)

    def vel_max_autonomia(self): # Velocidade de máxima autonomia ou de potência requerida mínima 
        return ((2*(self.W)/(self.rho*self.Sw))**0.5)*(((self.K)/(3*self.Cdmin))**0.25)

    def Cl_ideal(self):
        efeito_solo = ((16*self.hw/self.bw)**2)/((1+(16*self.hw/self.bw)**2)) # Efeito solo durante a decolagem e o pouso
        return self.mu/(2*efeito_solo*self.K)

    def Cd_ideal(self):
        efeito_solo = ((16*self.hw/self.bw)**2)/((1+(16*self.hw/self.bw)**2)) # Efeito solo durante a decolagem e o pouso
        return self.Cdmin + efeito_solo*self.K*(desempenho.Cl_ideal(self)**2)

    def ponto_projeto(self):
        Cl_asterix = m.sqrt(abs(self.Cdmin)/self.K) # Coef. de sustentação que maximiza a eficiência aerodinâmica - ou o alcance, (Cl*)
        #Cl_asterix =  m.sqrt((3*self.Cdmin)/self.K) # Coef. de sustentação que permite planeio com máxima autonomia (Cl*)
        #Cd_asterix = self.Cdmin + self.K*Cl_asterix**2 # Coef. de arrasto para o ponto de projeto - equivale ao "(2*self.Cdmin)"
        E_max = Cl_asterix/(2*self.Cdmin) # Eficiência aerodinâmica máxima, também escrita como (L/D)max
        return E_max

    def decolagem(self):
        T_Vlof_r2 = curvas.tracao(self, desempenho.vel_liftoff_070(self)) # Tração estimada na velocidade da norma aeronáutica
        D_Vlof_r2 = 0.5*self.rho*((desempenho.vel_liftoff_070(self))**2)*self.Sw*desempenho.Cd_ideal(self)
        L_Vlof_r2 = 0.5*self.rho*((desempenho.vel_liftoff_070(self))**2)*self.Sw*desempenho.Cl_ideal(self)
        ac_media = (1/self.Mtow)*(T_Vlof_r2-D_Vlof_r2-self.mu*((self.W)-L_Vlof_r2))
        Sg = (1.44*(self.W)**2)/(self.g*self.rho*self.Sw*self.Clmax*(T_Vlof_r2-D_Vlof_r2-self.mu*((self.W)-L_Vlof_r2)))
        t_Sg = m.sqrt(2*Sg/ac_media)
        return ac_media, Sg, t_Sg

    def subida(self, V):
        v = 0.01
        rate_climb = [] # Cria uma lista que irá conter a razão de subida em cada velocidade de V = 0 até V = 40 m/s
        while v <= 40:
            rate_climb.append(curvas.razao_subida(self, v)) # Guarda os valores de R/C em rate_climb
            v += 0.01 # Diferencial que funciona como contador
        max_rate_c = max(rate_climb) # Pega a maior razão de subida (R/C_max) em m/s
        vel_h = (rate_climb.index(max_rate_c)+1)*0.01 # Pega a velocidade durante R/C_max - Pegamos index + 1, pois o index_inical = 0
        max_ang_subida = m.asin(max_rate_c/vel_h)*(180/m.pi) # Calcula o ângulo de subida para o R/C_max em graus
        rate_c = curvas.razao_subida(self, V) # Calcula a razão de subida  para um dado 'V' em m/s
        ang_subida = m.asin(curvas.razao_subida(self, V)/V)*(180/m.pi) # Calcula o ângulo de subida para um dado 'V' em graus
        return max_rate_c, vel_h, max_ang_subida, rate_c, ang_subida

    #def cruzeiro():

    def pouso(self):
        D_Vland = 0.5*self.rho*((desempenho.vel_landing(self))**2)*self.Sw*desempenho.Cd_ideal(self)
        L_Vland = 0.5*self.rho*((desempenho.vel_landing(self))**2)*self.Sw*desempenho.Cl_ideal(self)
        Sland_FAR = (1.69*(self.W)**2)/(self.g*self.rho*self.Sw*self.Clmax*(D_Vland+self.mu*((self.W)-L_Vland)))
        D_Vstall = 0.5*self.rho*((desempenho.vel_estol(self)/m.sqrt(2))**2)*self.Sw*desempenho.Cd_ideal(self)
        L_Vstall = 0.5*self.rho*((desempenho.vel_estol(self)/m.sqrt(2))**2)*self.Sw*desempenho.Cl_ideal(self)
        Sland_real = ((self.W)**2)/(self.g*self.rho*self.Sw*self.Clmax*(D_Vstall+self.mu*((self.W)-L_Vstall)))
        ang_planeio = m.atan(1/desempenho.ponto_projeto(self))*(180/m.pi) # Calcula o ângulo de planeio para (L/D)max em graus
        vel_planeio = m.sqrt((2*self.W*m.cos(ang_planeio*m.pi/180))/(self.rho*self.Sw*desempenho.Cl_ideal(self)))
        return Sland_FAR, Sland_real, ang_planeio, vel_planeio

    #def envelope_de_voo():

    def mtow(self):
        rho = 1 # parâmetro de densidade que auxiliará a percorrer a lista
        Carga_util = [] # lista vazia para receber os valores de Sg, W e rho
        while rho <= 3:
            mtow = 10.0 # Mtow inicial
            if rho == 1: rho = 1.225 # Troca o valor de rho = 1 para rho = 1.225 kg/m³
            elif rho == 2: rho = 1.156 # Troca o valor de rho = 2 para rho = 1.156 kg/m³
            else: rho = 1.090 # Troca o valor de rho = 3 para rho = 1.090 kg/m³
            while mtow <= 20:
                W = mtow*self.g
                T_Vlof_r2 = curvas.tracao(self, (1.2*(m.sqrt((2*W)/(rho*self.Sw*self.Clmax))))/m.sqrt(2), rho) # Instâncias, 'Vlof/sqrt(2)', *args
                D_Vlof_r2 = 0.5*rho*(((1.2*(m.sqrt((2*W)/(rho*self.Sw*self.Clmax))))/m.sqrt(2))**2)*self.Sw*desempenho.Cd_ideal(self)
                L_Vlof_r2 = 0.5*rho*(((1.2*(m.sqrt((2*W)/(rho*self.Sw*self.Clmax))))/m.sqrt(2))**2)*self.Sw*desempenho.Cl_ideal(self)
                Sg = (1.44*W**2)/(self.g*rho*self.Sw*self.Clmax*(T_Vlof_r2-D_Vlof_r2-self.mu*(W-L_Vlof_r2)))
                if Sg <= 100:
                    Carga_util.append([Sg, W, rho]) # [Distância de decolagem, Peso e Densidade do ar]
                else:
                    break
                mtow += 0.1
            if rho == 1.225: rho = 2
            elif rho == 1.156: rho = 3
            else: break
        x1, x2, x3 = [],[],[] # Valores de distância de decolagem para diferentes pesos na densidade do ar de 0m, 600m e 1200m
        y1, y2, y3 = [],[],[] # Valores de Pesos (W) diferentes para deolagem na densidade do ar de 0m, 600m e 1200m
        mtowF, mtowS, mtowI = 10,10,10 # Força as variáveis de mtow(kg) existirem no MDO
        for i in Carga_util:
            if i[2] == 1.225:
                x1.append(i[0]) # Valores de dist. de decolagem com rho = 1.225 kg/m³
                y1.append(i[1]) # Valores de Peso com rho = 1.225 kg/m³
                if i[0] <= 50: # Distância (m) que se espera que a aeroanave atinja a velocidade de decolagem em rho = 1.225 kg/m³ 
                    mtowF = i[1]/self.g # Se o menor elemento de i[0] > "condição acima", então mtowF = 1
            elif i[2] == 1.156:
                x2.append(i[0]) # Valores de dist. de decolagem com rho = 1.156 kg/m³
                y2.append(i[1]) # Valores de Peso com rho = 1.156 kg/m³
                if i[0] <= 50: # Distância (m) que se espera que a aeroanave atinja a velocidade de decolagem em rho = 1.156 kg/m³
                    mtowS = i[1]/self.g # Se o menor elemento de i[0] > "condição acima", então mtowS = 1
            elif i[2] == 1.090:
                x3.append(i[0]) # Valores de dist. de decolagem com rho = 1.090 kg/m³
                y3.append(i[1]) # Valores de Peso com rho = 1.090 kg/m³
                if i[0] <= 50: # Distância (m) que se espera que a aeroanave atinja a velocidade de decolagem em rho = 1.090 kg/m³
                    mtowI = i[1]/self.g # Se o menor elemento de i[0] > "condição acima", então mtowI = 1
            else:
                break
        if self.rho == 1.225:
            return mtowF
        elif self.rho == 1.156:
            return mtowS
        elif self.rho == 1.090:
            return mtowI