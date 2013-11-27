"""
Copyright (c) 2013 - Roberto Arista (http://projects.robertoarista.it/) & ISIA Urbino (http://www.isiaurbino.net/home/)

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

### Modules
import robofab
from robofab.world import *
from robofab.interface.all.dialogs import Message, AskYesNoCancel, GetFolder
from robofab.pens.filterPen import flattenGlyph, _estimateCubicCurveLength, distance
from math import fabs, hypot, atan, degrees
from operator import itemgetter
import datetime
import string
import csv
import sys


### Class, functions and procedures
class typeStats:
    
    def __init__(self):
        return None
      
    # Start dialog  
    def startDialog(self):
        # Welcome message!
        Message("Hi! My name is typeStats.")
        
        # Mode
        verboso = AskYesNoCancel("Do you prefer the verbose mode?", title='typeStats', default=0)
        
        # Search path
        folder = GetFolder("Choose the directory to analyze")
        
        return folder, verboso
    
    # Reordering an iterable by occurrences
    def occurDict(self, items):
        d = {}
        for i in items:
            if i in d:
                d[i] = d[i]+1
            else:
                d[i] = 1
        return d
    
        
    # Creation of a Robofab font copy to work
    def stats_preparation(self, font):
        temp_font = font.copy()
        return temp_font
    
    # Segment slope 
    def angle_segment(self, punto1, punto2):
        if int(punto1[0]) != int(punto2[0]):
    		m = degrees(atan((-punto2[1]+punto1[1])/
    		                 (punto2[0]-punto1[0])))-90
    		
    		if -180 <= m < -90:
    			m = (m+180)
    		elif 180 >= m > 90:
    			m = (m-180)
    	else:
    		m = 0

    	return m
    
    	
    # Coordinates intersection bewtween two segments
    def intersect(self, pt1, pt2, pt3, pt4):
        try:
            denom = float((pt1.x-pt2.x)*(pt3.y-pt4.y)-
                          (pt1.y-pt2.y)*(pt3.x-pt4.x))
            x = ((pt1.x*pt2.y-pt1.y*pt2.x)*(pt3.x-pt4.x)-
                 (pt1.x-pt2.x)*(pt3.x*pt4.y-pt3.y*pt4.x))/denom
            y = ((pt1.x*pt2.y-pt1.y*pt2.x)*(pt3.y-pt4.y)-
                 (pt1.y-pt2.y)*(pt3.x*pt4.y-pt3.y*pt4.x))/denom
        except ZeroDivisionError:
            return
        return x, y
    
    
    # Points filter (mode == x, y, xy)
    def filter_points(self, glyph, mode):
        
        # Creation of an empty list
        list_points = []
        
        # Iteration over the glyph contours
        for con in glyph:
            
            # Iteration over glyph points
            for pt in con.points:
                
                # Points selection
                if pt.type != 'offCurve':
                    
                    # Filtering points
                    if mode == 'x':
                        list_points.append(pt.x)
                    
                    elif mode == 'y':
                        list_points.append(pt.y)
                    
                    elif mode == 'xy':
                        list_points.append((pt.x, pt.y))
                    
                    else:
                        print "There's an error!"
        
        return list_points
    
        
    # Copy the glyph and flat it
    def copyAndFlat(self, glyphName, font, precision):
        # Opening glyph
        glyph = font[glyphName]
        
        # Calling the layer
        glyph_flat = glyph.getLayer('flat', clear = False)
        
        # Copy and append
        glyph_matrix = glyph.copy()
        glyph_flat.appendGlyph(glyph_matrix)
        
        # Flattening
        flattenGlyph(glyph_flat, precision)
        
        return glyph_flat
    
    
    # Length of a contour    
    def contourLength(self, con):
        # empty list
        measures = [] 
        
        # First points
        begin = con.points[0]
        
        # Iteration over segments
        for seg in con:
            
            # Third degree curves calculation
            if len(seg.points) == 3:
                measure = _estimateCubicCurveLength((begin.x, begin.y), 
                                                   (seg[0].x, seg[0].y), 
                                                   (seg[1].x, seg[1].y), 
                                                   (seg[2].x, seg[2].y), 
                                                    precision=10)

                # First point progress
                begin = seg[2]
            
            elif len(seg.points) == 1:
                # Calculation of the length thanks to Pitagora
                measure = hypot((begin.x - seg[0].x), (begin.y - seg[0].y))
                                
                # First point progress 
                begin = seg[0]
                
            else:
                print "There's a problem!"
        
            # Lengths collection
            measures.append(measure)
        
        # Summation
        length = sum(measures)

        return length
    
        
    # Rectangles drawing procedure
    def rect(self, glyph, x_center, y_center, width, height):
        # Calling the pen
        pen = glyph.getPen()
        
        # drawing
        pen.moveTo((x_center-width/2.0, y_center+height/2.0))
        pen.lineTo((x_center+width/2.0, y_center+height/2.0))
        pen.lineTo((x_center+width/2.0, y_center-height/2.0))
        pen.lineTo((x_center-width/2.0, y_center-height/2.0))
        pen.lineTo((x_center-width/2.0, y_center+height/2.0))
        
        # Closing path
        pen.closePath()
        glyph.update()
        
    
    # Separation between internal and external contour of the 'o'
    def contours_separation(self, glyph):
        
        # Lengths calculation    
        contourLength_0 = self.contourLength(glyph[0])
        contourLength_1 = self.contourLength(glyph[1])
                
        # Leves creation
        external_level = glyph.getLayer('esterno', clear = True)
        internal_level = glyph.getLayer('interno', clear = True)
        
        # Moving contours
        if contourLength_0 > contourLength_1:
            external_level.appendContour(glyph[0])
            internal_level.appendContour(glyph[1])
            
        elif contourLength_0 < contourLength_1:
            external_level.appendContour(glyph[1])
            internal_level.appendContour(glyph[0])
        
        else:
            print "Error!"
            sys.exit()
        
        return internal_level, external_level
    

    # xHeight and XHeight calculation function
    def xHeight(self, font, case):
        
        # Calling the glyph
        if case == 'lowercase':
            x = font['x']
        elif case == 'uppercase':
            x = font['X']
        else:
            print "There's an error"
            sys.exit()
        
        # y values extraction
        list_y = self.filter_points(x, 'y')
        
        # multiples removal
        set_y = set(list_y)
        
        # Conversion to list and sorting
        list_y = list(set_y)
        list_y.sort()
        
        if (list_y[-1] - list_y[-2]) < 5:
            xHeight_lowercase = (list_y[-1] + list_y[-2])/2.0
        else:
            xHeight_lowercase = list_y[-1]
            
        # Visual check
        x_stats = x.getLayer('stats', clear = False)
        self.rect(x_stats, x_stats.width/2.0, xHeight_lowercase, x_stats.width, 2)
        
        return round(xHeight_lowercase, 0)
        

    # Weight calculation
    def weight(self, font, xHeight):
        
        # Calling the glyph
        l = font['l']
        
        # Copy and flat
        l_copy = self.copyAndFlat('l', font, 15)
        
        # Filtering points and rounding x values
        list_x = self.filter_points(l_copy, 'x')
        list_x = [round(x, 0) for x in list_x]

        # Creation of dictionary with the collection of list values with occurrences reordering
        occurrences = self.occurDict(list_x)
        dictionary_occurrences = sorted(occurrences.items(), key=itemgetter(1))
        
        # Calling the extremes values
        extreme_1 = dictionary_occurrences[-1][0]
        extreme_2 = dictionary_occurrences[-2][0]
        
        # weight calculation
        weight = round(fabs(extreme_2 - extreme_1)/xHeight, 4)
        
        # Visual check
        l_stats = l.getLayer('stats', clear = False)
        self.rect(l_stats, extreme_1-0.5, l.box[3]/2.0, 1, l.box[3])
        self.rect(l_stats, extreme_2-0.5, l.box[3]/2.0, 1, l.box[3])
        
        return weight
        
        
    # Contrast of 'o' thicknesses 
    def contrast(self, font):
        # Calling the glyph
        o = font['o']
        
        # Contours separation
        internal_level, external_level = self.contours_separation(o)
                
        # Flatting the level
        flattenGlyph(internal_level, 10)
        internal_points_number = len(internal_level[0])

        # External contour length
        external_length = self.contourLength(external_level[0])
        
        # External segment length
        d = external_length / internal_points_number
        
        # checked flattening
        flattenGlyph(external_level, d)
        
        # contour direction correction
        internal_level.correctDirection()
        external_level.correctDirection()
        
        # Correction starting points
        internal_level[0].autoStartSegment()
        external_level[0].autoStartSegment()
        
        # Contour condition
        if internal_level[0].clockwise == external_level[0].clockwise:
            pass
        else:
            print "There's an error!"
        
        # Checking the contour with less points
        if len(internal_level[0]) <= len(external_level[0]):
            len_min = len(internal_level[0])
        elif len(internal_level[0]) > len(external_level[0]):
            len_min = len(external_level[0])
        
        # Iteration over the number of contour points
        distances = []
        for i in range(len_min-1):
            
            # Points selection
            x1 = internal_level[0].points[i].x
            y1 = internal_level[0].points[i].y
            
            distances_detail = []
            for l in range(-3, 4): # Estrarre solo quello più corto
                
                # Indice di controllo
                index = i+l
                    
                if index >= len_min:
                    index = index-len_min
                
                x2 = external_level[0].points[index].x
                y2 = external_level[0].points[index].y
            
                # distance between points (Pitagora)
                distanza = hypot((x1-x2),(y1-y2))
                
                # Detail check
                distances_detail.append((((x1, y1), (x2, y2)), distanza))
            
            # Reordering details list
            distances_detail = sorted(distances_detail, key=itemgetter(1))
            
            # Collection of the shortest measure
            distances.append(distances_detail[0])
            
        # Reordering values list
        distances = sorted(distances, key=itemgetter(1))
        
        # Calling the shortest and the longest thickness
        shorter_thickness = distances[0][1]
        greater_thickness = distances[-1][1]
        
        # Contrast calculation
        contrast = shorter_thickness/greater_thickness
        
        # Slope shorter thickness calculation
        angle_min_thick = self.angle_segment(distances[0][0][0], distances[0][0][1])
        
        # Visual check
        o_stats = o.getLayer('stats', clear = False)
        self.rect(o_stats, distances[0][0][0][0], distances[0][0][0][1], 2, 2) # shortest
        self.rect(o_stats, distances[0][0][1][0], distances[0][0][1][1], 2, 2) # shortest
        self.rect(o_stats, distances[-1][0][0][0], distances[-1][0][0][1], 2, 2) # longest
        self.rect(o_stats, distances[-1][0][1][0], distances[-1][0][1][1], 2, 2) # longest

        return round(contrast, 2), int(round(angle_min_thick, 0))
    
    
    # Overshooting calculation   
    def overshooting(self, font, xHeight, position):
        # Calling the glyph
        o = font['o']
        
        # Filtering points
        lista_xy = self.filter_points(o, 'xy')
                    
        # Reordering by y values
        lista_xy = sorted(lista_xy, key=itemgetter(1))
        
        # Controlling positions and declaring variables
        if position == 'inferiore':
            extreme = lista_xy[0]
            overshooting = fabs(extreme[1])
            
        elif position == 'superiore':
            extreme = lista_xy[-1]
            overshooting = extreme[1] - xHeight
            
        else:
            print "There's an error"
            sys.exit()
            
        # Visual check
        o_stats = o.getLayer('stats', clear = False)
        
        if position == 'inferiore':
            self.rect(o_stats, o.width/2.0, -overshooting/2.0, o.width, overshooting)
        elif position == 'superiore':
            self.rect(o_stats, o.width/2.0, xHeight+overshooting/2.0, o.width, overshooting)
        
        return round(overshooting/xHeight, 4)
    
    
    # Ascenders calculation
    def ascenders(self, font, superior_overshooting, xHeight):
        
        # Calling the glyph
        f = font['f']
        
        # Filtering points (only y values)
        list_y = self.filter_points(f, 'y')
        
        # Sorting the points list
        list_y.sort(reverse=True)
        
        # Calculation
        ascenders = round((list_y[0]-superior_overshooting) /xHeight, 4)
        
        # Visual check    
        f_stats = f.getLayer('stats', clear = False)
        self.rect(f_stats, f.width/2.0, ascenders+superior_overshooting/2.0,f.width, superior_overshooting)
        self.rect(f_stats, f.width/2.0, ascenders/2.0, 2, ascenders) # Altezza ascendenti, senza overshooting
        
        return ascenders
    
    
    # Descenders calculation
    def descenders(self, font, xHeight):
        # Calling the glyph
        p = font['p']
        
        # Filtering the y values
        list_y = self.filter_points(p, 'y')
        
        # Multiples removal
        set_y = set(list_y)
        
        # Conversion to list and reordering
        list_y = list(set_y)
        list_y.sort(reverse = True)
        
        # Check if there's a serif
        if (list_y[-1] - list_y[-2]) < 5:
            descenders = (list_y[-1] + list_y[-2])/2.0
        else:
            descenders = list_y[-1]
            
        # Visual check
        p_stats = p.getLayer('stats', clear = False)
        self.rect(p_stats, p.width/2.0, descenders-1, p.width, 2)
        
        return round(descenders/xHeight, 4)
    
    
    # Lowercase 'n' expansion calculation     
    def exp_n(self, font, xHeight):
        # Calling the glyph
        n = font['n']
        
        # Flat copy 
        n_flat = self.copyAndFlat('n', font, 10)
        
        # Points x values
        list_x = self.filter_points(n_flat, 'x')
        
        # Collectiong by occurrences
        points_dictionary = self.occurDict(list_x)
        
        # Reordering the list
        x_values_reordered = sorted(points_dictionary.items(), key=itemgetter(1))
        
        # Stems extremes calling
        stem_extremes = x_values_reordered[-4:]
        
        # Riordinamento lista per valore di ascissa
        stem_extremes = sorted(stem_extremes, key=itemgetter(0))
        
        # Middle points
        left_middle_point = (stem_extremes[0][0] + stem_extremes[1][0])/2.0
        right_middle_point = (stem_extremes[2][0] + stem_extremes[3][0])/2.0
        
        # Expansion calculation
        expansion_n = right_middle_point - left_middle_point
        
        # Visual check
        n_stats = n.getLayer('stats', clear = False)
        
        # Middle points
        self.rect(n_stats, left_middle_point, n.box[3]/2.0, 2, 2) # Left
        self.rect(n_stats, right_middle_point, n.box[3]/2.0, 2, 2) # Right
        
        # Stem extremes
        self.rect(n_stats, stem_extremes[0][0], n.box[3]/3.0, 2, 2) 
        self.rect(n_stats, stem_extremes[1][0], n.box[3]/3.0, 2, 2)
        self.rect(n_stats, stem_extremes[2][0], n.box[3]/3.0, 2, 2)
        self.rect(n_stats, stem_extremes[3][0], n.box[3]/3.0, 2, 2)
        
        return round(expansion_n/xHeight, 4)
        
    
    # lowercase or uppercase 'o' expansion calculation
    def exp_o(self, font, case, xHeight):
        
        # Calling the right glyph
        if case == 'lowercase':
            o = font['o']
        elif case == 'uppercase':
            o = font['O']
        else:
            print "There's an error!"
            sys.exit()
        
        # Contours separation
        internal_level, external_level = self.contours_separation(o)
        
        # External contour points x values
        list_x_external = self.filter_points(external_level, 'x')
        
        # Internal contour points x values
        list_x_internal = self.filter_points(internal_level, 'x')
        
        # Lists reordering
        list_x_external.sort()
        list_x_internal.sort()
        
        # Middle points 
        left_middle_point = (list_x_internal[0] + list_x_external[0])/2.0
        right_middle_point = (list_x_internal[-1] + list_x_external[-1])/2.0
        
        # Expansion calculation
        expansion_o = round((right_middle_point - left_middle_point) / xHeight, 4)
        
        # Visual check
        o_stats = o.getLayer('stats', clear = False)
        
        # Middle points
        self.rect(o_stats, left_middle_point, o.box[3]/2.0, 2, 2)
        self.rect(o_stats, right_middle_point, o.box[3]/2.0, 2, 2)
        
        # Extremes
        self.rect(o_stats, list_x_internal[0], o.box[3]/3.0, 2, 2)
        self.rect(o_stats, list_x_external[0], o.box[3]/3.0, 2, 2)
        self.rect(o_stats, list_x_internal[-1], o.box[3]/3.0, 2, 2)
        self.rect(o_stats, list_x_external[-1], o.box[3]/3.0, 2, 2)
        
        return expansion_o
    
    
    # 'R' expansion    
    def exp_R(self, font, xHeight):
                
        # Calling the glyph
        R = font['R']
        
        # Contours separation (internal, external)
        internal_level, external_level = self.contours_separation(R)
        
        # Flattening contours
        flattenGlyph(internal_level, 10)
        flattenGlyph(external_level, 10)

        # Filtering x values
        left_stem_x_values = self.filter_points(external_level, 'x')
        right_stem_x_values = self.filter_points(internal_level, 'x')
        
        # Left middle points, occurrences collection
        left_stem_x_values = self.occurDict(left_stem_x_values)
        right_stem_x_values = self.occurDict(right_stem_x_values)
        
        # Left middle points, reordering occurrences
        left_stem_x_values = sorted(left_stem_x_values.items(), key=itemgetter(1), reverse = True)
        right_stem_x_values = sorted(right_stem_x_values.items(), key=itemgetter(1), reverse = True)
        
        # Left middle point, x value
        left_middle_point = (left_stem_x_values[0][0] + right_stem_x_values[0][0])/2.0
        
        # Right middle point
        left_bowl_x_values = self.filter_points(internal_level, 'x')
        right_bowl_x_values = self.filter_points(external_level, 'xy')
        
        # Right middle point, extreme internal
        left_extreme = max(left_bowl_x_values)
        
        # extreme superior
        right_bowl_x_values = sorted(right_bowl_x_values, key=itemgetter(1), reverse=True)
        extreme_superior = right_bowl_x_values[0][1]
        
        # Filtering the upper half of the glyph
        right_bowl_x_values = [item for item in right_bowl_x_values if item[1] >= extreme_superior/2.0]
        
        # x values reordering
        right_bowl_x_values = sorted(right_bowl_x_values, key=itemgetter(0), reverse=True)
        
        # Bowl right extreme
        right_extreme = right_bowl_x_values[0][0]
        
        # Right middle point
        right_middle_point = (right_extreme + left_extreme)/2.0

        # 'R' expansion
        expansion_R = right_middle_point - left_middle_point
        
        # Visual check
        R_stats = R.getLayer('stats', clear = False)
        
        # Middle points
        self.rect(R_stats, left_middle_point, R.box[3]/1.5, 2, 2)
        self.rect(R_stats, right_middle_point, R.box[3]/1.5, 2, 2)
        
        # Extremes
        self.rect(R_stats, left_extreme, R.box[3]/2.0, 2, 2)
        self.rect(R_stats, right_extreme, R.box[3]/2.0, 2, 2)
        self.rect(R_stats, left_stem_x_values[0][0], R.box[3]/2.0, 2, 2)
        self.rect(R_stats, right_stem_x_values[0][0], R.box[3]/2.0, 2, 2)
        
        return round(expansion_R/xHeight, 4)
        
        
    # H height calculation (no xHeight ratio)
    def Hheight(self, font):
    
        # Calling the glyph
        H = font['H']
        
        # y values filtering
        list_y = self.filter_points(H, 'y')
        
        # Multiples removal
        set_y = set(list_y)
        
        # Conversion to list and reordering
        list_y = list(set_y)
        list_y.sort()
        
        if (list_y[-1] - list_y[-2]) < 5:
            Hheight = (list_y[-1] + list_y[-2])/2.0
        else:
            Hheight = list_y[-1]
            
        # Visual check
        H_stats = H.getLayer('stats', clear = False)
        self.rect(H_stats, H_stats.width/2.0, Hheight, H_stats.width, 2)
        
        return Hheight


    def stemHheight(self, font, altezzaH):
        
        # Calling the glyph
        H = font['H']
        
        # Copy and flat
        H_flat = self.copyAndFlat('H', font, 10)
        
        # Filter points coordinates
        list_xy = self.filter_points(H_flat, 'xy')
        
        # Points filtering
        list_xy = [xy for xy in list_xy if xy[1] > altezzaH/6.0] # Removing inferior 1/5
        list_xy = [xy for xy in list_xy if xy[1] < altezzaH-altezzaH/6.0] # Removing superior 1/5 
        list_y = [round(xy[1], 0) for xy in list_xy] # Removing x values
        
        # Collecting occurrences
        points_dictionary = self.occurDict(list_y)
        
        # Reordering occurrences
        occurrences_list = sorted(points_dictionary.items(), key=itemgetter(1), reverse = True)
        
        # Calling extremes
        extreme1, extreme2 = occurrences_list[0][0], occurrences_list[1][0]
                
        # Horizontal stem middle point
        stemHheight = (extreme1 + extreme2)/2.0
        
        # Visual check
        H_stats = H.getLayer('stats', clear = False)
        self.rect(H_stats, H.box[2]/2.0, stemHheight, H.width, 2)
        
        return round(stemHheight/altezzaH, 4)
    
    
    # Optical horizontal center calculation
    def Tmiddle(self, font):
        
        # Calling the glyph
        T = font['T']
        
        # Copy and flat
        T_flat = self.copyAndFlat('T', font, 5)
        
        # Filtering the x values
        list_x = self.filter_points(T_flat, 'x')
        
        # Collectiog occurrences
        points_dictionary = self.occurDict(list_x)
        
        # Reordering occurrences
        occurrences_list = sorted(points_dictionary.items(), key=itemgetter(1), reverse = True)
        
        # Stem extremes
        extremes = [item[0] for item in occurrences_list[0:4]] 
        
        # Sorting coordinates
        extremes.sort()
        
        # Central stem middle point
        punto_medio = (extremes[1] + extremes[2])/2.0
        Tmiddle  = punto_medio/T_flat.width
        
        # X axis projections length
        T_left_projection = extremes[1] - extremes[0]
        T_right_projection = extremes[3] - extremes[2]
                
        # Symmetry check
        if -1 <= (T_left_projection - T_right_projection) >= 1: # Minimum difference for asymmetry --> 2
            symmetry = True
        else:
            symmetry = False
            
        # Visual check
        T_stats = T.getLayer('stats', clear = False)
        self.rect(T_stats, extremes[0], T.box[3]/2.0, 2, T.box[3])
        self.rect(T_stats, extremes[1], T.box[3]/2.0, 2, T.box[3])
        self.rect(T_stats, extremes[2], T.box[3]/2.0, 2, T.box[3])
        self.rect(T_stats, extremes[3], T.box[3]/2.0, 2, T.box[3])
              
        return round(Tmiddle, 4), round(T_left_projection, 0), round(T_right_projection, 0), symmetry
        
    
    # Squaring value of a contour calculation
    def contour_squaring(self, check_glyph, con):
        # Empty squaring list
        squaring_list = []
                    
        # Contour starting point
        pt0 = con.points[0]
                
        # Iteration over contour segments
        for seg in con:
            
            # Check line presence
            if not (seg.type != 'curve'  or seg.type != 'qcurve'):
                print seg.type
                print "Why is there a line?"
                sys.exit()
                
            else:
                curve_type = seg.type
                pt1 = seg.points[0]
                pt2 = seg.points[1]
                pt3 = seg.points[2]
                
                # bcp intersection
                intersection = self.intersect(pt0, pt1, pt2, pt3)
                
                # Visual check intersections
                self.rect(check_glyph, intersection[0], intersection[1], 2, 2)
            
                # Squaring value calculation and average of the two
                sq1 = distance((pt0.x, pt0.y), (pt1.x, pt1.y)) / distance((pt0.x, pt0.y), intersection)
                sq2 = distance((pt3.x, pt3.y), (pt2.x, pt2.y)) / distance((pt3.x, pt3.y), intersection)
                sq_avg = (sq1+sq2)/2.0
                
                # Collection squaring values
                squaring_list.append(sq_avg)
                
                # Starting point at the end of the cycle
                pt0 = pt3
            
        # Mean of all the squaring values
        sq_contorno = sum(squaring_list)/len(squaring_list)
            
        return round(sq_contorno, 4), curve_type
        
    
    # 'o' squaring calculation
    def squaring_o(self, font):
        
        # Calling the glyph
        o = font['o']
        
        # Contour separation
        internal_level, external_level = self.contours_separation(o)
        
        # Squaring calculation
        check_glyph = o.getLayer('squadratura', clear = False)
        internal_squaring, curve_type = self.contour_squaring(check_glyph, internal_level[0])
        external_squaring = self.contour_squaring(check_glyph, external_level[0])[0]
        
        # Dichiarazione variabili
        mean_squaring = (external_squaring + internal_squaring)/2.0
        
        return round(mean_squaring, 4), round(internal_squaring, 4), round(external_squaring, 4), curve_type
      
        
    # Function able to check the presence of serifs
    def serif_sniffer(self, font, xHeight):
        
        # Calling the glyph
        i = font['i']
        
        # Copy and flat
        i_flat = self.copyAndFlat('i', font, 2)
        
        # Filtering points
        list_xy = self.filter_points(i_flat, 'xy')
        
        # Inferior half points of the glyph
        list_xy_down = [coo for coo in list_xy if coo[1] < xHeight/2.0]
        
        # Selezione delle ascisse
        list_x = [round(coo[0]) for coo in list_xy_down]

        # Collecting occurrences
        occurrences = self.occurDict(list_x)
        
        # Reordering occurrences
        dictionary_occurrences = sorted(occurrences.items(), key=itemgetter(1))
        
        # Filtering and reordering
        extremes = dictionary_occurrences[-2:]
        extremes = [item[0] for item in extremes]
        extremes.sort()
        
        # Calling the extremes
        extreme_1 = extremes[-1]
        extreme_2 = extremes[-2]
        
        # Calling variables
        right = False
        left = False
        
        for abscissa in list_x:
            if abscissa >=  extreme_1+20:
                right = True
            if abscissa <=  extreme_2-20:
                left = True
        
        if right == True and left == True:
            serif_style = 'Serif'
        else:
            serif_style = 'Sans'
        
        return serif_style
        
        
    # Proportional or monospaced
    def width_sniffer(self, font):
        
        # Empty list
        widths = []
        
        # Iteration over lowercase alphabet
        for glyphName in string.lowercase:
            glyph = font[glyphName]
            
            # Collecting values
            widths.append(glyph.width)
        
        if len(set(widths)) <= 1:
            width_style = 'Mono'
        else:
            width_style = 'Proportional'
        
        return width_style
        

### Instructions
# Date and time
ts = datetime.datetime.now()
print "Start:", ts

# Calling the class
stats = typeStats()

# Variables dialog
input_path, verboso = stats.startDialog()

# Opening the csv file
csvfile = open('typeStatsDB.csv', 'wb')
statsWriter = csv.writer(csvfile)

# Columns headings
statsWriter.writerow(['familyName', 
                      'styleName', 
                      'xHeight', 
                      'capHeight', 
                      'weight',
                      'contrast',
                      'shortestThickSlope', 
                      'superiorOvershooting',
                      'inferiorOvershooting',
                      'ascenders',
                      'descenders',
                      "n_expansion",
                      "o_expansion",
                      "no_ratio",
                      "O_expansion",
                      "R_expansion", 
                      "RO_ratio", 
                      "Hheight",
                      "H_horizontalStemMiddlePoint",
                      "T_verticalStemMiddlePoint",
                      "T_stemLeftProjection",
                      "T_stemRightProjection",
                      "T_projectionsSymmetry",
                      "o_averageSquaring",
                      "o_internalSquaring",
                      "o_externalSquaring",
                      "bezierType",
                      "Serifs",
                      "spacing"])


# Iteration over the folder tree
for root, dirnames, filenames in os.walk(input_path):
    
    # Iteration over folders
    for dirname in dirnames:
        
        # Check file opening
        if dirname.endswith('.ufo') and '_typeStats' not in dirname:
            
            # Conditional statement on dirname
            if ('italic' in dirname or 'Italic' in dirname or 'oblique' in dirname or 'Oblique' in dirname):
                continue
            
            # Apertura del carattere
            font = OpenFont(root+os.path.sep+dirname, showUI = False)
            
            # Conditional statement on font.info.styleName
            if ('italic' in font.info.styleName or 'Italic' in font.info.styleName or 'Oblique' in font.info.styleName or 'oblique' in font.info.styleName):
                continue
                
            print "Path: ", root+os.path.sep+dirname

            # Preparing measuration, copy the font!
            temp_font = stats.stats_preparation(font)
            temp_font.save(root+os.path.sep+dirname[:-4]+'_typeStats.ufo')
            
            try:
                # xHeight
                xHeight = stats.xHeight(temp_font, 'lowercase')
                if verboso is True: print "xHeight:", xHeight

                # XHeight 
                capHeight = round(stats.xHeight(temp_font, 'uppercase')/xHeight, 4)
                if verboso is True: print "capHeight:", capHeight

                # Weight 
                weight = stats.weight(temp_font, xHeight)
                if verboso is True: print "Weight:", weight

                # Typeface contrast and minor thickness slope
                contrast_tuple = stats.contrast(temp_font)
                contrast = contrast_tuple[0]
                angle_min_thick = contrast_tuple[1]
                if verboso is True: print "Contrast:", contrast
                if verboso is True: print "Shortest thickness slope:", angle_min_thick

                # Superior overshooting
                superior_overshooting = stats.overshooting(temp_font, xHeight, 'superiore')
                if verboso is True: print "Superior overshooting: ", superior_overshooting

                # Inferior overshooting
                inferior_overshooting = stats.overshooting(temp_font, xHeight, 'inferiore')
                if verboso is True: print "Inferior overshooting: ", inferior_overshooting

                # Ascnders
                ascenders = stats.ascenders(temp_font, superior_overshooting, xHeight)
                if verboso is True: print "Ascenders: ", ascenders

                # Descenders
                descenders = stats.descenders(temp_font, xHeight)
                if verboso is True: print "Descenders: ", descenders

                # Calcolo dell'espansione della 'n'
                n_expansion = stats.exp_n(temp_font, xHeight)
                if verboso is True: print "n expansion: ", n_expansion

                # Calcolo dell'espansione della 'o'
                o_expansion = stats.exp_o(temp_font, 'lowercase', xHeight)
                if verboso is True: print "o expansion: ", o_expansion

                # n/o expansion ratio
                no_ratio = round(n_expansion / o_expansion, 2)
                if verboso is True: print "Rapporto no: ", no_ratio

                # Calcolo dell'espansione della 'O'
                O_expansion = stats.exp_o(temp_font, 'uppercase', xHeight)
                if verboso is True: print "O expansion: ", O_expansion

                # Calcolo dell'espansione della 'R'
                R_expansion = stats.exp_R(temp_font, xHeight)
                if verboso is True: print "R expansion: ", R_expansion

                # Rapporto di espansione RO
                RO_ratio = round(R_expansion / O_expansion, 2)
                if verboso is True: print "RO ratio: ", RO_ratio

                # measurezione dell'altezza dell'H
                H_height = stats.Hheight(temp_font)
                if verboso is True: print "H height: ", H_height
        
                # measurezione del punto centrale verticale dell'asta dell'H
                H_StemMiddlePoint = stats.stemHheight(temp_font, H_height)
                if verboso is True: print "H horizontal stem middle points: ", H_StemMiddlePoint

                T_stemMiddlePoint, T_left_projection, T_right_projection, T_projectionsSymmetry = stats.Tmiddle(temp_font)
                if verboso is True: print "T vertical stem middle point: ", Tmiddle
                if verboso is True: print "T left and right projections: ", T_left_projection, T_right_projection
                if verboso is True: print "T left and right projections symmetry: ", T_projectionsSymmetry

                # o squaring
                squaring_o, squaring_int_o, squaring_est_o, curve_type = stats.squaring_o(temp_font)
                if verboso is True: print "o average squaring: ", squaring_o
                if verboso is True: print "o internal squaring: ", squaring_int_o
                if verboso is True: print "o external squaring: ", squaring_est_o
                if verboso is True: print "bezier Type: ", curve_type

                # Serifs presence
                serifs = stats.serif_sniffer(temp_font, xHeight)
                if verboso is True: print "Serifs presence: ", serifs

                # Tipologia di spaziatura
                width = stats.width_sniffer(temp_font)
                if verboso is True: print "Spacing: ", width
                if verboso is True: print

                # Salvataggio della font con i parametri di measurezione
                temp_font.save(root+os.path.sep+dirname[:-4]+'_typeStats.ufo')
        
                # Writing data on csv file
                statsWriter.writerow([string.capwords(temp_font.info.familyName.replace('Std', '')), 
                                      string.capwords(temp_font.info.styleName),
                                      xHeight,
                                      capHeight,
                                      weight,
                                      contrast,
                                      angle_min_thick,
                                      superior_overshooting,
                                      inferior_overshooting,
                                      ascenders,
                                      descenders,
                                      n_expansion,
                                      o_expansion,
                                      no_ratio,
                                      O_expansion,
                                      R_expansion,
                                      RO_ratio,
                                      H_height,
                                      H_StemMiddlePoint,
                                      T_stemMiddlePoint,
                                      T_left_projection,
                                      T_right_projection,
                                      T_projectionsSymmetry,
                                      squaring_o,
                                      squaring_int_o,
                                      squaring_est_o,
                                      curve_type,
                                      serifs,
                                      width])
                
            except:
                print "Error: ", sys.exc_info()[1]
                print "Line number: ", sys.exc_traceback.tb_lineno 

# Saving/closing csv file
csvfile.close()

# Script timing
te = datetime.datetime.now()
print
print "End script:", te    
print "Duration:", te-ts
