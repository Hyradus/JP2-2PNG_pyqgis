#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: 
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Wed Aug  5 18:47:33 2020
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""


import os
import shutil
from datetime import datetime
from qgis.core import (QgsRasterLayer)
import pathlib
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererSequentialJob
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import QSize

from qgis.core import QgsApplication



PATH = #INSERT PATH TO JP2 DIRECTORY

global res
res = 14
def qgis_init():
# Initialize QGIS Application
    qgs = QgsApplication([], False)
    QgsApplication.setPrefixPath("INSERT PATH TO QGIS EXECUTABLE", True)
    QgsApplication.initQgis()
    for alg in QgsApplication.processingRegistry().algorithms():
            print(alg.id(), "->", alg.displayName())
    return(qgs)

def answer(question):
    answ = None
    while answ not in ['yes','y','no','n']:
        print("Please enter yes/y or no/n.")    
        answ = input(question+': ')
    return(answ)

def make_folder(name):
    os.getcwd()
    folder = name
    if os.path.exists(folder):
           qst = name + ' Folder exist, remove it? '
           answ = answer(qst)
           if answ in ['yes', 'y']:               
               shutil.rmtree(folder)
               os.mkdir(folder)
               print(name, 'Folder created')
           else:
               now = datetime.now()
               new_name = name +'_' + now.strftime("%d-%m-%Y_%H-%M-%S")
               print(new_name, ' Folder not exist, creating.')
               os.mkdir(new_name)
               print('Created new ', name,' Folder')
    else:
        print(name, ' Folder not exist, creating.')
        os.mkdir(folder)
        print('Created new ', name,' Folder')
    return(folder)

def get_paths(PATH):
    import glob
    os.chdir(PATH)
    filename = [i for i in glob.glob('**/*.JP2',recursive=True)]
    return(filename)



def pngs(file, res):
    image_name= pathlib.Path(file).name.split('.')[0]
    qgs = qgis_init()
    project= QgsProject.instance() 
    rlayer = QgsRasterLayer(file, image_name)
    project.addMapLayer(rlayer, False)
    layer = project.mapLayersByName(image_name)[0]
    
    settings = QgsMapSettings()
    settings.setLayers([layer])
    settings.setBackgroundColor(QColor(255, 255, 255))
    
    width = int(layer.width()/res)
    height = int(layer.height()/res)
    settings.setOutputSize(QSize(width, height))
    settings.setExtent(layer.extent())
    
    render = QgsMapRendererSequentialJob(settings)

    def finished():
        img = render.renderedImage()
        name = PATH+'/PNGs/'+image_name+'_print.png'
        img.save(name, "png")

    render.finished.connect(finished)  
    render.start()
    render.waitForFinished()
    project.clear()

def parallel_JP2PNG(files, JOBS):
    from joblib import Parallel, delayed
    Parallel (n_jobs=JOBS)(delayed(pngs)(files[i],res)
                            for i in range(len(files)))


def chunk_creator(item_list, chunksize):
    import itertools

    it = iter(item_list)
    while True:
        chunk = tuple(itertools.islice(it, chunksize))
        if not chunk:
            break
        yield chunk

rasters = get_paths(PATH)

os.chdir(PATH)
make_folder('PNGs')

from tqdm import tqdm
import psutil
JOBS=psutil.cpu_count(logical=False)
# JOBS = 1
rasters = get_paths(PATH)
with tqdm(total=len(rasters),
         desc = 'Generating PNGs',
         unit='File') as pbar:
    
    filerange = len(rasters)
    chunksize = round(filerange/JOBS)
    if chunksize <1:
        chunksize=1
        JOBS = filerange
    chunks = []
    for c in chunk_creator(rasters, JOBS):
        chunks.append(c)
        

    for i in range(len(chunks)):
        files = chunks[i]    
        print('\nRendering: ', files)
        parallel_JP2PNG(files, JOBS)
        pbar.update(JOBS)
        

