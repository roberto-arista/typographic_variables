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

### Apertura librerie
import os
import datetime as dt
from xlwt import Workbook
import sys

### Variabili
dest = 'robo_analyser'

### Comandi
# Inizio script
ds = dt.datetime.now()
print "Start!", ds

# Apertura di un file xls
book = Workbook()

# Aggiunta di un foglio
sheet1 = book.add_sheet('nomi')

# Operatore della navigazione nelle sottocartelle
camminata = os.walk(dest)

# Ciclo di collezione dei nomi dei file
row = 0
count_files = 0
for fol in camminata:
	folder = fol[0]
	files = fol[2]
	
	for name in files:
		if name != '.DS_Store' and name != '.gitignore' and name != '.directory' and name[-3:] != 'pfm':
			print folder+'/'+name
			f = OpenFont(folder+'/'+name, showUI = False)
			
			# Scrittura nome postscript
			sheet1.write(row, 0, f.info.postscriptFullName)
			
			# Scrittura nome famiglia
			sheet1.write(row, 1, f.info.familyName)
			
			# Scrittura stile carattere
			sheet1.write(row, 2, f.info.styleName)
			
			# Nome designer, fonderia, indirizzo web
			if f.info.openTypeNameDesigner:
				sheet1.write(row, 3, f.info.openTypeNameDesigner)
			if f.info.openTypeNameDesignerURL:
				sheet1.write(row, 4, f.info.openTypeNameDesignerURL)
			if f.info.openTypeNameManufacturer:
				sheet1.write(row, 5, f.info.openTypeNameManufacturer)
			
			# Calcolo della baseline, punto più basso di tutti i tracciati (rispetto alla x)	
			presenza_font = 'x' in f

			if presenza_font is True:
				x = f['x']
			else:
			 	x = f['uni0078']
			
			# Dichiarazione della lista che accoglierà i punti dei tracciati
			lista_punti = []
			
			# Iterazione sui contorni e sui punti del tracciato
			for con in x:
				for p in con.points:
					lista_punti.append(p.y)
			
			# Riordino della lista (crescente) ed inserimento del punto più basso nel foglio di calcolo
			lista_punti.sort()
			sheet1.write(row, 6, lista_punti[0])
			
			f.close()
			row+=1

# Chiusura file di testo
book.save('info.xls')

# Fine script
de = dt.datetime.now()
print "End!", de
print "Durata intera dello script:", de-ds