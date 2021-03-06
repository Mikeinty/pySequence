#!/usr/bin/env python
# -*- coding: utf-8 -*-

##This file is part of pySequence
#############################################################################
#############################################################################
##                                                                         ##
##                                   error                                 ##
##                                                                         ##
#############################################################################
#############################################################################

## Copyright (C) 2014 Cédrick FAURY - Jean-Claude FRICOU
##
## pySéquence : aide à la construction
## de Séquences et Progressions pédagogiques
## et à la validation de Projets

#    pySequence is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
    
#    pySequence is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pySequence; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

u"""
Module error
************

Gestion des erreurs

"""

import traceback

import sys
import util_path

from widgets import messageInfo
# 
import wx

import version



def MyExceptionHook(typ, value, traceb):
    u"""
    Handler for all unhandled exceptions.
  
    :param `etype`: the exception type (`SyntaxError`, `ZeroDivisionError`, etc...);
    :type `etype`: `Exception`
    :param string `value`: the exception error message;
    :param string `trace`: the traceback header, if any (otherwise, it prints the
     standard Python header: ``Traceback (most recent call last)``.
    """
#     frame = traceb.tb_frame
    print >>sys.stderr,"\n"
    traceback.print_tb(traceb)
    print >>sys.stderr,"\nType : ",typ,"\n"
    print >>sys.stderr,"ValueError : ",value
#     print "".join(traceback.format_exception(typ, value, traceb))
    SendBugReport()
#     sys.exit()
    







class RedirectErr:
    #
    # Redirige la sortie des erreurs pour envoyer l'erreur par mail
    #
    def __init__(self,stderr):
        self.stderr=stderr
        self.content = ""
        self.error_occured=False
        self.file_error=None

    def write(self,text):
        #
        # A la premiere erreur, on enregistrer la fonction de sortie
        #
        if not self.error_occured:
            #
            # Première erreur
            # D'abord on enregistre la fonction atexit
            import atexit
            
            atexit.register(SendBugReport)
            # puis on ouvre le fichier qui contient les erreurs
            self.file_error = open(util_path.ERROR_FILE,'w')
            self.error_occured=True
        if self.file_error is not None:
            self.file_error.write(text)
            self.file_error.flush()


# sys.stdout = open(util_path.LOG_FILE, "w")
# print ("test sys.stdout")


if True:#not "beta" in version.__version__:
    sys.excepthook = MyExceptionHook
#     sys.stderr=RedirectErr(sys.stderr)





def SendBugReport():
    """
    Fonction qui envoie le rapport de bug par mail.
    """
    #
    # On ouvre le fichier qui contient les erreurs
    #
    import webbrowser, datetime

    message= u"%s a rencontré une erreur et doit être fermé.\n\n" \
             u"Voulez-vous envoyer un rapport d'erreur ?" %version.__appname__
    dlg=wx.MessageDialog(None,message,"Erreur", wx.YES_NO| wx.ICON_ERROR).ShowModal()
    if dlg==5103:#YES, on envoie le mail
        #
        # Définition du mail
        #
        
        messageInfo(None, u"Rapport d'erreur", 
                    u"Rédaction du rapport d'erreur\n\n" \
                    u"Votre logiciel de messagerie va s'ouvrir\n" \
                    u"pour rédiger un courrier de rapport d'erreur.\n\n" \
                    u"Merci d'y indiquer le plus précisément possible\n" \
                    u"comment s'est produit cette erreur\n" \
                    u"ainsi que le moyen de la reproduire.\n" \
                    u"Ne pas hesiter à joindre un fichier .prj, .seq ou .prg.\n\n" \
                    u"L'équipe de développement de %s vous remercie pour votre participation." %version.__appname__)
        
        
        import util_path
        e_mail="cedrick.faury@ac-clermont.fr"
        now = str(datetime.datetime.now())
        subject = version.__appname__ + version.__version__
        subject += u" : rapport d'erreur" + now
#        body="<HTML><BODY><P>"
        
        body = u"%s a rencontré une erreur le " %version.__appname__ + now
        body += u"%0ADescription d'une méthode pour reproduire l'erreur :"
        body += u"%0A%0A%0A%0A%0A"
        body += u"=================TraceBack===================="
        #
        # Parcours du fichier
        #
        file_error=open(util_path.ERROR_FILE,'r')
        for line in file_error.readlines():
            body+=line+"%0A"
        file_error.close()
        body += u"==============================================%0A%0A"
        
        sys.stdout.close()
        file_log = open(util_path.LOG_FILE,'r')
#         sys.stdout.seek(0, 0)
        body += u"%0A".join(file_log.readlines())
        file_log.close()
        sys.stdout = open(util_path.LOG_FILE, "w")

#         body += u"L'équipe de développement de %s vous remercie pour votre participation." %version.__appname__
#        body+="</P></BODY></HTML>"
        file_error.close()
        to_send="""mailto:%s?subject=%s&body=%s"""%(e_mail,subject,body)

        print "Envoi ...",to_send
        print webbrowser.open("""mailto:%s?subject=%s&body=%s"""%(e_mail,subject,body))

    