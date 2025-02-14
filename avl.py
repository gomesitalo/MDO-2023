import re
import subprocess
import os
pi = 3.14159265358979323846264

caminho_perfis = './avl/'
caminho_geometrias = './avl/configs/'

def criar_arquivo(aeronave, efeito_solo):
    if efeito_solo:
        arq = open(caminho_geometrias + aeronave.nome + '-ge' + '.avl', 'w')
        arq.write(aeronave.nome + '\n')
        arq.write('0.0\n')          # Mach
        arq.write('0 1 0\n') # IYsym   IZsym   Zsym
        arq.write('%.2f %.2f %.2f\n' % (aeronave.Sw, aeronave.cw, aeronave.bw)) # Sref    Cref    Bref
        arq.write('%.3f 0.0 %.3f\n' % (aeronave.xcg, aeronave.zcg)) # Xref    Yref    Zref (Variei o Zcg -Paulo Robson-)
    else:
        arq = open(caminho_geometrias + aeronave.nome + '.avl', 'w')
        arq.write(aeronave.nome + '\n')
        arq.write('0.0\n')          # Mach
        arq.write('0 0 0.0\n') # IYsym   IZsym   Zsym
        arq.write('%.2f %.2f %.2f\n' % (aeronave.Sw, aeronave.cw, aeronave.bw)) # Sref    Cref    Bref
        arq.write('%.3f 0.0 %.3f\n' % (aeronave.xcg, aeronave.zcg )) # Xref    Yref    Zref (Variei o Zcg -Paulo Robson-)

    arq.write("\nSURFACE\n")
    arq.write("Asa\n")
    arq.write("8 1.0 15 1.0\n") # Discretização
    arq.write("TRANSLATE\n")
    arq.write("0.0 0.0 %.2f\n" % (aeronave.hw))
    arq.write("YDUPLICATE\n0.0\n")
    arq.write("ANGLE\n%.0f\n" % aeronave.iw)
    arq.write("COMPONENT\n1\n")
    for sect in aeronave.geometria_asa:
        arq.write("SECTION\n")
        arq.write("%.2f %.2f 0.0 %.2f 0.0\n" % (sect[2], sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
        arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_asa)

    if aeronave.tipo_ev == 't':
        arq.write("\nSURFACE\n")
        arq.write("EH\n")
        arq.write("4 1.0 6 1.0\n") # Discretização
        arq.write("TRANSLATE\n")
        arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["eh"][0], 0, aeronave.posicoes["eh"][1]+(aeronave.bv/2) -0.02))
        arq.write("YDUPLICATE\n0.0\n")
        arq.write("ANGLE\n%.0f\n" % aeronave.ih)
        arq.write("COMPONENT\n2\n")
        for sect in aeronave.geometria_eh:
            arq.write("SECTION\n")
            arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], sect[0], 0, sect[1])) # Xle    Yle    Zle     Chord   Ainc
            arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_eh)
        
        arq.write("\nSURFACE\n")
        arq.write("EV\n")
        arq.write("4 1.0 6 1.0\n") # Discretização
        arq.write("TRANSLATE\n")
        arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["ev"][0], 0, aeronave.posicoes["ev"][1] - 0.02))
        arq.write("COMPONENT\n2\n")
        for sect in aeronave.geometria_ev:
            arq.write("SECTION\n")
            arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], 0, sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
            arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
    else:
        arq.write("\nSURFACE\n")
        arq.write("EH\n")
        arq.write("4 1.0 6 1.0\n") # Discretização
        arq.write("TRANSLATE\n")
        arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["eh"][0], 0, aeronave.posicoes["eh"][1]))
        arq.write("YDUPLICATE\n0.0\n")
        arq.write("ANGLE\n%.0f\n" % aeronave.ih)
        arq.write("COMPONENT\n2\n")
        for sect in aeronave.geometria_eh:
            arq.write("SECTION\n")
            arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], sect[0], 0, sect[1])) # Xle    Yle    Zle     Chord   Ainc
            arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_eh)

        arq.write("\nSURFACE\n")
        arq.write("EV\n")
        arq.write("4 1.0 6 1.0\n") # Discretização
        arq.write("TRANSLATE\n")
        arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["ev"][0], 0, aeronave.posicoes["ev"][1]))
        if aeronave.tipo_ev == "u":
            arq.write("YDUPLICATE\n0.0\n")
            arq.write("COMPONENT\n2\n")
            for sect in aeronave.geometria_ev:
                arq.write("SECTION\n")
                arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], aeronave.bh/2, sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
                arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
        elif aeronave.tipo_ev == "h":
            arq.write("YDUPLICATE\n0.0\n")
            arq.write("COMPONENT\n2\n")
            arq.write("#inicio do primeiro laco\n")
            for sect in aeronave.geometria_ev:
                arq.write("SECTION\n")
                arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], aeronave.bh/2, sect[0]/2, sect[1])) # Xle    Yle    Zle     Chord   Ainc
                arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
            arq.write("#fim do primeiro laco\n")
            arq.write("\nSURFACE\n")
            arq.write("EV^-1\n")
            arq.write("4 1.0 6 1.0\n") # Discretização
            arq.write("TRANSLATE\n")
            arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["eh"][0], 0, aeronave.posicoes["eh"][1]))
            arq.write("YDUPLICATE\n0.0\n")
            arq.write("COMPONENT\n2\n")
            arq.write("#inicio do segundo laco\n")
            for sect in aeronave.geometria_ev:
                arq.write("SECTION\n")    
                arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], aeronave.bh/2, -sect[0]/2, sect[1])) # Xle    Yle    Zle     Chord   Ainc
                arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
            arq.write("#fim do segundo laço\n")
        elif aeronave.tipo_ev == "c":
            arq.write("COMPONENT\n2\n")
            for sect in aeronave.geometria_ev:
                arq.write("SECTION\n")
                arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], 0, sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
                arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
            arq.write("\nSURFACE\n")
            arq.write("EH\n")
            arq.write("4 1.0 6 1.0\n") # Discretização
            arq.write("TRANSLATE\n")
            arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["eh"][0], 0, aeronave.posicoes["eh"][1]))
            arq.write("YDUPLICATE\n0.0\n")
            arq.write("ANGLE\n%.0f\n" % aeronave.ih)
            arq.write("COMPONENT\n2\n")
            for sect in aeronave.geometria_eh:
                arq.write("SECTION\n")
                arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], sect[0], 0, sect[1])) # Xle    Yle    Zle     Chord   Ainc
                arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_eh)


    # arq.write("\nSURFACE\n")
    # arq.write("EV\n")
    # arq.write("4 1.0 6 1.0\n") # Discretização
    # arq.write("TRANSLATE\n")
    # arq.write("%.2f %.2f %.2f\n" % (aeronave.posicoes["ev"][0], 0, aeronave.posicoes["ev"][1]))
    # arq.write("YDUPLICATE\n0.0\n")
    # arq.write("COMPONENT\n2\n")
    # for sect in aeronave.geometria_ev:
    #     arq.write("SECTION\n")
    #     arq.write("%.2f %.2f %.2f %.2f 0.0\n" % (sect[2], aeronave.bh/2, sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
    #     arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
    arq.close()

