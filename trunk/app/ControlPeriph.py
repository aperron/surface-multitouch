#!/usr/bin/python
# -*- coding: utf-8 -*-
#

###
#	ControlPeriph -- 
#
#	Copyright (c) 2009-2010 MESTRE Charles
#
#	Permission is hereby granted, free of charge, to any person obtaining
#	a copy of this software and associated documentation files
#	(the "Software"), to deal in the Software without restriction,
#	including without limitation the rights to use, copy, modify, merge,
#	publish, distribute, sublicense, and/or sell copies of the Software,
#	and to permit persons to whom the Software is furnished to do so,
#	subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be
#	included in all copies or substantial portions of the Software.
#
#	Any person wishing to distribute modifications to the Software is
#	requested to send the modifications to the original developer so that
#	they can be incorporated into the canonical version.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#	IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
#	ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#	CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#	WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###

import sys
import os

# Change path so we find Xlib
#sys.path.insert(1, os.path.join(sys.path[0], '..'))
from time import localtime
import Xlib.display
import Xlib.ext.xtest
import time
########### variables globales ##########################
#infos utiles
coef_xy =[1.,1.] #x,y
buffer_tp = [0, 0, 0, 0]  #temp, x precedent, y precedent, premier appel
largeur_cam=0

#Parametres
tolerence_click = [5] #distance dans laquelle on considere le doigt static
temps_click = [3] #temps pendant lequel l'objet doit etre static pour cliquer

class MouseControl:
    
           #Initialisation
    def __init__(self, largeur_cam, hauteur_cam):
        largeur_cam=largeur_cam
        self.display = Xlib.display.Display()
        self.screen = self.display.screen()
        self.root = self.screen.root
        largeur_ecran, hauteur_ecran = self.get_screen_resolution() #Recuperation de la resolution du projecteur
        self.mise_echelle(largeur_ecran, hauteur_ecran, largeur_cam, hauteur_cam) #Mise a l'echelle projecteur/surface
        print""
        print "coef_x "+str(coef_xy[0]) + " coef_y " +str(coef_xy[1])
        print""
        print"largeur_cam "+str(largeur_cam)+" hauteur_cam " + str(hauteur_cam)
        print"largeur_ecran " + str(largeur_ecran) + " hauteur_ecran " + str(hauteur_ecran)
        print""

    def mouse_warp(self, x, y, offsetx, offsety):
        x=abs(largeur_cam-x)#abs(y-hauteur_cam)
        print x, y
        self.root.warp_pointer(((x*coef_xy[0])+offsetx),((y*coef_xy[1])+offsety))
        self.display.sync()
        if(buffer_tp[3]==0): #premier static potentiel
            buffer_tp[3]=1
            buffer_tp[0]=localtime()[5]
            buffer_tp[1]=x
            buffer_tp[2]=y
            
        else:
            if not(self.eststatique(x, y)):
                buffer_tp[0]=localtime()[4]
                buffer_tp[1]=x
                buffer_tp[2]=y
                
                
            else:
               # print localtime()[5], temps_click
               # print buffer_tp[0]
                if ((localtime()[5]-buffer_tp[0] >=temps_click[0]) or (localtime()[5]-buffer_tp[0])<0):
                    self.mouse_click( 1)
                    buffer_tp[3]=0
                
                
        
        


    def get_screen_resolution(self):
        return self.screen['width_in_pixels'], self.screen['height_in_pixels']


    def mouse_click(self, button): #Le clic souris est constitue d'un appui puis d'un relachement
        self.mouse_down(button)
        self.mouse_up(button)
        print"clic!"
        
    def mouse_down(self, button): #button= 1 left, 2 middle, 3 right
        Xlib.ext.xtest.fake_input(self.display,Xlib.X.ButtonPress, button)
        self.display.sync()
 
    def mouse_up(self, button):
        Xlib.ext.xtest.fake_input(self.display,Xlib.X.ButtonRelease, button)
        self.display.sync() 
        
    def mise_echelle(self,  widthscreen,  heightscreen,  widthcam, heightcam):
        coef_xy[0], coef_xy[1] = float(widthscreen) / float(widthcam),  float(heightscreen) / float(heightcam)

   
    
    def eststatique(self, x, y): # Pour savoir si l'objet est statique on test si son déplacement est bien inferieur
        test =((((x-buffer_tp[1])**2+(y-buffer_tp[2])**2)**0.5) < (tolerence_click))# A la tolerence donne
     #   print "test" + str(test)
        return test
#x=0
#y=0

#souris = MouseControl(240, 320)

#for x in range (1):
#    time.sleep(1)
#    MouseControl.mouse_warp(souris, 150, 150, 0, 0)
#    time.sleep(4)
#    print buffer_tp[0:3]
#    print"attention"
#    MouseControl.mouse_warp(souris, 150, 150, 0, 0)
#    print buffer_tp[0:3]
#    time.sleep(2)
#    MouseControl.mouse_warp(souris, 130, 120, 0, 0)
#    print buffer_tp[0:3]
#    time.sleep(2)
#    MouseControl.mouse_warp(souris, 130, 170, 0, 0)
#    print buffer_tp[0:3]
#    time.sleep(2)
#    MouseControl.mouse_warp(souris, 120, 200, 0, 0)
#    print buffer_tp[0:3]
#    time.sleep(2)
#    MouseControl.mouse_warp(souris, 110, 150, 0, 0)

