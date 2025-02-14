import csv

def avaliar_geometria(geometria):
    if len(geometria) == 0:
        return 0, 0, 0, 0, 0
    b = 2*geometria[-1][0] # Envergadura
    S = 0
    c = 0

    cr = geometria[0][1]  # Corda na raiz
    ct = geometria[-1][1] # Corda na tip

    yac = b*(2*ct + cr)/(6*ct + 6*cr) # Obtenção do Yac através de geometria analítica
    xac = 0
    for i in range(1, len(geometria)):
        h = geometria[i][0] - geometria[i-1][0]
        cm = (geometria[i][1] + geometria[i-1][1])
        S += h*cm # Somatório das áreas por intervalo entre seções

        ck = geometria[i][1]
        ck1 = geometria[i-1][1]
        c += (ck1**2 + ck1*ck + ck**2)*h/3 # Integração do cma

        if geometria[i-1][0] < yac and geometria[i][0] >= yac: # Obtenção do Xac
            xac = geometria[i-1][2] + (yac - geometria[i-1][0])*(geometria[i][2] - geometria[i-1][2])/(geometria[i][0] - geometria[i-1][0]) 
    c = 2*c/S
    xac += c*0.25
    AR = b*b/S
    return S, b, c, AR, xac

def constantes_perfil(perfil, a):
    cl = 0.0
    cm = 0.0
    cd = 0.0
    with open(perfil + '.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if round(a) == float(row['Alpha']):
                cl = float(row['Cl'])
                cm = float(row['Cm'])
                cd = float(row['Cd'])
    return cl, cm, cd

def clmax(perfil):
    clmax = -10.0
    with open(perfil + '.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['Cl']) >= clmax:
                clmax = float(row['Cl'])
    return clmax

def a0l(perfil):
    a0l = 0.0
    cl_ant = 0.0
    with open(perfil + '.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['Cl']) >= 0 and cl_ant <= 0:
                if -cl_ant > float(row['Cl']):
                    a0l = float(row['Alpha'])
                else:
                    a0l = float(row['Alpha']) - 0.1
            cl_ant = float(row['Cl'])
    return a0l

def cla(perfil):
    return constantes_perfil(perfil, 1)[0] - constantes_perfil(perfil, 0)[0]