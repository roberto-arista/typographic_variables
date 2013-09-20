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

## Apertura librerie
import os
import datetime as dt
import numpy as np
import math as mt
import shutil as sh
from numpy import fabs
from operator import itemgetter
from pyPdf import PdfFileWriter, PdfFileReader
from xlrd import open_workbook
from xlwt import Workbook

print # Spazio per il pannello output

## Funzioni
def check_folders():
	if os.path.exists("output") is False:
		os.makedirs("output")
	if os.path.exists("work") is False:
		os.makedirs("work")

def catchfiles(folder):
	# Creazione di una lista i nomi degli elementi presenti nella cartella input
	lista_files = os.listdir(folder)
	
	# Eliminazione dalla lista dei file .DS_Store
	ds = '.DS_Store' in lista_files
	if ds is True:
		del lista_files[0]
	return lista_files

def reset_stroke_fill():
	nofill()
	nostroke()

def glyph_quality():
	reset_stroke_fill()
	stroke(0.7)
	strokewidth(3)
	font(carattere)
	fontsize(1000)
	
def font_diagram():
	reset_stroke_fill()
	font ('SourceSansPro-Light')
	fontsize(10)
	
def coord_anchor():
	reset_stroke_fill()
	fill(0)
	fontsize(10)
	text(str(int(pt.x))+','+str(int(pt.y)*-1),pt.x-10,pt.y-10)
	rect(pt_x_Prec-5,pt_y_Prec-5,10,10)
	fill(1)
	align(CENTER)
	fontsize(7)
	text(str(count_pt), pt_x_Prec-3,pt_y_Prec+2)
	
def hnd_line():
	reset_stroke_fill()
	stroke(100/255.0,200/255.0,255/255.0)
	strokewidth(2)
	line(pt.x,pt.y,pt.ctrl2.x,pt.ctrl2.y)
	line(pt_x_Prec,pt_y_Prec,pt.ctrl1.x,pt.ctrl1.y)
	
def hnd_circle():
	reset_stroke_fill()
	fill(100/255.0,200/255.0,255/255.0)
	oval(pt.ctrl1.x-5,pt.ctrl1.y-5, 10,10)
	oval(pt.ctrl2.x-5,pt.ctrl2.y-5, 10,10)
	fill(0)
	align(CENTER)
	fontsize(7)
	text(str(count_pt), pt.ctrl1.x-3,pt.ctrl1.y+2)
	text(str(count_pt), pt.ctrl2.x-3,pt.ctrl2.y+2)

def hnd_text():
	reset_stroke_fill()
	fill(0)
	fontsize(10)
	align(CENTER)
	text(str(int(pt.ctrl1.x))+','+str(int(pt.ctrl1.y)*-1)+'(1)',pt.ctrl1.x-10,pt.ctrl1.y-10)
	text(str(int(pt.ctrl2.x))+','+str(int(pt.ctrl2.y)*-1)+'(2)',pt.ctrl2.x-10,pt.ctrl2.y-10)
	
def multiple_lines(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5):
	p1 = line(x1,y1,x2,y2, draw=False)
	p2 = line(x1,y1,x3,y3, draw=False)
	p3 = line(x4,y4,x5,y5, draw=False)
	p4 = line(x4,y4,x3,y3, draw=False)
	return p1,p2,p3,p4

def sq_text():
	reset_stroke_fill()
	fill(100/255.0,200/255.0,255/255.0)
	
def quoted_line(x1,y1, x2, y2, stroke_color, stroke_width, direction):
	strokewidth(stroke_width)
	stroke(stroke_color)
	line(x1, y1, x2, y2) #Traccia principale
	strokewidth(stroke_width/2)
	if direction == 'vertical':
		line(x1-10, y1, x1+10, y1)
		line(x2-10, y2, x2+10, y2)
	elif direction == 'horizontal':
		line(x1, y1-10, x1, y1+10)
		line(x2, y2-10, x2, y2+10)
	
def hnd_intersection_single_yPar(y_inter, x1, ctrl_x, y1, ctrl_y):
	a = np.array([[x1,1], [ctrl_x,1]])
	b = np.array([y1,ctrl_y])
	eq1 = np.linalg.solve(a, b)
	x_inter = (y_inter-eq1[1])/eq1[0]
	return x_inter, y_inter

def baseline_calculation(): # Calcolo offset per baseline
	# Qualità del carattere
	font(carattere)
	fontsize(1000)
	
	# Definizione del glifo da analizzare per la baseline
	path_x = textpath('x', 0, 0)
	
	# Creazione di una lista vuota da riempire con i punti appartenenti al tracciato della x minuscola
	lista_coordinate_baseline = []
	for pt in path_x:
		if pt.x != 0.0:
			lista_coordinate_baseline.append((pt.x, pt.y))
	
	lista_ordinata_baseline = sorted(lista_coordinate_baseline, key = itemgetter(1), reverse=True)
	point_inf_baseline = lista_ordinata_baseline[0]
	baseline = float(-point_inf_baseline[1])-int(sheet_info.cell(row_index, 6).value)
	return baseline
	
def occurDict(items):
	d = {}
	for i in items:
		if i in d:
			d[i] = d[i]+1
		else:
			d[i] = 1
	return d
	
def minimum_mono():
	spess_min = lista_ordinata_min[0]
	punto1 = spess_min[0]
	punto2 = spess_min[1]
	appereance_measurement()
	min = line(punto1[1], punto1[2], punto2[1], punto2[2])
	
	if int(punto1[1]) != int(punto2[1]):
		m = mt.degrees(mt.atan((-punto2[2]+punto1[2])/(punto2[1]-punto1[1])))-90

		if -180 <= m < -90:
			m = (m+180)
			
		elif 180 >= m > 90:
			m = (m-180)
		
	else:
		m = 0
	
	# Print sulla tavola dell'angolo
	fill(0,1,0)
	text(str(m)+u'°', (punto1[1]+punto2[1])/2+200, (punto1[2]+punto2[2])/2-200)
	
	min_thick = min.length
	fill(0,0,1)
	text(str(round(min_thick,3)), (punto1[1]+punto2[1])/2+20, (punto1[2]+punto2[2])/2-20)
	return min_thick, m

