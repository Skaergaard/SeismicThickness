# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 12:52:22 2022

@author: 1mart
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import geopandas as gpd
import shapely
import contextily as cx

def circlegrid(crs,corticales,espaciamiento,k,r_max,r_min,D,guardar_shp,shp):
    #Grid. First, a grid is greated, to divede the area
    #The total area of the grid is delimited by the limits of the seismic catalogue 
    corticales = pd.read_csv(corticales)
    geo_dat=gpd.GeoDataFrame(corticales, geometry=gpd.points_from_xy(corticales.longitud, corticales.latitud), crs=crs)
    xmin, ymin, xmax, ymax= geo_dat.total_bounds
    
    cell_size = espaciamiento 
    
    # Create the grid cells through a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax+cell_size, cell_size ):
        for y0 in np.arange(ymin, ymax+cell_size, cell_size):
            # bounds
            x1 = x0-cell_size
            y1 = y0+cell_size
            grid_cells.append( shapely.geometry.box(x0, y0, x1, y1)  )
            
    cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=crs)
    
    #The center each cell is calculated to create grid of equally spaced nodes
    list=np.arange(0,len(cell),1)
    list=pd.DataFrame(list,columns=['i'])
    points=gpd.GeoDataFrame(list, geometry=cell['geometry'].centroid) 
    
    #Create circular cells with a radius determined by the k nearest epicenters
    
    def knearest(from_points, to_points, k):
        distlist = to_points.distance(from_points)
        distlist.sort_values(ascending=True, inplace=True) # To have the closest ones first
        return distlist[:k].quantile(1)
    
    for Ks in [k]:
        name = 'dist_to_closest_k' # to set column name
        points[name] = points.geometry.apply(knearest, args=(geo_dat, Ks))
                
    circlegrid = points.copy()
                
    for i in range(len(points)):
        if points['dist_to_closest_k'][i] > r_min:
            size=points['dist_to_closest_k'][i]
        else:
            size=r_min
        
        circlegrid['geometry'][i] = circlegrid['geometry'][i].buffer(size)
                
    #Calculate the depth distribution of earthquakes within each cell
    
    nr_celdas=range(len(circlegrid))
    circlegrid=circlegrid[circlegrid['dist_to_closest_k']<r_max]
    circlegrid.reset_index(inplace=True)
    circlegrid['D95']='0'  
                
    def D95(datos):
        """
        This function calculates D95 (or any chosen percentile)
        
        """
        for k in range(len(nr_celdas)-1):
            sismos_celda=gpd.sjoin(datos.iloc[k:k+1],geo_dat, how='inner')
            datos.loc[k, 'D95']=sismos_celda['profundidad'].quantile(D)
    
    D95(circlegrid)
    circlegrid['D95']= pd.to_numeric(circlegrid['D95'])
                
    #Save data to a shapefile if needed, Yes/No = Si/No
    if guardar_shp == "Si": 
        circlegrid.to_file(shp)
    else:
        print ("No shapefile was created")  
    
    #Make map of the layer depth 
    
    ax=circlegrid.plot(column='D95', figsize=(24, 16), cmap='Spectral_r', legend=True,
                       legend_kwds={'label': "Layer depth (km)"}, alpha=0.5)
    
    plt.autoscale(False)
    plt.grid(True)
    world=gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world.plot(ax=ax, color='None', edgecolor='black')
    cx.add_basemap(ax=ax, crs=circlegrid.crs.to_string(), zoom=5, source=cx.providers.Esri.WorldShadedRelief)
    plt.show()
