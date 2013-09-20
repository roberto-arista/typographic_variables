## Robo_analyser
#The MIT License (MIT)

#Copyright © 2013 , Roberto Arista - ISIA Urbino

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

### BoxPlot (tesi Roberto Arista – ISIA Urbino)
### Apertura librerie
from xlrd import open_workbook
import numpy as np
import sys
from scipy.stats import mode

"""
Indice TAG:
    - 30 Sans
    - 31 Serif
    - 32 Mono
    - 33 Condensed
"""


### Funzioni
def quality():
    stroke(0)
    strokewidth(1)
    nofill()
    

def quality_type():
    font('Arial')
    fontsize(corpo)
    

def load_data(index):
    lista = [] # Dichiarazione lista vuota    
    for row in sheet.col(index):
        if isinstance(row.value, unicode) is True:
            titolo = row.value
        if isinstance(row.value, float) is True:            
            lista.append(row.value)
    return lista, titolo

    
def load_data_search(index, ricerca):
    lista = [] # Dichiarazione lista vuota
    count = 0 # Dichiarazione contatore
    
    for row in sheet.col(index):
        if isinstance(row.value, unicode) is True:
            titolo = row.value
        
        for i in ricerca:    
            if isinstance(row.value, float) is True and i in sheet.cell(count, 2).value:            
                lista.append(row.value)
        
        # Avanzamento contatore
        count +=1

    return lista, titolo, ricerca
    
def load_data_avoid(index, avoid):
    lista = [] # Dichiarazione lista vuota
    count = 0 # Dichiarazione contatore
    
    for row in sheet.col(index):
        if isinstance(row.value, unicode) is True:
            titolo = row.value
        
        for i in avoid:
            if isinstance(row.value, float) is True and sheet.cell(count, i).value == 0:            
                lista.append(row.value)
        
        # Avanzamento contatore
        count +=1

    return lista, titolo, avoid


def load_data_bool(index, scelta):
    lista = [] # Dichiarazione lista vuota
    count = 0 # Dichiarazione contatore
    
    for row in sheet.col(index):
        if isinstance(row.value, unicode) is True:
            titolo = row.value
            selettore = sheet.cell(count, scelta).value
        if isinstance(row.value, float) is True and sheet.cell(count, scelta).value == 1:            
            lista.append(row.value)
        
        # Avanzamento contatore
        count +=1

    return lista, titolo, selettore
    

def boxplot(x, y, lista_array, width, fattore, titolo, arr, selettore):
    
    # Calcoli
    whisker_down = round(np.percentile(lista_array, 5), arr)
    whisker_down_graph = -((whisker_down*fattore)+y) # baffo inferiore
    
    perc25 = round(np.percentile(lista_array, 25), arr) # 25esimo percentile
    perc25_graph = -((perc25*fattore)+y)
    
    mean = round(np.mean(lista_array), arr) # media aritmetica
    mean_graph = -((mean*fattore)+y)
    
    mediana = round(np.median(lista_array), arr) # mediana
    mediana_graph = -((mediana*fattore)+y)
    
    perc75 = round(np.percentile(lista_array, 75), arr) # 75esimo percentile
    perc75_graph = -((perc75*fattore)+y)
    
    whisker_up = round(np.percentile(lista_array, 95), arr) # Baffo superiore
    whisker_up_graph = -((whisker_up*fattore)+y)
    
    moda = round(float(mode(lista_array)[0]), arr) # Moda
    moda_occur = int(mode(lista_array)[1])
    moda_graph = -((moda*fattore)+y)
    
    # Baffo inferiore
    line(x-width/2, whisker_down_graph, x+width/2, whisker_down_graph)
    
    # Fondo bianco percentili 25 e 75
    nostroke()
    fill(1)
    rect(x-width/2, perc25_graph, width, perc75_graph-perc25_graph)
    
    # Mediana
    nofill()
    stroke(0)
    line(x-width/2, mediana_graph, x+width/2, mediana_graph)
    
    # Media aritmetica
    stroke(1,0,0)
    line(x-width/2, mean_graph, x+width/2, mean_graph)
    
    # Moda
    stroke(0,0,1)
    line(x-width/2, moda_graph, x+width/2, moda_graph)
    
    # Percentili 25 e 75
    stroke(0)
    rect(x-width/2, perc25_graph, width, perc75_graph-perc25_graph)
    
    # Baffo superiore
    stroke(0)
    line(x-width/2, whisker_up_graph, x+width/2, whisker_up_graph)
    
    # Link fra percentili e baffi
    line(x, whisker_down_graph, x, perc25_graph) # inferiore
    line(x, whisker_up_graph, x, perc75_graph) # superiore
    
    # Didascalie
    fill(0)
    text(u'5°: '+str(whisker_down), x+width/1.5, whisker_down_graph+corpo/3.0) # Baffo inferiore
    text(u'25°: '+str(perc25), x+width/1.5, perc25_graph+corpo/3.0) # 25esimo percentile
    text('Mediana: '+str(mediana), x+width/1.5, mediana_graph+corpo/3.0) # mediana
    text('Media: '+str(mean), x+width/1.5, mean_graph+corpo/3.0) # Media aritmetica 
    text('Moda: '+str(moda)+' ('+str(moda_occur)+')', x+width/1.5, moda_graph+corpo/3.0)
    text(u'75°: '+str(perc75), x+width/1.5, perc75_graph+corpo/3.0) # 75esimo percentile
    text(u'95°: '+str(whisker_up), x+width/1.5, whisker_up_graph+corpo/3.0) # Baffo superiore
    transform(CORNER)
    translate(x-2, whisker_down_graph+width/4)
    rotate(-90)
    
    # titolo boxplot
    if selettore:
        text(titolo+' ('+selettore+')', 0, 0)
    else:
        text(titolo, 0, 0)
    
    reset()
    nofill()
    
    
