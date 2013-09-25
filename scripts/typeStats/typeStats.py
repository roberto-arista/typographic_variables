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
#    - angolo spessore minimo
#    - overshooting
#    - ascendenti
#    - discendenti
#    - espansioni (n, o, R, O)


### Importazione moduli esterni
import robofab
from robofab.world import *
from robofab.pens.filterPen import flattenGlyph, _estimateCubicCurveLength 
from operator import itemgetter
from math import fabs, hypot
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
        
    # Funzione che copia il glifo in una nuova cassa e lo appiattisce
    def copyAndFlat(self, glyphName, font, precision):
        # Apertura glifo
        glyph = font[glyphName]
        
        # Creazione di una cassa temporanea
        glyph_flat = glyph.getLayer('flat', clear = True)
        
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
        
        # Ciclo che itera sui contorni della x
        list_y = [] # Creazione di una lista in cui collezionare i dati
        for con in x:
            for pt in con.points:
                
                # Collezione delle ordinate dei punti di ancoraggio, non manipolatori
                if pt.type != 'offCurve':
                    list_y.append(pt.y)
        
        # Riordinamento della lista (crescente)
        list_y.sort()
        
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
        x_stats = x.getLayer('stats', clear = True)
        stats.rect(x_stats, x_stats.width/2.0, xHeight_lowercase, x_stats.width, 2)
        
        # Restituzione dell'xHeight
        return xHeight_lowercase
        
    
    # Definizione della funzione in grado di estrapolare il peso di un carattere
    def weight(self, font):
        
        # Invocazione glifo nella cassa
        l = font['l']
        
        # Copia appiattita su cui fare le misurazioni
        l_copy = stats.copyAndFlat('l', font, 10)
        
        # Raccolta delle ascisse in una lista
        list_x = []
        for con in l_copy:
            for pt in con.points:
                list_x.append(round(pt.x, 0))
        
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
        l_stats = l.getLayer('stats', clear = True)
        stats.rect(l_stats, estremo_1-0.5, l.box[3]/2.0, 1, l.box[3])
        stats.rect(l_stats, estremo_2-0.5, l.box[3]/2.0, 1, l.box[3])
        
        return weight
        
        
    # Funzione in grado di estrarre il valore di contrasto da un carattere
    def contrast(self, font):
        
        # Glifo della cassa
        o = font['o']
        print o
        
        # Copia appiattita su cui fare la valutazione interno/esterno
        o_flat = stats.copyAndFlat('o', font, 10)
        print o_flat
        
        # Valutazione automatica interno/esterno
        len_0 = len(o_flat[0].points)
        len_1 = len(o_flat[1].points)
        
        # Creazione livelli interno/esterno
        livello_esterno = o.getLayer('esterno', clear=True)
        livello_interno = o.getLayer('interno', clear=True)
        
        # Travaso contorni
        if len_0 > len_1:
            # Copia contorni nei livelli di destinazione
            livello_esterno.appendContour(o[0])
            livello_interno.appendContour(o[1])
            
        elif len_0 < len_1:
            # Copia contorni nei livelli di destinazione
            livello_esterno.appendContour(o[1])
            livello_interno.appendContour(o[0])
        
        else:
            print "Errore"
            sys.exit()
                
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
        
        print lista_distanze[-1][0][0][0]
        print lista_distanze[-1][0][0][1]
        
        # Verifica visiva della misurazione
        o_stats = o.getLayer('stats', clear = True)
        stats.rect(o_stats, lista_distanze[0][0][0][0], lista_distanze[0][0][0][1], 2, 2) # Minore
        stats.rect(o_stats, lista_distanze[0][0][1][0], lista_distanze[0][0][1][1], 2, 2) # Minore
        stats.rect(o_stats, lista_distanze[-1][0][0][0], lista_distanze[-1][0][0][1], 2, 2) # Maggiore
        stats.rect(o_stats, lista_distanze[-1][0][1][0], lista_distanze[-1][0][1][1], 2, 2) # Maggiore
        
        # Restituzione del valore
        return contrast


### Variabili
font = OpenFont('test.ufo')

### Istruzioni
# Invocazione della classe
stats = typeStats()

# Preparazione misurazione, creazione font di copia su cui lavorare
temp_font = stats.stats_preparation(font)
temp_font.save('temp_font.ufo')

# Lunghezza di un contorno
contorno1 = temp_font['a'][0]
contourLength = stats.contourLength(contorno1)
print "Contorno:\t", contourLength

# xHeight minuscola
xHeight_lowercase = stats.xHeight(temp_font, 'lowercase')
print "xHeight:\t", xHeight_lowercase

# xHeight maiuscola
xHeight_uppercase = stats.xHeight(temp_font, 'uppercase')
print "XHeight:\t", xHeight_uppercase

# Peso del carattere 
weight = stats.weight(temp_font)
print "Peso:\t\t", weight

# Contrasto del carattere
contrasto = stats.contrast(temp_font)
print "Contrasto:\t", contrasto

# Salvataggio della font con i parametri di misurazione
temp_font.save('temp_font.ufo')