def maximum_mono():
	spess_max = lista_ordinata_max[len(lista_ordinata_max)-1]
	punto3 = spess_max[0]
	punto4 = spess_max[1]
	appereance_measurement()
	max = line(punto3[1], punto3[2], punto4[1], punto4[2])
	max_thick = max.length
	text(str(round(max_thick,3)), (punto3[1]+punto4[1])/2+20, (punto3[2]+punto4[2])/2-20)
	return max_thick
	
def appereance_measurement():
	reset_stroke_fill()
	stroke(0,0,1)
	fill(0,0,1)
	strokewidth(4)
	font('SourceSansPro-Light')
	fontsize(42)
	
def collect_pdf():
	# Output creation
	lista_files = catchfiles('work')
	output = PdfFileWriter()

	for indice, pagina in enumerate(lista_files):
		doc = PdfFileReader(file('work/'+pagina, "rb"))
		output.addPage(doc.getPage(0))

	# Save and close
	outputStream = file("output/RoboAnalyzer_"+carattere+'_'+str(dh)+'.pdf', "wb")
	output.write(outputStream)
	outputStream.close()
	sh.rmtree('work')

## Variabili
# Creazione di una lista con le variabili da analizzare
variable_list = ['xHeight/corpo', 'Peso', 'Grado di monolinearità', 'Ascendenti / xHeight', 'Discendenti / xHeight', 'Espansione n', 'Espansione o', 'Espansione R', 'Espansione O', 'Squadrature']

# Precisione taglio tracciati (più il valore è alto, maggiore è il numero di divisione dei tracciati nell'analisi)
precision = 20

# Modalità di printing
verboso = 'no'

# Ora e data di esecuzione
dh = dt.datetime.now()
print "Start:", dh

# Lista di caratteri da analizzare (lettura da foglio di calcolo)
wb = open_workbook('input/info.xls')
sheet_info = wb.sheet_by_index(0)
	
# Apertura di un xls per caricare i dati delle variabili + foglio di calcolo
book = Workbook()
sheet_out = book.add_sheet('misurazioni')

# Dimensione della tavola da disegno
size(1000, 1414) # Compatibile con una stampa A4

# Traslazione del sistema di riferimento. Necessario per la disposizione degli assi nativa in nodebox
translate(200,1000)

