# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 19:47:17 2022

@author: 1mart
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import geopandas as gpd
import shapely
from shapely.geometry import LineString
import contextily as cx

def squaregrid(crs, corticales, tamaño_celda, traslape, D,k_min, guardar_shp,shp):
    
    corticales = pd.read_csv(corticales)
    geo_dat=gpd.GeoDataFrame(corticales, geometry=gpd.points_from_xy(corticales.longitud, corticales.latitud), crs=crs)
    
    #Grid. First, a grid is greated, to divede the area
    #The total area of the grid is delimited by the limits of the seismic catalogue
    xmin, ymin, xmax, ymax= geo_dat.total_bounds
    
    cell_size = tamaño_celda    
    
   # Create the grid cells through a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax+cell_size, cell_size ):
        for y0 in np.arange(ymin, ymax+cell_size, cell_size):
            # bounds
            x1 = x0-cell_size-traslape
            y1 = y0+cell_size+traslape
            grid_cells.append( shapely.geometry.box(x0, y0, x1, y1)  )
        
    cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=crs)
    
    densidad = gpd.sjoin(geo_dat, cell, how='left', op='within')
    densidad['n_sismos']=1
    dissolve = densidad.dissolve(by="index_right", aggfunc="count")
    cell.loc[dissolve.index, 'n_sismos'] = dissolve.n_sismos.values
    
    #Verify cell size and overlap 
    c1=gpd.GeoDataFrame(cell.loc[0:0],columns=['geometry'], crs=crs)
    c2=gpd.GeoDataFrame(cell.loc[1:1],columns=['geometry'], crs=crs)
    
    xmin1, ymin1, xmax1, ymax1= c1.total_bounds
    xmin2, ymin2, xmax2, ymax2= c2.total_bounds
    print('Cell size:', (ymin1-ymax1)*-1, '°')
    print('Overlap %:', -100*((ymax1-ymin2)/(ymin1-ymax1)))
    
    #Visualization of cell size and overlap
    fig1=plt.figure(figsize=(20,20))
    ax1=fig1.add_subplot()
    cell.plot(ax=ax1, facecolor="none", edgecolor='grey')
    cell.loc[0:0].plot(ax=ax1, alpha=0.5)
    cell.loc[1:1].plot(ax=ax1, alpha=0.5, color='y')

    
    #Calculation of layer depth: 
    d95=cell.copy()
    d95['D95']='0' 
    d95=d95[d95['n_sismos']>=k_min]
    d95.dropna(inplace=True)
    d95.reset_index(inplace=True)
    
    cmax=len(d95)
    nr_celdas=np.arange(0,cmax,1)
    
    def D95(datos):
        """
        This function calculates D95 (or any chosen percentile)
        """
        for k in range(len(nr_celdas)):
            sismos_celda=gpd.sjoin(datos.iloc[k:k+1],geo_dat, how='inner')
            datos.loc[k, 'D95']=sismos_celda['profundidad'].quantile(D)
    
    D95(d95)
    d95['D95']= pd.to_numeric(d95['D95'])
    
    
    #Make map of the layer depth:  
    fig2=plt.figure(figsize=(24, 16))
    ax2=fig2.add_subplot()
    d95.plot(ax=ax2, column='D95', cmap='Spectral_r', legend=True,
               legend_kwds={'label': "Espesor sismogenico (km)"}, alpha=0.7)
    
    plt.autoscale(False)
    plt.grid(True)
    world=gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world.plot(ax=ax2, color='None', edgecolor='black')
    cx.add_basemap(ax=ax2, crs=d95.crs.to_string(), source=cx.providers.Esri.WorldShadedRelief, zoom=5)
    
    plt.show()

    #Save data to a shapefile if needed, Yes/No = Si/No
    if guardar_shp == "Si": 
        d95.to_file(shp)
    else:
        print ("No shapefile was created")