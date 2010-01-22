#! /usr/bin/python
# -*- coding: utf-8 -*-


###
#	fingerTracker -- Develop for FTIR technology
#
#	Copyright (c) 2009-2010 PERRON Anthony <anthony-perron@hotmail.fr>
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

# import the necessary things for OpenCV
from opencv import cv
from opencv import highgui

from ControlPeriph import *
import Xlib.display

#import TuioServerModule
import time

################################### UTILISATION CLASSIQUE ############################
## 1 - lancer le programme : > python fingerTracker.py (-h pour voir les options)
## 2 - regler les parametres pour une detection optimale.  (cf : trackbar + touche 'b' pour rafraichir la suppression du background)
## 3 - touche 's' pour sauver la configuration (cf : background.bmp et config)
## 4 - relancer le programme avec l'option -noGUI => le programme est lance sans interface graphique
############################################################################

##################################A FAIRE######################################
##      * inertie des pointeurs pr identitePointeur => ne pas changer pour rien d id
##      * meilleur init pr appeler identitePointeur  
##      * qd aucun point pdt un certain tps remise a zero des infos sur les pointeurs
##
#############################################################################
# definition of some constants
color = cv.CV_RGB(0,255,255);##bleu claire
color2= cv.CV_RGB(0,0,255);##bleu fonce
critere=cv.CvTermCriteria()                                                 ## utils for cvMeanShift  cvCamshift
critere.type=cv.CV_TERMCRIT_ITER+cv.CV_TERMCRIT_EPS;                        ##
critere.epsilon=0.0;                                                        ##

#  ########  parametre de reglage ########  #
nb_div_zone=[4]; ## nbr_div_zone fois divise en quatre cf : trackbar
seuil_binary=[254]; ## seuil utiliser pour binariser l image cf : trackbar
gain=[3]; ## amplification de l'image
param_liss=[3]; ## lissage
param2_liss=[1]; ## lissage
image_par_image=0;## if =1 : 'n' to go to the next frame
GUI=1; ## if =0 hide windows, cf : command arg -noGui

# ######## infos utils ########  #
hauteur_image=0;
largeur_image=0;
zone_active=[]
pointeur=[] ## pointeur[0]=centrePointeur  ,  pointeur[1]=info_size des pointeurs
centrePointeur=[]  ## liste de cvPoint
info_size=[]
id_Pointeur=[]
prec_time =[time.time()]  ## utils pour sendTuioMess()
prec_centrePointeur=[]     ## utils pour identitePointeur()
prec_info_size=[]
prec_id_Pointeur=[]                   ##
id_abs=[-1]
#############################################################################
# some useful functions
def set_nb_div(position):
        nb_div_zone[0]=position

def get_nb_div():
    return nb_div_zone[0]

def set_seuil(position):
    seuil_binary[0]=position

def get_seuil():
    return float(seuil_binary[0])

def set_gain(position):
    gain[0]=position

def get_gain():
    return float(gain[0])

def set_param_liss(position):
    param_liss[0]=position;
    
def set_param2_liss(position):
    param2_liss[0]=position;

def init_cam(width=320, height=240):
    capture = highgui.cvCreateCameraCapture (0)
    highgui.cvSetCaptureProperty (capture,highgui.CV_CAP_PROP_FRAME_WIDTH, int(width))
    highgui.cvSetCaptureProperty (capture,highgui.CV_CAP_PROP_FRAME_HEIGHT, int(height))
    return capture
    
def zoneActivePremier(zone_active, framebuffer):
    critere.max_iter=1
    zone_active=[]
    zone = cv.cvRect(0, 0,largeur_image/2, hauteur_image/2);
    for x in range(0,largeur_image,largeur_image/2) :
        for y in range(0, hauteur_image, hauteur_image/2):
            zone.x=x ; zone.y=y;
            trouver = cv.cvMeanShift(framebuffer,zone, critere, cv.CvConnectedComp())
            if trouver!=0 :
                zone_active+=[cv.cvRect(x,y,largeur_image/2, hauteur_image/2) ]
    #print "zoneActivePremier() a trouver "+str(len(zone_active))+" zone active"
    return zone_active

