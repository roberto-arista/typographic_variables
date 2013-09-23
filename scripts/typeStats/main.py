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


### Importazione moduli esterni
import robofab
from robofab.world import *
from robofab.pens.filterPen import flattenGlyph
from operator import itemgetter
from math import fabs
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
        
        # Restituzione dell'xHeight
        return xHeight_lowercase
        
    
    # Definizione della funzione in grado di estrapolare il peso di un carattere
    def weight(self, font):
        
        # Apertura glifo
        l = font['l']
        
        # Creazione di una cassa temporanea
        temp_font = robofab.world.RFont(showUI = False)
        
        # Copia del glifo in un'altra font
        l_matrix = l.copy()
        temp_font.insertGlyph(l_matrix)
        
        # Appiattimento della copia
        l_copy = temp_font['l']
        flattenGlyph(l_copy)
        
        
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
        
        return weight


### Variabili
font = CurrentFont()

### Istruzioni
# Invocazione della classe
stats = typeStats()

# xHeight minuscola
xHeight_lowercase = stats.xHeight(font, 'lowercase')
print xHeight_lowercase

# xHeight maiuscola
xHeight_uppercase = stats.xHeight(font, 'uppercase')
print xHeight_uppercase

# Peso del carattere 
weight = stats.weight(font)
print weight
