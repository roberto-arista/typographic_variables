"""
Copyright (c) 2013 - Roberto Arista (http://projects.robertoarista.it/), ISIA Urbino (http://www.isiaurbino.net/home/)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

#To do list:
#- squadratura media
#- squadratura interna
#- squadratura esterna


### Importazione moduli esterni
import robofab
from robofab.world import *
from robofab.pens.filterPen import flattenGlyph, _estimateCubicCurveLength 
from operator import itemgetter
from math import fabs, hypot, atan, degrees
import sys

### Classi e funzioni
class typeStats:

    def __init__(self):
        return None
    
    # Funzione che riordina un iterabile per occorrenze
    def occurDict(self, items):
        d = {}
        for i in items:
            if i in d:
                d[i] = d[i]+1
            else:
                d[i] = 1
        return d
        
    # Creazione di una font copia in cui lavorare
    def stats_preparation(self, font):
        # Copia della font e restituzione
        temp_font = font.copy()
        
        return temp_font
        
    def angle_segment(self, punto1, punto2):
        # Calcolo del coefficiente angolare della retta
        if int(punto1[0]) != int(punto2[0]):
    		m = degrees(atan((-punto2[1]+punto1[1])/(punto2[0]-punto1[0])))-90
    		
    		if -180 <= m < -90:
    			m = (m+180)
    		elif 180 >= m > 90:
    			m = (m-180)
    	else:
    		m = 0
    	
    	# Restituzione dell'angolo
    	return m
    
    # Filtro dei punti (mode == x, y, xy)
    def filter_points(self, glyph, mode):
        
        # Creazione di una lista che accoglierà i dati
        list_points = []
        
        # Ciclo che itera sui contorni del glifo
        for con in glyph:
            
            # Ciclo che itera sui punti del glifo
            for pt in con.points:
                
                # Selezione dei punti di ancoraggio
                if pt.type != 'offCurve':
                    
                    # Filtro della tipologia di punto
                    if mode == 'x':
                        list_points.append(pt.x)
                    
                    elif mode == 'y':
                        list_points.append(pt.y)
                    
                    elif mode == 'xy':
                        list_points.append((pt.x, pt.y))
                    
                    else:
                        print "C'è un errore"
        
        # Restituzione lista
        return list_points
        
    # Funzione che copia il glifo in una nuova cassa e lo appiattisce
    def copyAndFlat(self, glyphName, font, precision):
        # Apertura glifo
        glyph = font[glyphName]
        
        # Creazione di una cassa temporanea
        glyph_flat = glyph.getLayer('flat', clear = False)
        
        # Copia del glifo in un'altra font
        glyph_matrix = glyph.copy()
        glyph_flat.appendGlyph(glyph_matrix)
        
        # Appiattimento della copia
        flattenGlyph(glyph_flat, precision)
        
        return glyph_flat
        
    def contourLength(self, con):
        # Lista vuota che dovrà accogliere le misure
        lista_misure = [] 
        
        # Dichiarazione punto di partenza del tracciato
        begin = con.points[0]
        
        # Ciclo che itera sui segmenti
        for seg in con:
            
            # Curve di terzo grado
            if len(seg.points) == 3:
                misura = _estimateCubicCurveLength((begin.x, begin.y), 
                                                   (seg[0].x, seg[0].y), 
                                                   (seg[1].x, seg[1].y), 
                                                   (seg[2].x, seg[2].y), 
                                                    precision=10)

                # Avanzamento punto di partenza del calcolo
                begin = seg[2]
            
            elif len(seg.points) == 1:
                # Calcolo della lunghezza del segmento mediante Pitagora
                misura = hypot((begin.x - seg[0].x), (begin.y - seg[0].y))
                                
                # Avanzamento punto di partenza del calcolo 
                begin = seg[0]
                
            else:
                print "Errore, c'è un problema"
        
            # Collezionamento delle lunghezze
            lista_misure.append(misura)
        
        # Sommatoria delle misure prese
        length = sum(lista_misure)
        
        return length
        
    # Procedura in grado di disegnare un rettangolo
    def rect(self, glyph, x_center, y_center, width, height):
        # Invocazione della penna
        pen = glyph.getPen()
        
        # Disegno
        pen.moveTo((x_center-width/2.0, y_center+height/2.0))
        pen.lineTo((x_center+width/2.0, y_center+height/2.0))
        pen.lineTo((x_center+width/2.0, y_center-height/2.0))
        pen.lineTo((x_center-width/2.0, y_center-height/2.0))
        pen.lineTo((x_center-width/2.0, y_center+height/2.0))
        
        # Chiusura del tracciato ed aggiornamento
        pen.closePath()
        glyph.update()
        
    # Procedura che separa correttamente contorno interno/esterno della o
    def contours_separation(self, glyph):
        
        # Calcolo delle lunghezze dei contorni    
        contourLength_0 = stats.contourLength(glyph[0])
        contourLength_1 = stats.contourLength(glyph[1])
                
        # Creazione livelli interno/esterno
        livello_esterno = glyph.getLayer('esterno', clear = False)
        livello_interno = glyph.getLayer('interno', clear = False)
        
        # Travaso contorni
        if contourLength_0 > contourLength_1:
            # Copia contorni nei livelli di destinazione
            livello_esterno.appendContour(glyph[0])
            livello_interno.appendContour(glyph[1])
            
        elif contourLength_0 < contourLength_1:
            # Copia contorni nei livelli di destinazione
            livello_esterno.appendContour(glyph[1])
            livello_interno.appendContour(glyph[0])
        
        else:
            print "Errore"
            sys.exit()
        
        # Restituzione dei livelli 
        return livello_interno, livello_esterno
    

    # Funzione per il calcolo dell'xHeight minuscola
    def xHeight(self, font, case):
        
        # Apertura del glifo corretto nella cassa
        if case == 'lowercase':
            x = font['x']
        elif case == 'uppercase':
            x = font['X']
        else:
            print "C'è un errore!"
            sys.exit()
        
        # Estrazione delle ordinate dal glifo
        list_y = stats.filter_points(x, 'y')
        
        # Eliminazione dei multipli
        set_y = set(list_y)
        
        # Riconversione in lista e riordinamento
        list_y = list(set_y)
        list_y.sort()
        
        if (list_y[-1] - list_y[-2]) < 5:
            xHeight_lowercase = (list_y[-1] + list_y[-2])/2.0
        else:
            xHeight_lowercase = list_y[-1]
            
        # Verifica visiva della misurazione
        x_stats = x.getLayer('stats', clear = False)
        stats.rect(x_stats, x_stats.width/2.0, xHeight_lowercase, x_stats.width, 2)
        
        # Restituzione dell'xHeight
        return xHeight_lowercase
        
    
    # Definizione della funzione in grado di estrapolare il peso di un carattere
    def weight(self, font):
        
        # Invocazione glifo nella cassa
        l = font['l']
        
        # Copia appiattita su cui fare le misurazioni
        l_copy = stats.copyAndFlat('l', font, 10)
        
        # Filtraggio e arrotondamento delle ascisse dei punti di ancoraggio
        list_x = stats.filter_points(l_copy, 'x')
        list_x = [round(x, 0) for x in list_x]

        # Creazione di un dizionario che colleziona le occorrenze di valori della lista
        occurrences = stats.occurDict(list_x)
        
        # Riordino del dizionario per ricorrenze
        dict_occurrences = sorted(occurrences.items(), key=itemgetter(1))
        
        # Estrapolazione degli estremi dell'asta
        estremo_1 = dict_occurrences[-1][0]
        estremo_2 = dict_occurrences[-2][0]
        
        # Travaso del valore in una variabile
        weight = fabs(estremo_2 + estremo_1)/stats.xHeight(font, 'lowercase')
        
        # Verifica visiva della misurazione
        l_stats = l.getLayer('stats', clear = False)
        stats.rect(l_stats, estremo_1-0.5, l.box[3]/2.0, 1, l.box[3])
        stats.rect(l_stats, estremo_2-0.5, l.box[3]/2.0, 1, l.box[3])
        
        return weight
        
        
    # Funzione in grado di estrarre il valore di contrasto da un carattere
    def contrast(self, font):
        # Glifo della cassa
        o = font['o']
        
        # Separazione dei contorni
        livello_interno, livello_esterno = stats.contours_separation(o)
                
        # Appiattimento livello con contorno interno
        flattenGlyph(livello_interno, 10)
        numero_punti_interno = len(livello_interno[0])
        
        # Calcolo della lunghezza del contorno esterno
        length_esterno = stats.contourLength(livello_esterno[0])
        
        # Lunghezza segmenti contorno esterno
        d = length_esterno / numero_punti_interno
        
        # Appiattimento "controllato" del contorno esterno
        flattenGlyph(livello_esterno, d)
        
        # Correzione della direzione dei contorni
        livello_interno.correctDirection()
        livello_esterno.correctDirection()
        
        # Correzione punto di partenza contorni
        livello_interno[0].autoStartSegment()
        livello_esterno[0].autoStartSegment()
        
        # Verifica della corretta direzione
        if livello_interno[0].clockwise == livello_esterno[0].clockwise:
            pass
        else:
            print "C'è un errore!"
        
        # Contorno con numero inferiore di punti
        if len(livello_interno[0]) <= len(livello_esterno[0]):
            len_min = len(livello_interno[0])
        elif len(livello_interno[0]) > len(livello_esterno[0]):
            len_min = len(livello_esterno[0])
        
        # Ciclo che itera sul numero di punti
        lista_distanze = []
        for i in range(len_min-1):
            
            # Punti interessati
            x1 = livello_interno[0].points[i].x
            y1 = livello_interno[0].points[i].y
            
            lista_distanze_dettaglio = []
            for l in range(-3, 4): # Estrarre solo quello più corto
                
                # Indice di controllo
                index = i+l
                    
                if index >= len_min:
                    index = index-len_min
                
                x2 = livello_esterno[0].points[index].x
                y2 = livello_esterno[0].points[index].y
            
                # Calcolo della distanza fra punti contrapposti
                distanza = hypot((x1-x2),(y1-y2))
                
                # Verifica nel dettaglio
                lista_distanze_dettaglio.append((((x1, y1), (x2, y2)), distanza))
            
            # Riordino lista distanze dettaglio
            lista_distanze_dettaglio = sorted(lista_distanze_dettaglio, key=itemgetter(1))
            
            # Inserimento della misura nella lista deputata
            lista_distanze.append(lista_distanze_dettaglio[0])
            
        # Riordino della lista per valori
        lista_distanze = sorted(lista_distanze, key=itemgetter(1))
        
        # Estrazione dello spessore minore e di quello maggiore
        spessore_minore = lista_distanze[0][1]
        spessore_maggiore = lista_distanze[-1][1]
        
        # Calcolo del contrasto
        contrast = spessore_minore/spessore_maggiore
        
        # Calcolo dell'angolo dello spessore minimo
        angle_min_thick = stats.angle_segment(lista_distanze[0][0][0], lista_distanze[0][0][1])
        
        # Verifica visiva della misurazione
        o_stats = o.getLayer('stats', clear = False)
        stats.rect(o_stats, lista_distanze[0][0][0][0], lista_distanze[0][0][0][1], 2, 2) # Minore
        stats.rect(o_stats, lista_distanze[0][0][1][0], lista_distanze[0][0][1][1], 2, 2) # Minore
        stats.rect(o_stats, lista_distanze[-1][0][0][0], lista_distanze[-1][0][0][1], 2, 2) # Maggiore
        stats.rect(o_stats, lista_distanze[-1][0][1][0], lista_distanze[-1][0][1][1], 2, 2) # Maggiore
        
        # Restituzione del valore
        return contrast, angle_min_thick
        
    def overshooting(self, font, xHeight, posizione):
        # Apertura del glifo nella cassa
        o = font['o']
        
        # Coordinate dei punti di ancoraggio del glifo
        lista_xy = stats.filter_points(o, 'xy')
                    
        # Riordinamento secondo l'ordinata
        lista_xy = sorted(lista_xy, key=itemgetter(1))
        
        # Controllo della posizione e dichiarazione della variabile
        if posizione == 'inferiore':
            estremo = lista_xy[0]
            overshooting = fabs(estremo[1])
            
        elif posizione == 'superiore':
            estremo = lista_xy[-1]
            overshooting = estremo[1] - xHeight
            
        else:
            print "C'è un errore"
            sys.exit()
            
        # Verifica visiva
        o_stats = o.getLayer('stats', clear = False)
        
        if posizione == 'inferiore':
            stats.rect(o_stats, o.width/2.0, -overshooting/2.0, o.width, overshooting)
        elif posizione == 'superiore':
            stats.rect(o_stats, o.width/2.0, xHeight+overshooting/2.0, o.width, overshooting)
        
        # Restituzione del valore
        return overshooting
    
    def ascenders(self, font, overshooting_superiore):
        
        # Apertura del glifo in cassa
        f = font['f']
        
        # Coordinate punti di ancoraggio del glifo
        list_y = stats.filter_points(f, 'y')
        
        # Riordino della lista in base alle esigenze di misurazione
        list_y.sort(reverse=True)
        
        # Dichiarazione della variabile
        ascenders = list_y[0]-overshooting_superiore
        
        # Verifica visiva    
        f_stats = f.getLayer('stats', clear = False)
        stats.rect(f_stats, f.width/2.0, ascenders+overshooting_superiore/2.0,f.width, overshooting_superiore)
        stats.rect(f_stats, f.width/2.0, ascenders/2.0, 2, ascenders) # Altezza ascendenti, senza overshooting
        
        # Restituzione della variabile
        return ascenders
    
    def descenders(self, font):
        # Apertura del glifo in cassa
        p = font['p']
        
        # Coordinate delle ordinate dei punti di ancoraggio del glifo
        list_y = stats.filter_points(p, 'y')
        
        # Eliminazione dei multipli
        set_y = set(list_y)
        
        # Riconversione in lista e riordinamento
        list_y = list(set_y)
        list_y.sort(reverse = True)
        
        # Verifica della presenza di una grazia
        if (list_y[-1] - list_y[-2]) < 5:
            descenders = (list_y[-1] + list_y[-2])/2.0
        else:
            descenders = list_y[-1]
            
        # Verifica visiva
        p_stats = p.getLayer('stats', clear = False)
        stats.rect(p_stats, p.width/2.0, descenders-1, p.width, 2)
        
        # Restituzione della variabile
        return descenders
        
    def exp_n(self, font):
        # Apertura glifo nella cassa
        n = font['n']
        
        # Copia appiattita 
        n_flat = stats.copyAndFlat('n', font, 10)
        
        # Ascisse dei punti di ancoraggio del glifo
        list_x = stats.filter_points(n_flat, 'x')
        
        # Riordino per occorrenze
        dizio_punti = stats.occurDict(list_x)
        
        # Riordino della lista
        lista_x_riordinata = sorted(dizio_punti.items(), key=itemgetter(1))
        
        # Estrazione estremi delle aste
        estremi_aste = lista_x_riordinata[-4:]
        
        # Riordinamento lista per valore di ascissa
        estremi_aste = sorted(estremi_aste, key=itemgetter(0))
        
        # Punti medi
        punto_medio_sin = (estremi_aste[0][0] + estremi_aste[1][0])/2.0
        punto_medio_des = (estremi_aste[2][0] + estremi_aste[3][0])/2.0
        
        # Espansione
        expansion_n = punto_medio_des - punto_medio_sin
        
        # Verifica visiva della misurazione --> Punti medi ed estremi
        n_stats = n.getLayer('stats', clear = False)
        
        # Punti medi
        stats.rect(n_stats, punto_medio_sin, n.box[3]/2.0, 2, 2) # Sinistro
        stats.rect(n_stats, punto_medio_des, n.box[3]/2.0, 2, 2) # Destro
        
        # Estremi aste
        stats.rect(n_stats, estremi_aste[0][0], n.box[3]/3.0, 2, 2) 
        stats.rect(n_stats, estremi_aste[1][0], n.box[3]/3.0, 2, 2)
        stats.rect(n_stats, estremi_aste[2][0], n.box[3]/3.0, 2, 2)
        stats.rect(n_stats, estremi_aste[3][0], n.box[3]/3.0, 2, 2)
        
        # Restituzione variabile
        return expansion_n
        
    
    def exp_o(self, font, case): # Aggiungere case
        
        # Apertura del glifo nella cassa
        if case == 'lowercase':
            o = font['o']
        elif case == 'uppercase':
            o = font['O']
        else:
            print "c'è un errore"
            sys.exit()
        
        # Separazione dei contorni
        livello_interno, livello_esterno = stats.contours_separation(o)
        
        # Ascisse dei punti di ancoraggio del contorno esterno della lettera
        list_x_esterno = stats.filter_points(livello_esterno, 'x')
        
        # Ascisse dei punti di ancoraggio del contorno interno della lettera
        list_x_interno = stats.filter_points(livello_interno, 'x')
        
        # Riordino della liste
        list_x_esterno.sort()
        list_x_interno.sort()
        
        # Calcolo punti medi
        punto_medio_sinistro = (list_x_interno[0] + list_x_esterno[0])/2.0
        punto_medio_destro = (list_x_interno[-1] + list_x_esterno[-1])/2.0
        
        # Dichiarazione variabile
        expansion_o = punto_medio_destro - punto_medio_sinistro
        
        # Verifica visiva
        o_stats = o.getLayer('stats', clear = False)
        
        # Punti medi
        stats.rect(o_stats, punto_medio_sinistro, o.box[3]/2.0, 2, 2)
        stats.rect(o_stats, punto_medio_destro, o.box[3]/2.0, 2, 2)
        
        # Estremi
        stats.rect(o_stats, list_x_interno[0], o.box[3]/3.0, 2, 2)
        stats.rect(o_stats, list_x_esterno[0], o.box[3]/3.0, 2, 2)
        stats.rect(o_stats, list_x_interno[-1], o.box[3]/3.0, 2, 2)
        stats.rect(o_stats, list_x_esterno[-1], o.box[3]/3.0, 2, 2)
        
        # Restituzione variabile
        return expansion_o
        
    def exp_R(self, font):
                
        # Apertura glifo nella cassa
        R = font['R']
        
        # Separazione dei contorni (interno, esterno)
        livello_interno, livello_esterno = stats.contours_separation(R)
        
        # Appiattimento dei contorni
        flattenGlyph(livello_interno, 10)
        flattenGlyph(livello_esterno, 10)

        # Selezione delle ascisse dei contorni
        lista_asta_x_sin = stats.filter_points(livello_esterno, 'x')
        lista_asta_x_des = stats.filter_points(livello_interno, 'x')
        
        # Punto medio sinistro, calcolo occorrenze
        lista_asta_x_sin = stats.occurDict(lista_asta_x_sin)
        lista_asta_x_des = stats.occurDict(lista_asta_x_des)
        
        # Punto medio sinistro, riordino occorrenze
        lista_asta_x_sin = sorted(lista_asta_x_sin.items(), key=itemgetter(1), reverse = True)
        lista_asta_x_des = sorted(lista_asta_x_des.items(), key=itemgetter(1), reverse = True)
        
        # Punto medio sinistro, ascissa
        punto_medio_sin = (lista_asta_x_sin[0][0] + lista_asta_x_des[0][0])/2.0
        
        # Punto medio destro
        lista_pancia_x_sin = stats.filter_points(livello_interno, 'x')
        lista_pancia_x_des = stats.filter_points(livello_esterno, 'xy')
        
        # Punto medio destro, estremo interno
        estremo_sinistro = max(lista_pancia_x_sin)
        
        # estremo superiore
        lista_pancia_x_des = sorted(lista_pancia_x_des, key=itemgetter(1), reverse=True)
        estremo_superiore = lista_pancia_x_des[0][1]
        
        # Cernita punti appartenenti alla metà superiore della lettera
        lista_pancia_x_des = [item for item in lista_pancia_x_des if item[1] >= estremo_superiore/2.0]
        
        # Riordino della lista per valori di ascissa
        lista_pancia_x_des = sorted(lista_pancia_x_des, key=itemgetter(0), reverse=True)
        
        # Estremo destro pancia
        estremo_destro = lista_pancia_x_des[0][0]
        
        # Punto medio destro
        punto_medio_des = (estremo_destro + estremo_sinistro)/2.0

        # Espansione della R
        expansion_R = punto_medio_des - punto_medio_sin
        
        # Verifica visiva
        R_stats = R.getLayer('stats', clear = False)
        
        # Punti medi
        stats.rect(R_stats, punto_medio_sin, R.box[3]/1.5, 2, 2)
        stats.rect(R_stats, punto_medio_des, R.box[3]/1.5, 2, 2)
        
        # Estremi
        stats.rect(R_stats, estremo_sinistro, R.box[3]/2.0, 2, 2)
        stats.rect(R_stats, estremo_destro, R.box[3]/2.0, 2, 2)
        stats.rect(R_stats, lista_asta_x_sin[0][0], R.box[3]/2.0, 2, 2)
        stats.rect(R_stats, lista_asta_x_des[0][0], R.box[3]/2.0, 2, 2)
        
        # Restituzione variabile
        return expansion_R


### Variabili
# Dichiarazione del percorso della font da analizzare
input_path = "test.ufo"

### Istruzioni
# Apertura del carattere
font = OpenFont(input_path, showUI = True)

# Invocazione della classe
stats = typeStats()

# Preparazione misurazione, creazione font di copia su cui lavorare
temp_font = stats.stats_preparation(font)
temp_font.save(input_path[:-4]+'_typeStats.ufo')

# Lunghezza di un contorno
contorno1 = temp_font['a'][0]
contourLength = stats.contourLength(contorno1)
print "Contorno:\t\t\t", contourLength

# xHeight minuscola
xHeight = stats.xHeight(temp_font, 'lowercase')
print "xHeight:\t\t\t", xHeight

# xHeight maiuscola
capHeight = stats.xHeight(temp_font, 'uppercase')
print "capHeight:\t\t\t", capHeight

# Peso del carattere 
weight = stats.weight(temp_font)
print "Peso:\t\t\t\t", weight

## Contrasto del carattere e angolo dello spessore minore
#contrasto, angle_min_thick = stats.contrast(temp_font)
#print "Contrasto:\t\t\t", contrasto
#print "Angolo spess min:\t", angle_min_thick

# Calcolo dell'overshooting superiore
overshooting_superiore = stats.overshooting(temp_font, xHeight, 'superiore')
print "Overshooting superiore: ", overshooting_superiore

# Calcolo dell'overshooting inferiore
overshooting_inferiore = stats.overshooting(temp_font, xHeight, 'inferiore')
print "Overshooting inferiore: ", overshooting_inferiore

# Calcolo degli ascendenti
ascendenti = stats.ascenders(temp_font, overshooting_superiore)
print "Ascendenti: ", ascendenti

# Calcolo delle discendenti
discendenti = stats.descenders(temp_font)
print "Discendenti: ", discendenti

# Calcolo dell'espansione della 'n'
espansione_n = stats.exp_n(temp_font)
print "Espansione n: ", espansione_n

# Calcolo dell'espansione della 'o'
espansione_o = stats.exp_o(temp_font, 'lowercase')
print "Espansione o: ", espansione_o

# Rapporto di espansione n/o
no_ratio = espansione_n / espansione_o
print "Rapporto no: ", no_ratio

# Calcolo dell'espansione della 'O'
espansione_O = stats.exp_o(temp_font, 'uppercase')
print "Espansione O: ", espansione_O

# Calcolo dell'espansione della 'R'
espansione_R = stats.exp_R(temp_font)
print "Espansione R: ", espansione_R

# Rapporto di espansione RO
RO_ratio = espansione_R / espansione_O
print "Rapporto RO: ", RO_ratio

# Salvataggio della font con i parametri di misurazione
temp_font.save(input_path[:-4]+'_typeStats.ufo')
