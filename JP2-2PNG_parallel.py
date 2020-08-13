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



PATH = '/media/gnodj/W-DATS/HiRiSE_Data/Skylight'

global res
res = 14
def qgis_init():
# Initialize QGIS Application
    qgs = QgsApplication([], False)
    QgsApplication.setPrefixPath("/home/gnodj/anaconda3/envs/38/bin/qgis", True)
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
    # from pathlib import Path

    # for path in Path(PATH).rglob('*.JP2'):
    #     print(path.name)
    import glob
    os.chdir(PATH)
    filename = [i for i in glob.glob('**/*.JP2',recursive=True)]
    return(filename)



def pngs(file, res):
    image_name= pathlib.Path(file).name.split('.')[0]
		#add vectorlayers
    qgs = qgis_init()
    project= QgsProject.instance() 
    # project_name = PATH+'/'+image_name+'.qgz'
    # project.write(project_name)
        
    rlayer = QgsRasterLayer(file, image_name)
    # QgsProject.instance().addMapLayer(rlayer, False)
    project.addMapLayer(rlayer, False)
    # project.write(project_name)
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
        # save the image; e.g. img.save("/Users/myuser/render.png","png")
        name = PATH+'/PNGs/'+image_name+'_print.png'
        img.save(name, "png")

    render.finished.connect(finished)  
    render.start()
    render.waitForFinished()
    # print('rendering: ', image_name)
    # print(QgsProject.instance().mapLayers())
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



# for file in rasters:
# # for i in range(4):
#     # file = rasters[i]
#     if file.endswith(".JP2"):
#         print(QgsProject.instance().mapLayers())
#         # time.sleep(100)
#         # QTimer.singleShot(1000, pngs()
        
#         # pngs(file)
#         # time.sleep(5)
        
#         # time.sleep(5)
#         pngs(file)
#         # project.write(project_name)
#         print(QgsProject.instance().mapLayers())
#         project.clear()

rasters = get_paths(PATH)

# project= QgsProject.instance() 
# project_name = PATH+'/Skylight_JP2.qgz'
# project.write(project_name)
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
        # print(files)
        print('\nRendering: ', files)
        parallel_JP2PNG(files, JOBS)
        pbar.update(JOBS)
        