def resultados_avl(aeronave, comando): # CM0, CL0, CLa, CMa, Xnp
    process = subprocess.Popen(['avl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if comando[0] == 'solo':
        criar_arquivo(aeronave, True)
        out = process.communicate(bytes('load %s\noper\na a %.3f\nx\nst\n\nquit\n' % (caminho_geometrias + aeronave.nome + '-ge', comando[1]), 'utf-8'))[0]
    else:
        criar_arquivo(aeronave, False)
        if comando[0] == 'alpha':
            out = process.communicate(bytes('load %s\noper\na a %.3f\nx\nst\n\nquit\n' % (caminho_geometrias + aeronave.nome, comando[1]), 'utf-8'))[0]
        if comando[0] == 'trim':
            out = process.communicate(bytes('load %s\noper\na pm %.3f\nx\nst\n\nquit\n' % (caminho_geometrias + aeronave.nome, 0), 'utf-8'))[0]
        
    process.terminate()
    output = out.decode('utf-8')
    results = dict()
    
    match = re.search(r'Execute flow calculation first!', output)
    if match:
        return None
    else:
        match = re.search(r'Alpha =..........', output)
        # if match == None:
        #     print(output)
        results['Alpha'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(Cmtot =..........)', output)
    results['CM'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CLtot =..........)', output)
    results['CL'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CLa =...........)', output)
    results['CLa'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cma =...........)', output)
    results['CMa'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cmq =...........)', output)
    results['CMq'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cnb =...........)', output)
    results['Cnb'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cnr =...........)', output)
    results['Cnr'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Xnp =...........)', output)
    results['Xnp'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CDtot =...........)', output)
    results['CD'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(Clb Cnr / Clr Cnb  =...........)', output)
    results['Sst'] = float(output[match.start() + 22:match.start() + 32])
    
    return results