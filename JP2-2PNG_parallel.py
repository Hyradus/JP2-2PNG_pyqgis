#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: JP2 to PNG converter
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de

This script use pyqgis to load JP2 images and convert into png of a given resolution.

Before run edit path to qgis executable

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
from argparse import ArgumentParser
from tkinter import Tk,filedialog

global PATH
global vres


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



def pngs(file):
    image_name= pathlib.Path(file).name.split('.')[0]
		#add vectorlayers
    qgis_init()
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
    
    # max_height = vres
    width = rlayer.width()
    height = rlayer.height()
    
    # if height < max_height:
    #     new_height=2048
    #     new_width = round(width*new_height/height)
    
    # else:
    new_height=vres
    new_width = int(width*new_height/height)

    
    # new_width = (layer.width()/res)
    # new_height = int(layer.height()/res)
    settings.setOutputSize(QSize(new_width, new_height))
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
    Parallel (n_jobs=JOBS)(delayed(pngs)(files[i])
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
def main():

    from tqdm import tqdm
    import psutil
    JOBS=psutil.cpu_count(logical=False)
    # JOBS = 8
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
            

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--PATH', help='Directory with JP2 files')
    parser.add_argument('--vres', help='Max vertical resolution')
    
    args = parser.parse_args()  

    PATH = args.PATH
    vres = args.vres
    
    if PATH is None:
        root = Tk()
        root.withdraw()
        PATH = filedialog.askdirectory(parent=root,initialdir=os.getcwd(),title="Please select the folder with JP2 files")
        print('Working folder:', PATH)
    
    if vres is None:
        while True:
            try:
                vres = int(input('Insert max vertical resolution in pixels: ' ))
            except:
                print('Please insert only integer')
                # continue
            if isinstance(vres, int):
                break
    
    os.chdir(PATH)
    rasters = get_paths(PATH)
    make_folder('PNGs')

    
    main()