def zoneActive(zone_active, framebuffer, iteration):
    critere.max_iter=5
    hauteur=hauteur_image/pow(2, iteration+1)
    largeur=largeur_image/pow(2, iteration+1)
    for i in range(0, len(zone_active)):        
        zone = cv.cvRect(zone_active[i].x, zone_active[i].y, largeur ,hauteur);
        origine_x_zone=zone_active[i] .x; origine_y_zone =zone_active[i].y;
        index=0
        for x in range(origine_x_zone,origine_x_zone+(largeur*2),largeur) :
                for y in range(origine_y_zone, origine_y_zone+ (hauteur*2), hauteur):
                    zone.x=x ; zone.y=y; trouver=0;
                    trouver = cv.cvMeanShift(framebuffer,zone, critere, cv.CvConnectedComp())
                    if trouver!=0 :
                        #cv.cvRectangle(frame, cv.cvPoint(x,y), cv.cvPoint((x+largeur), (y+hauteur)), color)
                        if  index==0:
                            zone_active[i]=cv.cvRect(x,y,largeur, hauteur) 
                        else:
                            zone_active+=[cv.cvRect(x,y,largeur, hauteur) ]
                        index=index+1
    return zone_active

    
def pointeurPrecision(zone_active, framebuffer):
    info_size=[];  centre=[];
    for i in range(0, len(zone_active)):
        conteneur=cv.CvConnectedComp()
        info = cv.CvBox2D()
        trouver=cv.cvCamShift(framebuffer,zone_active[i], critere, conteneur, info)
        info_size.append(info.size.height*info.size.width)
        centre.append(cv.cvPoint(int(info.center.x), int(info.center.y)))
        #***** possibilite de recuperer l angle *****#
    return [centre , info_size]

def FiltreRedondance(centre, info_size):
    i=0
    while i<len (centre):
        j=i+1
        dist=(info_size[i] / 3.14)**0.5 ; #rayon de la tache detecte (considerer comme un cercle)
        while j <len(centre):
            if abs(  ( (centre[i].x - centre[j].x)**2   +  (centre[i].y - centre[j].y)**2  )**0.5 ) < dist:
                del centre[j]
                del info_size[j]
            else:
                j=j+1
        i=i+1
    return [centre, info_size]


def printListPointeur(list):
    for i in range(0, len(list)):
        print "pointeur "+str(i)+" x:" +str(list[i].x)+ " y:"+str(list[i].y)
    print ""

def sendTuioMess():
    for i in range(0, len(centrePointeur)):
        run=0
        if (i==(len(centrePointeur))-1):
            run=1
        dt = abs(time.time() - prec_time[0])
        x_relative= float(centrePointeur[i].x) / float(largeur_image)
        y_relative = float(centrePointeur[i].y) / float(hauteur_image)
        
        #X_speed = (x_relative -prec_x_relative)/ dt
        #Y_speed  = (y_relative - prec_y_relative)/ dt
        #m = (    ( X_speed**2 + Y_speed**2 ) **0.5  -  ( prec_X_speed**2 + prec_Y_speed**2 ) **0.5   ) / dt
        indice=0;
        if (TuioServerModule.isMessageFull()==1):
            TuioServerModule.move( run, id_Pointeur[i] ,  x_relative , y_relative  , float(0), float(0) , float(0) ) ;
            TuioServerModule.CursorAlive(run,  id_Pointeur[i] , i);
        else:
            print "Tuio Message is full"
        #print "cursor "+str(i)+" x:"+str(x_relative) +" y:"+str(y_relative) #+ " X: " +str(X_speed)+ " Y: " +str(Y_speed)+ " m: " +str(m)
        prec_time [0]= time.time()   
        #(run,id,x,y,X,Y,m)   
        #run (int): lance l envoie du message ;  id(int):identite ; 
        #x et y (float 0<1)du point ; 
        #X (float): acceleration sur axe x; m (float)acceleration
    
