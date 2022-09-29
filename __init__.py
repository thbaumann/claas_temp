# encoding: utf-8
#-----------------------------------------------------------
# Copyright (C) 2022 Thomas Baumann, parts recycled from https://github.com/enricofer/autoSaver
# based on qgis-minimal-plugin from Martin Dobias

#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# NUR ZU EXPERIMENTELLEN ZWECKEN. FUER PRODUKTIVBETRIEB BESSER MITTELS QGSTASK bzw.EIGENEM THREAD FUER DAS FILEWATCH !!!
# 
#---------------------------------------------------------------------
from qgis.core import Qgis, QgsProject, QgsExpression, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QTimer
import os

def classFactory(iface):
    return ClaasPlugin(iface)

# LEDIGLICH EIN EINFACHER PROOF OF CONCEPT UND KEIN FERTIGES PLUGIN.
# NUR ZU EXPERIMENTELLEN ZWECKEN. FUER PRODUKTIVBETRIEB BESSER MITTELS QGSTASK bzw.EIGENEM THREAD FUER DAS FILEWATCH UND SIGNAL AN DEN HAUPT-THREAD !!!

class ClaasPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.cron = QTimer()
        self.cron.timeout.connect(self.cronEvent)

    def initGui(self):
        icon_on_off = QIcon()
        icon_on_off.addFile( os.path.join(self.plugin_dir,"icons", "slide_off.svg"), state=QIcon.Off )
        icon_on_off.addFile( os.path.join(self.plugin_dir,"icons", "slide_on.svg"), state=QIcon.On )
        self.action_on_off = QAction( icon_on_off, u"Plugin inactive or active", self.iface.mainWindow() )
        self.action_on_off.toggled.connect( self.tis_bau )
        self.action_on_off.setCheckable( True )
        self.action_on_off.setChecked( False )

        self.iface.addToolBarIcon(self.action_on_off)

    def unload(self):
        self.cron.stop()
        self.cron.timeout.disconnect(self.cronEvent)
        self.iface.removeToolBarIcon(self.action_on_off)
        del self.action_on_off

    def tis_bau(self, checked):
        self.vlayer = QgsProject.instance().mapLayersByName("Baeume")[0]
        self.expr_string = '"M1"=50'
        self.expr = QgsExpression(self.expr_string )
        print(checked)
        if checked:
            print("start")
            self.cron.start(5000)
        else:
            self.cron.stop()
            

    def cronEvent(self):
        #print("Hallo")
        #https://nyalldawson.net/2016/10/speeding-up-your-pyqgis-scripts/
        self.vlayer.dataProvider().forceReload()
        # offene Fragen: brauchen wir zwingend einen forceReload? gibt es einen FeatureRequest, der direkt auf die Platte geht? bringt QgsFeatureRequest.NoGeometry was, wenn wir eh einen ForceReload machen? 
        
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes(['M1'], self.vlayer.fields() )
        it = self.vlayer.getFeatures(request)
        anz = len(list(it))
        if anz > 0:
            self.vlayer.selectByExpression(self.expr_string )
            self.iface.mapCanvas().zoomToSelected(self.vlayer)
        # besser waere es ggf. noch die schon gefundenen Treffer in eine Liste zu schreiben und dann nur noch zu testen, ob es neue Treffer gibt