## Comandi
# Ciclo scandito dagli elementi presenti nella lista dei caratteri da analizzare
row = 0
for row_index in range(sheet_info.nrows):
	
	# Travaso dalla cella del foglio di calcolo
	carattere = str(sheet_info.cell(row_index, 0).value)
	
	# Avanzamento contatore righe foglio di calcolo
	row+=1
	
	# Controllo presenza cartelle di lavoro
	check_folders()
	
	# Creazione di un file di testo per i dati di copertina
	out_cover = open("work/data_cover.txt", 'w')
	out_cover.write('RoboAnalyzer v0.1 - still developing! \n')
	
	# Calcolo baseline
	baseline = baseline_calculation()
	if verboso == 'yes':
		print "Linea di base:", baseline
	
	# Ciclo scandito dalle variabili (una pagina per variabile)
	count_variable = 0
	for variable in variable_list:
	
		# Avanzamento contatore variabili
		count_variable +=1
	
		# Creazione di una lista che raccolga le coordinate, glifo per glifo
		lista_coordinate = []
	
		# Creazione di una lista che raccolga tutte le squadrature, glifo per glifo
		lista_squadrature = []
	
		# Creazione di una lista dettagliata per le squadrature, glifo per glifo
		lista_rich_int_sq = []
		lista_rich_est_sq = []
	
		# Creazione di due liste per differenziare squadrature interne ed esterne
		lista_sq_esterno = []
		lista_sq_interno = []
	
		# Variabili visive glifo in analisi
		glyph_quality()
	
		if variable == 'xHeight/corpo':
			glifo = 'x'
		elif variable == 'Peso':
			glifo = 'l'
		elif variable == 'Grado di monolinearità':
			glifo = 'o'
		elif variable == 'Ascendenti / xHeight':
			glifo = 'f'
		elif variable == 'Discendenti / xHeight':
			glifo = 'p'
		elif variable == 'Espansione n':
			glifo = 'n'
		elif variable == 'Espansione o':
			glifo = 'o'
		elif variable == 'Espansione R':
			glifo = 'R'
		elif variable == 'Espansione O':
			glifo = 'O'
		elif variable == 'Squadrature':
			glifo = 'o'
	
		# Disegno del glifo sulla tavola
		path = textpath(glifo, 0, baseline)
		drawpath(path)

		# Scelta e dimensione del carattere per le misure sulla tavola
		font_diagram()

		# Iterazione sui contorni prensenti nel glifo
		count_contour = 0
		for contour in path.contours:
			count_contour +=1
		
			# Ciclo scandito dai punti del tracciato
			count_pt = 0
			for pt in contour:
		
				# Inserimento delle coordinate dei punti di ancoraggio
				lista_coordinate.append((pt.x,pt.y))
	
				# Contatore dell'iterazioni sui punti dei tracciati
				count_pt +=1
	
				# Istruzioni per il punto di partenza del tracciato
				if pt.cmd is MOVETO:
					# Travaso dei valori del punto di partenza del tracciato
					pt_x_Prec = pt.x
					pt_y_Prec = pt.y
			
					# Funzione per il disegno del punto di ancoraggio
					coord_anchor()
				
				# Istruzioni per le curve
				elif pt.cmd is CURVETO:
					# Linea che congiungono punti di ancoraggio e manipolatori
					hnd_line()
			
					# Terminazioni dei manipolatori
					hnd_circle()
		
					# Punto di ancoraggio
					coord_anchor()
		
					# Comandi di testo per i manipolatori
					hnd_text()
			
					# Comandi di testo e calcolo delle squadrature
					sq_text()
						
					## Calcolo squadrature quadranti (contorno esterno: sup_dx, inf_sx; contorno interno: sup_sx, inf_dx)
					if pt_x_Prec == pt.ctrl1.x:
						if pt.ctrl2.y-pt_y_Prec != 0:
							sq = round((pt.ctrl1.y-pt_y_Prec)/(pt.ctrl2.y-pt_y_Prec), 3)
							fontsize(10)
							if variable == 'Squadrature':
								text(str(sq),pt.ctrl1.x,pt.ctrl1.y+15)
				
							# Inserimento valori squadratura all'interno della lista dedicata
							lista_squadrature.append(sq)
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq, 1)))
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq, 1)))
					
							# Inserimento valori divisi per contorno
							if count_contour == 1:
								lista_sq_esterno.append(sq)
							elif count_contour == 2:
								lista_sq_interno.append(sq)

					if pt.y == pt.ctrl2.y and pt_x_Prec == pt.ctrl1.x:
						if pt.ctrl1.x-pt.x != 0:
							sq = round((pt.ctrl2.x-pt.x)/(pt.ctrl1.x-pt.x), 3)
							fontsize(10)
							if variable == 'Squadrature':
								text(str(sq),pt.ctrl2.x,pt.ctrl2.y+15)
				
							# Inserimento valori squadratura all'interno della lista dedicata
							lista_squadrature.append(sq)
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq, 2)))
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq, 2)))
					
							# Inserimento valori divisi per contorno
							if count_contour == 1:
								lista_sq_esterno.append(sq)
							elif count_contour == 2:
								lista_sq_interno.append(sq)		
					## Calcolo squadrature quadranti (contorno esterno: sup_sx, inf_dx; contorno interno: sup_dx, inf_sx)
					if pt.ctrl1.y == pt_y_Prec and pt.ctrl2.x == pt.x:
						if pt.ctrl2.x-pt_x_Prec != 0:
							sq = round((pt.ctrl1.x-pt_x_Prec)/(pt.ctrl2.x-pt_x_Prec), 3)
							fontsize(10)
							if variable == 'Squadrature':
								text(str(sq),pt.ctrl1.x,pt.ctrl1.y+15)
				
							# Inserimento valori squadratura all'interno della lista dedicata
							lista_squadrature.append(sq)
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq, 1)))
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq, 1)))
					
							# Inserimento valori divisi per contorno
							if count_contour == 1:
								lista_sq_esterno.append(sq)
							elif count_contour == 2:
								lista_sq_interno.append(sq)
			
					if pt.ctrl2.x == pt.x:
						if pt.ctrl1.y-pt.y != 0:
							sq = round((pt.ctrl2.y-pt.y)/(pt.ctrl1.y-pt.y), 3)
							fontsize(10)
							if variable == 'Squadrature':
								text(str(sq),pt.ctrl2.x,pt.ctrl2.y+15)
				
							# Inserimento valori squadratura all'interno della lista dedicata
							lista_squadrature.append(sq)
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq, 2)))
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq, 2)))
					
							# Inserimento valori divisi per contorno
							if count_contour == 1:
								lista_sq_esterno.append(sq)
							elif count_contour == 2:
								lista_sq_interno.append(sq)
				
				# Manipolatori non ortogonali
					if pt.x != pt.ctrl2.x and pt.y != pt.ctrl2.y:
						# Funzione per il punto di intersezione tra manipolatore non ortogonale e ortogonale
						coord_inter = hnd_intersection_single_yPar(pt_y_Prec, pt.x, pt.ctrl2.x, pt.y, pt.ctrl2.y)
				
						# Dichiarazione segmenti per calcolo squadrature
						multiple = multiple_lines(pt.x,pt.y,pt.ctrl2.x,pt.ctrl2.y,coord_inter[0],coord_inter[1],pt_x_Prec,pt_y_Prec,pt.ctrl1.x,pt.ctrl1.y)
						
						# Calcolo squadrature
						if multiple[1].length != 0:
							sq_non_orth = multiple[0].length/multiple[1].length
							lista_squadrature.append(sq_non_orth)
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq_non_orth, 2)))
								lista_sq_esterno.append(sq_non_orth)
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq_non_orth, 2)))
								lista_sq_interno.append(sq_non_orth)
						
						if multiple[3].length != 0:
							sq_orth = multiple[2].length/multiple[3].length
							lista_squadrature.append(sq_orth)
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq_orth, 1)))
								lista_sq_esterno.append(sq_orth)
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq_orth, 1)))
								lista_sq_interno.append(sq_orth)
				
						# Print sulla tavola
						if variable == 'Squadrature':
							text(str(round(sq_non_orth,3)),pt.ctrl2.x,pt.ctrl2.y+15)
							text(str(round(sq_orth,3)),pt.ctrl1.x,pt.ctrl1.y+15)			 
				
					if pt_x_Prec != pt.ctrl1.x and pt_y_Prec != pt.ctrl1.y:
						# Funzione per il punto di intersezione tra manipolatore non ortogonale e ortogonale
						coord_inter = hnd_intersection_single_yPar(pt.y, pt_x_Prec, pt.ctrl1.x, pt_y_Prec, pt.ctrl1.y)
				
						# Dichiarazione segmenti per calcolo lunghezze
						multiple = multiple_lines(pt_x_Prec, pt_y_Prec, pt.ctrl1.x, pt.ctrl1.y, coord_inter[0], coord_inter[1], pt.x, pt.y, pt.ctrl2.x, pt.ctrl2.y)
				
						# Calcolo squadrature
						if multiple[1].length != 0:
							sq_non_orth = multiple[0].length/multiple[1].length
							lista_squadrature.append(sq_non_orth)
							if count_contour == 1:
								 lista_rich_est_sq.append((count_pt, (sq_non_orth, 2)))
								 lista_sq_esterno.append(sq_non_orth)
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq_non_orth, 2)))
								lista_sq_interno.append(sq_non_orth)
								
						if multiple[3].length != 0:
							sq_orth = multiple[2].length/multiple[3].length
							lista_squadrature.append(sq_orth)
							
							if count_contour == 1:
								lista_rich_est_sq.append((count_pt, (sq_orth, 1)))
								lista_sq_esterno.append(sq_orth)
							elif count_contour == 2:
								lista_rich_int_sq.append((count_pt, (sq_orth, 1)))
								lista_sq_interno.append(sq_orth)
				
						# Print sulla tavola
						if variable == 'Squadrature':
							text(str(round(sq_non_orth,3)),pt.ctrl1.x,pt.ctrl1.y+15)
							text(str(round(sq_orth,3)),pt.ctrl2.x,pt.ctrl2.y+15)
		
				# Istruzioni per segmenti e i punti di chiusura
				elif pt.cmd is LINETO or CLOSE:
					coord_anchor()
			
				# Valori della x al ciclo precedente
				pt_x_Prec = pt.x
				pt_y_Prec = pt.y
		
		# Calcolo spaziatura
		lista_coordinate.sort()
	
		# Lista punti di ancoraggio ordinata per y
		lista_ordinata_y = sorted(lista_coordinate, key=itemgetter(1))
	
		# Misure specifiche
		if variable == 'xHeight/corpo':
			# Il punto con ordinata più alta è l'xHeight
			point_max_y = lista_ordinata_y[0]
			xht = float(fabs(point_max_y[1]))
			if verboso == 'yes':
				print "Carattere analizzato (PSname):", carattere
			sheet_out.write(row, 0, str(carattere)) # PSname
			sheet_out.write(row, 1, sheet_info.cell(row_index, 1).value) # famiglia
			sheet_out.write(row, 2, sheet_info.cell(row_index, 2).value) # stile
			out_cover.write("Carattere analizzato (PSname): "+str(carattere)+'\n')
			if verboso == 'yes':
				"xHeight:", xht
			sheet_out.write(row, 3, xht) # xHeight
			out_cover.write("xHeight: "+str(xht)+'\n')
		
			# Variabili visive misurazione
			appereance_measurement()
			line(0, 0, 0, -xht) # Traccia principale
			line(-10, 0, 10, 0) # Estremità traccia principale
			line(-10, -xht, 10, -xht)
			text(str(xht), 20, -xht/2)
	
		elif variable == 'Peso':
			# Creazione di un tracciato frazionato in 200 punti
			lista_density_x = []
			for pt in path.points(200):
				lista_density_x.append(pt.x)
	
			# Scelta degli estremi dell'asta fra i due punti più "densi"
			dizio_density = occurDict(lista_density_x)
			dict_ordered = sorted(dizio_density.items(), key=itemgetter(1), reverse = True)
		
			tsv = fabs(dict_ordered[0][0]-dict_ordered[1][0])
			# print "Spessore aste verticali:", tsv
			wgt = tsv/xht
			if verboso == 'yes':
				print "Peso:", wgt
			sheet_out.write(row, 4, wgt)
			out_cover.write("Peso: "+str(wgt)+'\n')
		
			# Print misurazione
			appereance_measurement()
			line(dict_ordered[0][0], -xht/2, dict_ordered[1][0], -xht/2) # Traccia principale
			line(dict_ordered[0][0], -xht/2+10, dict_ordered[0][0], -xht/2-10) # Estremità traccia principale
			line(dict_ordered[1][0], -xht/2+10, dict_ordered[1][0], -xht/2-10)
			text(str(tsv)+'/'+str(xht)+'='+str(round(tsv/xht,3)), dict_ordered[1][0]+100, -xht/2)
		
		elif variable == 'Grado di monolinearità':
		
			# Creazione delle liste necessarie
			lista_coordinate1 = []
			lista_coordinate2 = []
			lista_dati_complessiva_min = []
			lista_dati_complessiva_max = []
		
			# Ciclo scandito dal numero di contorni (2)
			count_contour = 0
			for contour in path.contours:
				count_contour +=1
			
				# Ciclo scandito dalla divisione proporzionale alla lunghezza dei tracciati
				count_p = 0
				for pt in contour.points(int(contour.length)/precision):
					if count_contour == 1:
						fill(0,1,0)
					else:
						fill(1,0,0)
				
					# Prosecuzione contatore punti sul tracciato
				  	count_p+=1
			
					# Riempimento delle liste delle coordinate dei punti creati sul tracciato (ogni tracciato ha la sua lista)
					if count_contour == 1:
						lista_coordinate1.append((count_p, pt.x, pt.y))
					if count_contour == 2:
						lista_coordinate2.append((count_p, pt.x, pt.y))
	
			# Iterazione sulla lista di coordinate del primo tracciato
			for indice1, coo1 in enumerate(lista_coordinate1):
		
				# Creazione di una lista temporanea delle misure per l'ipotenusa massima
				lista_temp_max = []
		
				# Iterazione sulla lista di coordinate del secondo tracciato
				for indice2, coo2 in enumerate(lista_coordinate2):
		
					# Misurazione dei segmenti massimi (gamma legata alla numerazione dei punti)
					ipo_max = mt.sqrt((coo1[2]-coo2[2])**2 + (coo1[1]-coo2[1])**2)
					lista_temp_max.append((coo1, coo2, ipo_max))
			
					# Misurazione dell'ipotenusa minima
					ipo_min = mt.sqrt((coo1[2]-coo2[2])**2 + (coo1[1]-coo2[1])**2)
					lista_dati_complessiva_min.append((coo1, coo2, ipo_min))
		
				# Estrazione delle ipotenuse rilevanti dalla lista generata il ciclo precedente
				lista_temp_ordinata = sorted(lista_temp_max, key=lambda ipo: ipo[2])
				ipotenusa_scelta = lista_temp_ordinata[0]
		
				# Inserimento dei dati all'interno della lista finale degli spessori
				lista_dati_complessiva_max.append(ipotenusa_scelta)
		
			# Riordino delle liste secondo il parametro delle ipotenuse
			lista_ordinata_min = sorted(lista_dati_complessiva_min, key=lambda ipo: ipo[2])
			lista_ordinata_max = sorted(lista_dati_complessiva_max, key=lambda ipo: ipo[2])
	
			# Minimo
			min_thick_o = minimum_mono()

			# Massimo
			max_thick_o = maximum_mono()
		
			#Grado di monolinearità
			mono_ratio = min_thick_o[0]/max_thick_o
			m = min_thick_o[1]
			if verboso == 'yes':
				print "Grado di monolinearità:", mono_ratio
				print "Angolo tratto più corto:", m
			sheet_out.write(row, 5, mono_ratio)
			sheet_out.write(row, 21, m)
			out_cover.write("Grado di monolinearità: "+str(mono_ratio)+'\n')
		
			# Entità dei contrasti
			con_amount = mono_ratio**-1
			if verboso == 'yes':
				print "Entità dei contrasti:", con_amount
			sheet_out.write(row, 6, con_amount)
			out_cover.write("Entità dei contrasti: "+str(con_amount)+'\n')
		
			# Overshooting superiore
			point_over = lista_ordinata_y[0]
			over_y = fabs(point_over[1])
			ovs_sup = (over_y-xht)/xht
			if verboso == 'yes':
				print "Overshooting superiore:", ovs_sup
			sheet_out.write(row, 7, ovs_sup)
			out_cover.write("Overshooting superiore: "+str(ovs_sup)+'\n')
				
			# Overshooting inferiore
			point_inf = lista_ordinata_y[len(lista_ordinata_y)-1]
			ovs_inf = point_inf[1]/xht
			if verboso == 'yes':
				print "Overshooting inferiore:", ovs_inf
			sheet_out.write(row, 8, ovs_inf)
			out_cover.write("Overshooting inferiore: "+str(ovs_inf)+'\n\n')
		
			# Print misurazione
			fill(1,0,0,0.5)
			nostroke()
			rect(path.bounds[0][0], 0, path.bounds[1][0]-path.bounds[0][0], ovs_inf)
			text(str(ovs_inf), path.bounds[0][0]-100, 0)
			rect(path.bounds[0][0], -xht, path.bounds[1][0]-path.bounds[0][0], -ovs_sup)
			text(str(ovs_sup), path.bounds[0][0]-100, -xht)
			text(str(min_thick_o[0]/max_thick_o), path.bounds[0][0], 200)
	
		elif variable == 'Ascendenti / xHeight':
			lista_ordinata_y = sorted(lista_coordinate, key=itemgetter(1))
			asc = fabs(lista_ordinata_y[0][1])-ovs_sup-xht
			if verboso == 'yes':
				print "Rapporto ascendenti / xHeight:", asc/xht
			sheet_out.write(row, 9, asc/xht)
			out_cover.write("Rapporto ascendenti / xHeight: "+str(asc/xht)+'\n')
		
			# Variabili visive misurazione
			appereance_measurement()
		
			# Filetto xht
			line(0, 0, 0, -xht) # Traccia principale
			line(-10, 0, 10, 0) # Estremità traccia principale
			line(-10, -xht, 10, -xht)
			text(str(xht), 20, -xht/2)
		
			# Filetto ascendenti
			line(0, -xht, 0, -xht-asc) # Traccia principale
			line(-10, -xht-asc, 10, -xht-asc) # Estremità traccia principale
			text(str(asc), 20, (-xht*2-asc)/2)	
		
		elif variable == 'Discendenti / xHeight':
			lista_ordinata_y = sorted(lista_coordinate, key=itemgetter(1), reverse = True)
			dsc = fabs(lista_ordinata_y[0][1])
			if verboso == 'yes':
				print "Rapporto discendenti / xHeight:", dsc/xht
			sheet_out.write(row, 10, dsc/xht)
			out_cover.write("Rapporto discendenti / xHeight: "+str(dsc/xht)+'\n\n')
		
			# Variabili visive misurazione
			appereance_measurement()
		
			# Filetto xht
			line(0, 0, 0, -xht) # Traccia principale
			line(-10, 0, 10, 0) # Estremità traccia principale
			line(-10, -xht, 10, -xht)
			text(str(xht), 20, -xht/2)
		
			# Filetto discendenti
			line(0, 0, 0, dsc) # Traccia principale
			line(-10, dsc, 10, dsc) # Estremità traccia principale
			text(str(dsc), 20, (dsc)/2)
		
		elif variable == 'Espansione n':
			# Punto medio di separazione delle liste di densità
			punto_medio_x = lista_coordinate[len(lista_coordinate)-1][0]/2
		
			# Creazione lista punti divisi
			lista_div_n = []
		
			# Ciclo scandito dalla divisione in punti del tracciato
			for pt in path.points(300):
				fill(1,0,0)
				rect(pt.x, pt.y, 4, 4)
				lista_div_n.append((pt.x, pt.y))
			
			# Creazione di due liste separate (sinistra_destra)
			lista_div_n_sin = []
			lista_div_n_des = []
		
			for point in lista_div_n:
				if point[0] <= punto_medio_x:
					lista_div_n_sin.append(point[0])
				elif point[0] >= punto_medio_x:
					lista_div_n_des.append(point[0])
				
			# Punto medio asta sinistra
			dizio_density = occurDict(lista_div_n_sin)
			dict_ordered = sorted(dizio_density.items(), key=itemgetter(1), reverse = True)
			punto_medio_sin = fabs(dict_ordered[0][0]+dict_ordered[1][0])/2
		
			# Punto medio asta destra
			dizio_density = occurDict(lista_div_n_des)
			dict_ordered = sorted(dizio_density.items(), key=itemgetter(1), reverse = True)
			punto_medio_des = fabs(dict_ordered[0][0]+dict_ordered[1][0])/2
		
			# Grado di espansione della n
			exp_n = (punto_medio_des-punto_medio_sin)/xht
			if verboso == 'yes':
				print "Grado di espansione della n:", exp_n
			sheet_out.write(row, 11, exp_n)
			out_cover.write("Grado di espansione della n: "+str(exp_n)+'\n')
		
			# Variabili visive misurazione
			appereance_measurement()
			line(punto_medio_sin, -xht/2, punto_medio_des, -xht/2)
			line(punto_medio_sin, -xht/2+10, punto_medio_sin, -xht/2-10)
			line(punto_medio_des, -xht/2+10, punto_medio_des, -xht/2-10)
			text(str(round(exp_n,3)), (punto_medio_des+punto_medio_sin)/2, -xht/2+50)
		
		elif variable == 'Espansione o':
		
			# Creazione di liste con i punti dei tracciati
			lista_punti_interno = []
			lista_punti_esterno = []
		
			count_contour = 0
			for contour in path.contours:
				count_contour +=1
			
				for pt in contour.points(int(contour.length)/10):
				
					if count_contour == 1:
						fill(0,0,1)
						lista_punti_esterno.append(pt.x)
					
					elif count_contour == 2:
						fill(1,0,0)
						lista_punti_interno.append(pt.x)
		
			# Riordino delle liste, ordine crescente
			lista_punti_esterno.sort()
			lista_punti_interno.sort()
		
			# Calcolo dei punti medi		
			punto_medio_sin = (lista_punti_interno[0]+lista_punti_esterno[0])/2
			punto_medio_des = (lista_punti_interno[-1]+lista_punti_esterno[-1])/2
		
			# Espansione della o
			exp_o = (punto_medio_des-punto_medio_sin)/xht
			if verboso == 'yes':
				print "Grado di espansione della o:", exp_o
			sheet_out.write(row, 12, exp_o)
			out_cover.write("Grado di espansione della o: "+str(exp_o)+'\n')
		
			# Rapporto espansione n-o
			nor = exp_n/exp_o
			if verboso == 'yes':
				print "Rapporto di espansione n-o:", nor
			sheet_out.write(row, 13, nor)
			out_cover.write("Rapporto di espansione n-o: "+str(nor)+'\n')
		
			# Variabili visive misurazione
			appereance_measurement()
			line(punto_medio_sin, -xht/2, punto_medio_des, -xht/2)
			line(punto_medio_sin, -xht/2+10, punto_medio_sin, -xht/2-10)
			line(punto_medio_des, -xht/2+10, punto_medio_des, -xht/2-10)
			text(str(round(exp_o,3)), (punto_medio_des+punto_medio_sin)/2, -xht/2+50)
		
		elif variable == 'Espansione R':
		
			# Creazione di una lista per la raccolta delle coordinate
			lista_punti_complessiva_x = []
		
			# Raccolta coordinate divisione tracciato
			for pt in path.points(400):
				lista_punti_complessiva_x.append(pt.x)
			
			# Estrazione del valore del punto medio per l'asta sinistra
			dizio_sin = occurDict(lista_punti_complessiva_x)
			dict_ordered = sorted(dizio_sin.items(), key=itemgetter(1), reverse = True)
			punto_medio_sin = (dict_ordered[0][0]+dict_ordered[1][0])/2.0 
		
			# Liste da colmare
			lista_punti_interno = []
			lista_punti_esterno_sup = []
		
			# Ciclo scandito dal numero di contorni (estrazione delle ascisse più alte contorno per contorno)
			count_contour = 0
			for contour in path.contours:
				count_contour +=1
			
				for pt in contour.points(int(contour.length)/10):
					if count_contour == 1:
						if fabs(pt.y) > xht/2:
							lista_punti_esterno_sup.append(pt.x)
						fill(1,0,0)
					elif count_contour == 2:
						fill(0,1,0)
						lista_punti_interno.append(pt.x)
					rect(pt.x-2, pt.y-2, 4, 4)
			
			# Riordino ed estrazione dell'ascissa massima del contorno interno
			lista_punti_interno.sort()
			max_interno = lista_punti_interno[-1]
		
			# Riordino ed estrazione dell'ascissa massima del contorno esterno superiore
			lista_punti_esterno_sup.sort()
			max_esterno = lista_punti_esterno_sup[-1]
		
			# Calcolo punto medio pancia superiore destra
			punto_medio_des = (max_esterno+max_interno)/2
		
			# Calcolo espansione R
			exp_R = (punto_medio_des-punto_medio_sin)/xht
			if verboso == 'yes':
				print "Grado di espansione della R:", exp_R
			sheet_out.write(row, 14, exp_R)
			out_cover.write("Grado di espansione della R: "+str(exp_R)+'\n')
		
			# Variabili visive misurazione
			appereance_measurement()
			line(punto_medio_sin, -xht/2, punto_medio_des, -xht/2)
			line(punto_medio_sin, -xht/2+10, punto_medio_sin, -xht/2-10)
			line(punto_medio_des, -xht/2+10, punto_medio_des, -xht/2-10)
			text(str(round(exp_R,3)), (punto_medio_des+punto_medio_sin)/2, -xht/2+50)
		
		elif variable == 'Espansione O':
		
			# Creazione di liste con i punti dei tracciati
			lista_punti_interno = []
			lista_punti_esterno = []
		
			count_contour = 0
			for contour in path.contours:
				count_contour +=1
			
				for pt in contour.points(int(contour.length)/10):
				
					if count_contour == 1:
						fill(0,0,1)
						lista_punti_esterno.append(pt.x)
					
					elif count_contour == 2:
						fill(1,0,0)
						lista_punti_interno.append(pt.x)
		
			# Riordino delle liste, ordine crescente
			lista_punti_esterno.sort()
			lista_punti_interno.sort()
		
			# Calcolo dei punti medi		
			punto_medio_sin = (lista_punti_interno[0]+lista_punti_esterno[0])/2
			punto_medio_des = (lista_punti_interno[-1]+lista_punti_esterno[-1])/2
		
			# Espansione della o
			exp_O = (punto_medio_des-punto_medio_sin)/xht
			if verboso == 'yes':
				print "Grado di espansione della o:", exp_O
			sheet_out.write(row, 15, exp_O)
			out_cover.write("Grado di espansione della o: "+str(exp_O)+'\n')
		
			# Rapporto espansione R-O
			ROr = exp_R/exp_O
			if verboso == 'yes':
				print "Rapporto di espansione R-O:", ROr
			sheet_out.write(row, 16, ROr)
			out_cover.write("Rapporto di espansione R-O: "+str(ROr)+'\n\n')
		
			# Variabili visive misurazione
			appereance_measurement()
			line(punto_medio_sin, -xht-asc/2, punto_medio_des, -xht-asc/2)
			line(punto_medio_sin, -xht-asc/2+10, punto_medio_sin, -xht-asc/2-10)
			line(punto_medio_des, -xht-asc/2+10, punto_medio_des, -xht-asc/2-10)
			text(str(round(exp_O,3)), (punto_medio_des+punto_medio_sin)/2, -xht-asc/2+50)
		
		elif variable == 'Squadrature':
			count_contour = 0
			for contour in path.contours:
				count_contour +=1
			
				for pt in contour:
					if count_contour == 1:
						fill(1,0,0)
					elif count_contour == 2:
						fill(0,1,0)
					#rect(pt.x-2, pt.y-2, 4, 4)
				
			# Calcolo media squadratura
			media_sq = sum(lista_squadrature)/len(lista_squadrature)
			if verboso == 'yes':
				print "Squadratura media:", media_sq
			sheet_out.write(row, 17, media_sq)
			out_cover.write("Squadratura media: "+str(media_sq)+'\n')
		
			# Calcolo media squadratura per contorno
			media_sq_est = sum(lista_sq_esterno)/len(lista_sq_esterno)
			media_sq_int = sum(lista_sq_interno)/len(lista_sq_interno)
			if verboso == 'yes':
				print "Squadratura interna media:", media_sq_int
				print "Squadratura esterna media:", media_sq_est
			sheet_out.write(row, 18, media_sq_int)
			sheet_out.write(row, 19, media_sq_est)
			out_cover.write("Squadratura interna media: "+str(media_sq_int)+'\n')
			out_cover.write("Squadratura esterna media: "+str(media_sq_est)+'\n')
		
			# Calcolo indice di progressività nella variazione del peso di una curva
			prog_wgt_curve = media_sq_est/media_sq_int
			if verboso == 'yes':
				print "Indice di progressività nella variazione del peso di una curva:", prog_wgt_curve
			sheet_out.write(row, 20, prog_wgt_curve)
			out_cover.write("Indice di progressività nella variazione del peso di una curva: "+str(prog_wgt_curve)+'\n\n')
		
			## Disallineamento	
			# Creazioni liste da colmare con i punti dei tracciati (disallineamento)
			lista_punti_esterno = []
			lista_punti_interno = []
		
			# Ciclo scandito dal numero di contorni
			count_contour = 0
			for contour in path.contours:
				count_contour +=1
			
				# Ciclo scandito dalle divisioni dei contorni
				for pt in contour.points(int(contour.length)/3):
					if count_contour == 1:
						fill(0,0,1)
						lista_punti_esterno.append((pt.x, pt.y))
					elif count_contour == 2:
						fill(0,1,0.5)
						lista_punti_interno.append((pt.x, pt.y))
					#rect(pt.x-2, pt.y-2, 4, 4)
				
			# Riordino liste
			lista_punti_interno_y = sorted(lista_punti_interno, key=itemgetter(1), reverse = True)
			lista_punti_esterno_y = sorted(lista_punti_esterno, key=itemgetter(1), reverse = True)
			lista_punti_interno_x = sorted(lista_punti_interno, key=itemgetter(0), reverse = True)
			lista_punti_esterno_x = sorted(lista_punti_esterno, key=itemgetter(0), reverse = True)
		
			# Calcolo disallineamento verticale
			dis_sup = fabs(lista_punti_esterno_y[-1][0]-lista_punti_interno_y[-1][0])/xht
			dis_inf = fabs(lista_punti_esterno_y[0][0] -lista_punti_interno_y[0][0])/xht
			if verboso == 'yes':
				print "Disallineamento superiore della o:", dis_sup
				print "Disallineamento inferiore della o:", dis_inf
			sheet_out.write(row, 22, dis_sup)
			sheet_out.write(row, 23, dis_inf)
			out_cover.write("Disallineamento superiore della o: "+str(dis_sup)+'\n')
			out_cover.write("Disallineamento inferiore della o: "+str(dis_inf)+'\n')

		
			# Calcolo disallineamento orizzontale
			dis_des = fabs(lista_punti_esterno_x[0][1]-lista_punti_interno_x[0][1])/xht
			dis_sin = fabs(lista_punti_esterno_x[-1][1]-lista_punti_interno_x[-1][1])/xht
			if verboso == 'yes':
				print "Disallineamento destro della o:", dis_des
				print "Disallineamento sinistro della o:", dis_sin
			sheet_out.write(row, 24, dis_des)
			sheet_out.write(row, 25, dis_sin)
			out_cover.write("Disallineamento destro della o: "+str(dis_des)+'\n')
			out_cover.write("Disallineamento sinistro della o: "+str(dis_sin)+'\n\n')
		
			# Disomogeneità interna
			lista_dis_int = []
			count_dis = 0
			for item in lista_rich_int_sq:
				count_dis +=1
			
				if count_dis != 1:
					hnd_dis = item[1][0]-item_Prec[1][0]
					#print "Disomogeneità manipolatori contorno interno:", hnd_dis
					lista_dis_int.append(hnd_dis)
			
				# Tupla al ciclo precedente
				item_Prec = item
		
			# Disomogeneità esterna
			lista_dis_est = []
			count_dis = 0
			for item in lista_rich_est_sq:
				count_dis +=1
				if count_dis != 1:
					hnd_dis = item[1][0]-item_Prec[1][0]
					#print "Disomogeneità manipolatori contorno esterno:", hnd_dis
					lista_dis_est.append(hnd_dis)
			
				# Tupla al ciclo precedente
				item_Prec = item
			
			# Calcolo medie disomogeneità
			diso_int = (sum(lista_dis_int)/len(lista_dis_int))/xht
			diso_est = (sum(lista_dis_est)/len(lista_dis_est))/xht
			if verboso == 'yes':
				print "Disomogeneità media del contorno interno della o:", diso_int
				print "Disomogeneità media del contorno esterno della o:", diso_est
			sheet_out.write(row, 26, diso_int)
			sheet_out.write(row, 27, diso_est)
			out_cover.write("Disomogeneità media del contorno interno della o: "+str(diso_int)+'\n')
			out_cover.write("Disomogeneità media del contorno esterno della o: "+str(diso_est)+'\n')
		
			# Discontinuità interna
			# Manipolazione della lista per stabilire l'ordine corretto di calcolo
			first = lista_rich_int_sq.pop(0)
			lista_rich_int_sq.append(first)
		
			# Ciclo di calcolo interna
			lista_dis_int = []
			count_dis = 0
			for item in lista_rich_int_sq:
				count_dis +=1
			
				if count_dis != 1:
					hnd_dis = item[1][0]-item_Prec[1][0]
					#print "Disomogeneità manipolatori contorno interno:", hnd_dis
					lista_dis_int.append(hnd_dis)
			
				# Tupla al ciclo precedente
				item_Prec = item
				
			# Manipolazione della lista per stabilire l'ordine corretto di calcolo
			first = lista_rich_est_sq.pop(0)
			lista_rich_est_sq.append(first)
			
			# Ciclo di calcolo esterno
			lista_dis_est = []
			count_dis = 0
			for item in lista_rich_est_sq:
				count_dis +=1
				if count_dis != 1:
					hnd_dis = item[1][0]-item_Prec[1][0]
					#print "Disomogeneità manipolatori contorno esterno:", hnd_dis
					lista_dis_est.append(hnd_dis)
			
				# Tupla al ciclo precedente
				item_Prec = item
		
			# Calcolo medie discontinuità
			disc_int = (sum(lista_dis_int)/len(lista_dis_int))/xht
			disc_est = (sum(lista_dis_est)/len(lista_dis_est))/xht
			if verboso == 'yes':
				print "Discontinuità media del contorno interno della o:", disc_int
				print "Discontinuità media del contorno esterno della o:", disc_est
			sheet_out.write(row, 28, disc_int)
			sheet_out.write(row, 29, disc_est)
			out_cover.write("Discontinuità media del contorno interno della o: "+str(disc_int)+'\n')
			out_cover.write("Discontinuità media del contorno esterno della o: "+str(disc_est)+'\n\n')
		
		# Salvataggio dei file pdf e pulizia della tavola
		canvas.save('work/RoboAnalyzer - '+str(carattere)+' - '+str("%#04d" % count_variable)+'.pdf')
		canvas.clear()
	
	# Informazioni accessorie
	sheet_out.write(row, 30, sheet_info.cell(row_index, 3).value) # Designers
	sheet_out.write(row, 31, sheet_info.cell(row_index, 4).value) # URL designers
	
	# Print in output di data ed ora dello script
	sheet_out.write(row, 32, str(dh))
	out_cover.write("Data ed ora di esecuzione dello script: "+str(dh))

	# Chiusura del file output
	out_cover.close()

	# Realizzazione copertina
	fill(0)
	fontsize(18)

	# Legge il file txt di output
	in_file = open("work/data_cover.txt","r")
	text_values = in_file.read().decode('utf-8')
	in_file.close()
	os.remove("work/data_cover.txt")

	# Print sulla tavola del riassunto dei valori
	text(text_values, -100, -900)

	# Salvataggio copertina e pulizia della tavola
	canvas.save('work/0.pdf')
	canvas.clear()

	# Raccolta pagine singole pdf
	collect_pdf()

# Salvataggio file xls
book.save('misurazioni.xls')

de = dt.datetime.now()
print "End:", de
print "Durata script:", de-dh

	