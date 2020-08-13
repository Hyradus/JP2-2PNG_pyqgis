#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: 
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Wed Aug  5 18:47:33 2020
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""


import os
from qgis.core import (QgsRasterLayer)
import pathlib
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererSequentialJob
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import QSize

from qgis.core import QgsApplication

def qgis_init():
# Initialize QGIS Application
    qgs = QgsApplication([], False)
    QgsApplication.setPrefixPath("INSERT PATH TO QGIS EXECUTABLE", True)
    QgsApplication.initQgis()
    for alg in QgsApplication.processingRegistry().algorithms():
            print(alg.id(), "->", alg.displayName())
    return(qgs)


PATH = #INSERT PATH TO JP2 DIRECTORY

def get_paths(PATH):
    # from pathlib import Path

    # for path in Path(PATH).rglob('*.JP2'):
    #     print(path.name)
    import glob
    os.chdir(PATH)
    filename = [i for i in glob.glob('**/*.JP2',recursive=True)]
    return(filename)


def pngs(file):
    image_name= pathlib.Path(file).name.split('.')[0]
    rlayer = QgsRasterLayer(file, image_name)
    project.addMapLayer(rlayer, False)
    project.write(project_name)
    layer = project.mapLayersByName(image_name)[0]
    
    settings = QgsMapSettings()
    settings.setLayers([layer])
    settings.setBackgroundColor(QColor(255, 255, 255))
    
    width = int(layer.width()/4)
    height = int(layer.height()/4)
    settings.setOutputSize(QSize(width, height))
    settings.setExtent(layer.extent())
    
    render = QgsMapRendererSequentialJob(settings)

    def finished():
        img = render.renderedImage()
        name = PATH+'/'+image_name+'_print.png'
        img.save(name, "png")

    render.finished.connect(finished)  
    render.start()
    render.waitForFinished()
    print('rendering: ', image_name)


rasters = get_paths(PATH)

project= QgsProject.instance()      
project_name = PATH+'/Skylight_JP2.qgz'
project.write(project_name)

for file in rasters:
    if file.endswith(".JP2"):
        print(QgsProject.instance().mapLayers())
        pngs(file)
        print(QgsProject.instance().mapLayers())
        project.clear()
