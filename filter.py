# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 19:06:45 2022

@author: 1mart
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
import cartopy.crs as ccrs 
import cartopy.feature as cfeature

def filtro(archivo, sep, calcular_Mc, Mc,err_prof,err_h,margen_slab,margen_moho, output,latmin,latmax,lonmin,lonmax):
    
    """
    Requirements: Seismic Catalogue must be in a .csv file. Must have a columns with the names:
    latitud, longitud, profundidad, magnitud, err_h and err_prof
    Depth must be in positive kilometers (eg. 5 not -5)
    
    Also, on the same directry you are working on you must have a .txt file for the slab (eg. slab2.0,https://doi.org/10.5066/F7PV6JNV.)
    and one for the moho
    It is asumed that this files are named "slab2.txt" and "moho.txt"
    
    
    A detailed description of the variables used in this code can be found in the "README" file 
    """
   
    #Import and check data
    dat=pd.read_csv(archivo, sep=sep)
    dat['profundidad']=dat['profundidad']*-1
    print(dat.head())
    
    ##########################################################################################
    #1. Magnitude of completeness calculation (if needed) through the Maximum Curvature Technique (see Mignan y Woessner, 2012)
    fig, ax = plt.subplots(1,1, figsize=(15,8))
    plt.hist(dat['magnitud'], bins=100) 
    plt.xlim(0,10)
    plt.axvline(Mc,color='r')
    #plt.show()
    
    ##########################################################################################
    #2. Filters
    if calcular_Mc == "No": 
        #2.1 Eliminate events with magnitude < Mc
        dat_f=dat[dat['magnitud']>=Mc]
        print('Filtered by Mc')
        
        #2.2 Eliminate events with depth or magnitude fixed at 0 
        dat_f=dat_f[dat_f['profundidad']!=0]
        dat_f=dat_f[dat_f['magnitud']!=0]
        print('Filtered events with depth or Mw = 0')
        
        #2.3 Eliminate events with high location error 
        dat_f=dat_f[dat_f['err_prof']<=err_prof]
        dat_f=dat_f[dat_f['err_h']<=err_h]
        print('Filtered by location error')
        
        #######################################################################################
        #2.4 Eliminate events below the slab + margin  
        
        print('Filtering events below the slab... This may take a while...')
        
        dat_f.reset_index(inplace=True)
        
        slab = pd.read_csv('slab.txt', header=None, names=['Longitud', 'Latitud', 'profundidad'])
        slab['Longitud'] = slab['Longitud']-360 #Transformar longitudes
        slab = slab.dropna() #Eliminar valores nulos
        slab.to_csv('slab2.txt', index=False, header=False)
        

        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx], idx
        
        def isbetween(x, mayor, menor):
            return menor <= x <= mayor
                
        def SLAB_MOD(lon,lat,prof):
                
            data="slab2.txt"
            fosa_sam = np.loadtxt(data, delimiter=',')
            LONsam=fosa_sam[:,0]; LATsam=fosa_sam[:,1]; DEPsam=fosa_sam[:,2];  #numeros negativos
            
            
            '''Clip slab to study area'''
            index_si=[];
            for i in range(len(LONsam)):
                if isbetween(LATsam[i],latmax,latmin) and isbetween(LONsam[i],lonmax,lonmin):
                    index_si.append(i)
            lonsam=LONsam[index_si]; latsam=LATsam[index_si]; depsam=DEPsam[index_si];
            
            lista2=[]
            for i in range(len(lon)):
                lon_ev=lon[i]; lat_ev=lat[i]; prof_ev=prof[i]; 
                lonsl=find_nearest(lonsam,lon_ev)[0] 
                latsl=find_nearest(latsam,lat_ev)[0]
                
                index=np.where(np.logical_and(lonsam==lonsl,latsam==latsl))
                profsl=depsam[index]
                
                if (prof_ev >= profsl+margen_slab):
                    lista2.append(i)
         
            return lista2
    
        
        index2 = SLAB_MOD(np.array(dat_f["longitud"]), np.array(dat_f["latitud"]) , np.array(dat_f["profundidad"]))

        dat_f=dat_f.loc[index2]
        dat_f.reset_index(inplace=True)
        print('Filtered by the slab')
        
        
        ###########################################################################################################
        #2.5 Filter events below the moho
        
        print('Filtering events below the moho... This may take a while...')
        
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx], idx
        
        def isbetween(x, mayor, menor):
        
            return menor <= x <= mayor
        
        
        def MOHO_MOD(lon,lat,prof):
                
            moho="moho.txt"
            fosa_sam = np.loadtxt(moho, delimiter=',')
            LONsam=fosa_sam[:,0]; LATsam=fosa_sam[:,1]; DEPsam=fosa_sam[:,2];
            
            lonsam=LONsam; latsam=LATsam; depsam=DEPsam;
            lista3=[]
            for i in range(len(lon)):  
                lon_ev=lon[i]; lat_ev=lat[i]; prof_ev=prof[i]; 
                lonsl=find_nearest(lonsam,lon_ev)[0] 
                select=np.where(lonsam==lonsl)
                latsl=find_nearest(latsam[select],lat_ev)[0] 
                index3=np.where(np.logical_and(lonsam==lonsl,latsam==latsl))
                profsl=depsam[index3[0][0]]
                
                if (prof_ev >= profsl+margen_moho):
                    lista3.append(i)
         
            return lista3
        index4 = MOHO_MOD(np.array(dat_f["longitud"]), np.array(dat_f["latitud"]) , np.array(dat_f["profundidad"]))
        corticales=dat_f.loc[index4]
        print('Filtered by moho \n Filtering done :) \n Lets check the data')
        #############################################################################################
        #3. Check data:
        corticales.drop('level_0', inplace=True, axis=1)
        corticales.drop('index', inplace=True, axis=1)
    
        corticales.to_csv(output, index=False)
        print(corticales.describe())
        
        fig2 = plt.figure(figsize=(10,15))
        ax2 = fig2.add_subplot(1, 1, 1, projection=ccrs.Orthographic())
        #ax2.set_extent([-60, -80, -60, -10], crs=ccrs.PlateCarree())
        #ax2.set_xticks([-80, -75, -70, -65, -60], crs=ccrs.PlateCarree())
        #ax2.set_yticks([-10, -20, -30, -40, -50, -60], crs=ccrs.PlateCarree())
        ax2.add_feature(cfeature.LAND)
        ax2.add_feature(cfeature.OCEAN)
        ax2.add_feature(cfeature.COASTLINE)
        ax2.add_feature(cfeature.BORDERS, linestyle=':')
        
        plt.plot(dat['longitud'],dat['latitud'],'k.')
        plt.plot(corticales['longitud'],corticales['latitud'],'c.')
        #plt.show()
        
        fig3=plt.figure(figsize=(15,10))
        ax3=fig3.add_subplot()
        plt.plot(dat['longitud'],dat['profundidad'],'k.')
        plt.plot(corticales['longitud'],corticales['profundidad'],'c.')
        
        
        
    else: 
        print("\n", '#'*30, '\n', "Mc was calculated and no filters were applyed" )