def identitePointeur(centrePointeur, prec_centrePointeur, id_Pointeur,prec_id_Pointeur,  info_size):
    id_Pointeur=[]
    for i in range(0, len(centrePointeur)):
        id_Pointeur.append(-1)
    
    i=0
    while i<len (centrePointeur):
        j=0
        dist=(info_size[i] / 3.14)**0.5 ; #rayon tache detect
        while j <len(prec_centrePointeur):
            
            if abs(  ( (centrePointeur[i].x - prec_centrePointeur[j].x)**2   +  (centrePointeur[i].y - prec_centrePointeur[j].y)**2  )**0.5 ) < dist:
                #print "i:"+str(i)+" j:"+str(j)
                #if j==len(prec_id_Pointeur):
                #    prec_id_Pointeur.append(id_Pointeur[i])
                #else:
                if j<len(prec_id_Pointeur):
                    id_Pointeur[i]=prec_id_Pointeur[j]
            j=j+1
        i=i+1
    for i in range(0, len(centrePointeur)):
        if id_Pointeur[i]==-1:
            id_abs[0]=id_abs[0]+1
            id_Pointeur[i] = id_abs[0]
    
    return id_Pointeur
    
    
#############################################################################
# so, here is the main part of the program

if __name__ == '__main__':
    
    #######################CHECK COMMAND ARGS +  OPEN SOURCE ########################
    capture=None
    if len (sys.argv) == 1:
        capture=init_cam()
    else:
        for i in range (1, len(sys.argv)) :
            if sys.argv[i]=="-h" or sys.argv[i]=="--help" :
                print """usage : multitouch [option]
    option:
        -h  | --help                            show help
        -f  | --file    <path>                  open file (no cam)
        -s  | --size    <width><height>         param of cam
        --noGUI                                dont show windows
        
        attention a l ordre des arguments
                
                """
                sys.exit (1)
            elif sys.argv[i]=="-s" or sys.argv[i]=="--size" :
                capture=init_cam(sys.argv[i+1], sys.argv[i+2])
                i=i+2
            elif sys.argv[i]=="-f" or sys.argv[i]=="--file" :
                capture = highgui.cvCreateFileCapture (str(sys.argv[i+1]))
                i=i+1
            elif sys.argv[i]=="--noGUI":
                GUI =0
                capture=init_cam()
                i=i+1
            elif sys.argv[i]=="--fps":
                capture=init_cam()
                highgui.cvSetCaptureProperty (capture,highgui.CV_CAP_PROP_FPS, int(sys.argv[i+1]))
                i=i+1
    # check that capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit (1)
    
    # Load config 
    frameGrayBg = highgui.cvLoadImage("background.bmp", highgui.CV_LOAD_IMAGE_GRAYSCALE)
    logfile = open('config', 'r') 
    nb_div_zone[0] = int (logfile.readline())
    seuil_binary[0]= int (logfile.readline())
    gain[0]= int (logfile.readline())
    param_liss[0]= int (logfile.readline())
    param2_liss[0]= int (logfile.readline())
    logfile.close()
    
    # a small welcome
    print "OpenCV Python - multitouch"
    print "OpenCV version: %s (%d, %d, %d)" % (cv.CV_VERSION,cv.CV_MAJOR_VERSION,cv.CV_MINOR_VERSION,cv.CV_SUBMINOR_VERSION)
    
    ############################ GUI Config #####################################
    if GUI==1:
        
    
        # first, create the necessary windows
        highgui.cvNamedWindow ('Camera', highgui.CV_WINDOW_AUTOSIZE)
        highgui.cvNamedWindow ('Originale', highgui.CV_WINDOW_AUTOSIZE)
        highgui.cvNamedWindow ('Binarisation', highgui.CV_WINDOW_AUTOSIZE)
        highgui.cvNamedWindow ('1-without background', highgui.CV_WINDOW_AUTOSIZE)
        highgui.cvNamedWindow ('2-amplifie', highgui.CV_WINDOW_AUTOSIZE)
        highgui.cvNamedWindow ('3-lisser-Smooth', highgui.CV_WINDOW_AUTOSIZE)
        highgui.cvNamedWindow ('4-lisser-And', highgui.CV_WINDOW_AUTOSIZE)
       
        # move the new window to a better place
        highgui.cvMoveWindow ('Camera', 0, 0)
        highgui.cvMoveWindow ('Binarisation', 0, 280)
        highgui.cvMoveWindow ('1-without background', 320, 0)
        highgui.cvMoveWindow ('2-amplifie', 320, 280)
        highgui.cvMoveWindow ('3-lisser-Smooth', 640, 0)
        highgui.cvMoveWindow ('4-lisser-And', 640, 280)
        
        #trackbar pour la modification des variables de reglages
        highgui.cvCreateTrackbar ("nombre division", "Camera", get_nb_div(), 6, set_nb_div)
        highgui.cvCreateTrackbar ("seuil binarisation", "Binarisation", get_seuil(), 255, set_seuil)
        highgui.cvCreateTrackbar ("gain", "2-amplifie", get_gain(), 100, set_gain)
        #highgui.cvCreateTrackbar ("param lissage", "3-lisser", 3, 3, set_param_liss)
        #highgui.cvCreateTrackbar ("param 2 lissage", "3-lisser", 1, 10, set_param2_liss)

    #############################  GO WORK  ######################################
    frame = highgui.cvQueryFrame (capture)
    frame_size=cv.cvGetSize (frame)  ;  hauteur_image=cv.cvGetSize (frame).height  ;  largeur_image=cv.cvGetSize (frame).width
    
    print "hauteur_image:"+str(hauteur_image)+" largeur_image:"+str(largeur_image)+ " depth:"+str(frame.depth)
    print "frame per seconds : "+str(highgui.CV_CAP_PROP_FPS)
    print ""
    
    font=cv.cvInitFont( cv.CV_FONT_HERSHEY_SIMPLEX,1.0, 1.0)
   
    frameGray = cv.cvCreateImage (frame_size, frame.depth, 1)
    ##frameGrayBg = cv.cvCreateImage (frame_size, frame.depth, 1)
    framewithoutbg = cv.cvCreateImage (frame_size, frame.depth, 1)
    framemul = cv.cvCreateImage (frame_size, frame.depth, 1)
    framelisser = cv.cvCreateImage (frame_size, frame.depth, 1)
    frameBin = cv.cvCreateImage (frame_size, frame.depth, 1)
    framelisser1 = cv.cvCreateImage (frame_size, frame.depth, 1)
    framelisser2 = cv.cvCreateImage (frame_size, frame.depth, 1)
    
    mess_saved=0
    first=1
    first2=1 
    
    # Xlib init   ,  cf : Control Periph
    souris=MouseControl(largeur_image, hauteur_image) 
    
    # server Tuio init   ,  cf : TuioServerModule en C++
    #TuioServerModule.initServer();
    
    while 1:
        # do forever        
        # capture the current image
        frame = highgui.cvQueryFrame (capture) 
        highgui.cvShowImage ('Originale', frame);
        
        if frame is None:
        # no image captured... end the processing 
            break 
        
        ################   traitement de l'image   ################
        cv.cvCvtColor( frame,frameGray, cv.CV_BGR2GRAY ); # niveau de gris 
        cv.cvSub(frameGray, frameGrayBg, framewithoutbg); # soustraction du background
        cv.cvMul(framewithoutbg, framewithoutbg,framemul,get_gain()); # amplification
        cv.cvSmooth(framemul, framelisser1,cv.CV_BLUR,  param_liss[0], param2_liss[0]); # lissage
        if first==0:      # "moyenne" sur deux image
            cv.cvAnd(framelisser1, framelisser2, framelisser)
        if first==1:
            framelisser=cv.cvCloneImage(framelisser1)
        
        framelisser2=cv.cvCloneImage(framelisser1)
        
        cv.cvThreshold(framelisser,frameBin, get_seuil(), float(255), cv.CV_THRESH_BINARY) # binaristaion de l image
      
            
        ################   run detection   ################
        zone_active=zoneActivePremier(zone_active, frameBin)
        if len(zone_active)==0:
            centrePointeur=[]
            info_size=[]
        if len(zone_active)!=0:
            for i in range(1, nb_div_zone[0]+1):
                zone_active=zoneActive(zone_active,frameBin, i)
            pointeur=pointeurPrecision(zone_active,frameBin)
            pointeur=FiltreRedondance(pointeur[0], pointeur[1]) # pointeur[0] : centrePointeur , pointeur[1] : info_size
            
            centrePointeur=pointeur[0]
            info_size=pointeur[1]
            
            if len(centrePointeur)>20:
                frameGrayBg = cv.cvCloneImage(frameGray)  # reprend l image de bg qd lumiere augmente de trop


            
            if len(centrePointeur)!=0 and len(prec_centrePointeur)!=0:
                if first2==1:
                    first2=0
                    for i in range (0, len(centrePointeur)):
                        id_Pointeur.append(id_abs[0])
                        prec_id_Pointeur.append(id_abs[0])
                        id_abs[0]=id_abs[0]+1
                id_Pointeur = identitePointeur(centrePointeur, prec_centrePointeur,id_Pointeur,prec_id_Pointeur,  info_size)
            prec_centrePointeur=[]
            
            
            for i in range(0, len(centrePointeur)):
                prec_centrePointeur.append(centrePointeur[i])
            prec_info_size=[]
            for i in range(0, len(info_size)):
                prec_info_size.append(info_size[i])
            prec_id_Pointeur=[]
            for i in range(0, len(id_Pointeur)):
                prec_id_Pointeur.append(id_Pointeur[i])
            
            
            
            ################   use list of pointeur  ################
            
            #print id_Pointeur
            # affichage dans le shell
            #if len(centrePointeur)!=1:
            #   printListPointeur(centrePointeur)
            
            # utilsation de ControlPeriph
            MouseControl.mouse_warp(souris,centrePointeur[0].x,centrePointeur[0].y,0,0)
            
            
            # envoie des coordonnees de pointeur via  protocole Tuio
            ##if first2==0:
            ##    sendTuioMess()
            
        first =0
        if GUI==1:
            #on trace un cercle sur les pointeurs
            for i in range(0, len(centrePointeur)):
                cv.cvCircle( frame, centrePointeur[i], 5, color, 2, 6, 0);
                #if first2==0:
                #    cv.cvPutText(frame, str(id_Pointeur[i]), centrePointeur[i], font, color2)
            cv.cvPutText(frame, str(len(centrePointeur)), cv.cvPoint(20, 30), font, color) # affiche le nombre de pointeur
            
            # message "config saved" temporaire
            if mess_saved<20 and mess_saved!=0 :
                cv.cvPutText(frame, "config saved", cv.cvPoint(20, 100), font, color) 
                mess_saved=mess_saved+1
                if mess_saved == 19:
                    mess_saved=0
            
            # we can now display the images
            highgui.cvShowImage ('Camera', frame);
            highgui.cvShowImage ('Binarisation', frameBin)
            highgui.cvShowImage ('1-without background', framewithoutbg)
            highgui.cvShowImage ('2-amplifie', framemul)
            highgui.cvShowImage ('3-lisser-Smooth', framelisser1)
            highgui.cvShowImage ('4-lisser-And', framelisser2)
            
            # handle events
            if image_par_image== 1:
                k = highgui.cvWaitKey (100000000);
                            

                if k == '\x1b':
                # user has press the ESC key, so exit
                    highgui.cvDestroyWindow("Camera");
                    highgui.cvDestroyAllWindows();
                    sys.exit(0);
                    break
                
                if k=='n':
                    #image par image. util si la var image_par_image=1 ligne 42 
                    None
            
            k = highgui.cvWaitKey (10);
            if k == 'b':
                # recupere l image en appuyant sur b
                frameGrayBg = cv.cvCloneImage(frameGray)
            
            if k == 's':
                # save configuration
                highgui.cvSaveImage ("background.bmp", frameGrayBg)
                logfile = open('config', 'w') 
                text=str(nb_div_zone[0])+"\n"+str(seuil_binary[0])+"\n"+str(gain[0])+"\n"+str(param_liss[0])+"\n"+str(param2_liss[0])
                logfile.write(text)
                logfile.close()
                mess_saved=1
                
            
            if k == '\x1b':
                # user has press the ESC key, so exit
                highgui.cvDestroyAllWindows();
                break

    sys.exit(0);