def coordinate_system():
    strokewidth(0.25)
    for i in range(0, 900, 10):
        stroke(0.75)
        line(50, -i, WIDTH-100, -i) # Linee sistema di riferimento
        
        nostroke()
        fill(0)
        text(str(i/fattore), 40, -i) # Valori griglia

    stroke(0.5) # colore traccia
    line(50, -900, 50, 25) # asse y
    line(25, 0, WIDTH-100, 0) # asse x
    


### Variabili
xls_input = 'misurazioni.xls'

# Fattore di ingradimento
fattore = 500.0

# Corpo carattere
corpo = 6

# Liste tag peso
light_list = ['Light', 'Thin', 'Hairline', 'Extralight']
regular_list = ['Regular', 'Book', 'Roman', 'Normal', 'Medium']
bold_list = ['Bold', 'Demi', 'Semibold']
black_list = ['Black', 'Heavy', 'Extrabold', 'BoldNonextended']

### Comandi
# Dimensione tavola da disegno
size(4000,1500)

# Apertura foglio di calcolo
book = open_workbook(xls_input)
sheet = book.sheet_by_index(0)

# Definizione del sistema di orientamento
translate(0,1200)

# Qualità del testo vicino al boxplot
quality_type()

# Sistema di riferimento
coordinate_system()

# Qualità del boxplot
quality()

## Peso
# Light
tupla = load_data_search(4, light_list)
boxplot(150, 0, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Regular
tupla = load_data_search(4, regular_list)
boxplot(300, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Bold
tupla = load_data_search(4, bold_list)
boxplot(450, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Black
tupla = load_data_search(4, black_list)
boxplot(600, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

## Grado di monolinearità (diviso in sans e serif, no mono)
# Sans
tupla = load_data_bool(5, 30)
boxplot(750, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

# Serif
tupla = load_data_bool(5, 31)
boxplot(900, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Rapporto ascendenti / xHeight
# Sans
tupla = load_data_bool(7, 30)
boxplot(1050, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

# Serif
tupla = load_data_bool(7, 31)
boxplot(1200, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Rapporto discendenti / xHeight
# Sans
tupla = load_data_bool(8, 30)
boxplot(1350, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

# Serif
tupla = load_data_bool(8, 31)
boxplot(1500, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Espansione n
# Sans e serif
tupla = load_data_avoid(9, [32, 33])
boxplot(1650, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Condensed
tupla = load_data_bool(9, 33)
boxplot(1800, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Espansione o
# Sans e serif
tupla = load_data_avoid(10, [32, 33])
boxplot(1950, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Condensed
tupla = load_data_bool(10, 33)
boxplot(2100, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Espansione R
# Sans e serif
tupla = load_data_avoid(12, [32, 33])
boxplot(2400, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Condensed
tupla = load_data_bool(12, 33)
boxplot(2550, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Espansione O
# Sans e serif
tupla = load_data_avoid(13, [32, 33])
boxplot(2700, -1200, tupla[0], 20, fattore, tupla[1], 4, str(tupla[2][0]))

# Condensed
tupla = load_data_bool(13, 33)
boxplot(2850, -1200, tupla[0], 20, fattore, tupla[1], 4, tupla[2])

## Squadrature
# Media
tupla = load_data(15)
boxplot(3150, -1200, tupla[0], 20, fattore, tupla[1], 4, 'all')

# Interna media
tupla = load_data(16)
boxplot(3300, -1200, tupla[0], 20, fattore, tupla[1], 4, 'all')

# Esterna media
tupla = load_data(17)
boxplot(3450, -1200, tupla[0], 20, fattore, tupla[1], 4, 'all')

# Indice di progressività di variazione della curva
tupla = load_data(18)
boxplot(3600, -1200, tupla[0], 20, fattore, tupla[1], 4, 'all')

# Esportazione della tavola
canvas.save('out_singolo1.pdf')
print "END"

