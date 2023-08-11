Instructions and explanation of the code to calculate seismic thickness

#######################################################################################

REQUIREMENTS: 

The file “espesor_sismogenico.yml” contains the necessary libreries to run the code. It can be used in an Anaconda terminal to create an environment in which to work in. 
The following files need to be on the directory where the code will be executed: 
-"slab.txt" Slab2.0  model (Hayes, 2018) https://doi.org/10.5066/F7PV6JNV. An example file is provided with the code. 
-"moho.txt" File with the moho. An example file is provided with the code. 
-A .csv file containing the seismic catalogue. It must have columns with event latitude, longitude, depth (=profundidad), magnitude, vertical and horizontal error. An example catalogue is provided with the code.  
Column names must be: 
latitud
longitud
profundidad
magnitud
err_prof
err_h
These columns must only contain numerical data and depth must be in positive kilometers.
 
#######################################################################################

INSTRUCTIONS: 

Besides this instructions, a jupyter notebook (ejemplo.ipynb) is provided. It exemplifies code usage. 
Here, each part of the code and its variables are described: 

1. Filter:
The code filters according to:
-	It eliminates events with depth or magnitude fixed at 0
-	Eliminates events with magnitude below the magnitude of completeness of the catalogue 
-	Eliminates events below the slab or moho
-	Eliminates events with high location errors
If the magnitude of completeness is unknown, an option is provided to calculate it graphically using the maximum curvature technique. However, to execute the code it is necessary to indicate a magnitude of completeness, even if it is not correct. It can then be adjusted after calculating it. To avoid having to wait for the filters to run, there is the option to only calculate the magnitude of completeness of the catalogue or to run the whole code. 

-----Variables------

archivo = 'catalog.csv'  – Name of the file with the catalogue 
sep= ';'                 -  Separator of the .csv file
calcular_Mc = "Si"       - Si/No Whether to only calculate the magnitude of completeness or to run the whole code. “Si” = only Mc is calculated. “No” = whole code is run. 
Mc= 1.2                  - Magnitude of completeness  
err_prof=5               -Maximum depth error permitted for the events
err_h=10                 -Maximum horizontal error permitter for the events
margen_slab= 13          -Margin above the slab
margen_moho=0            - Margin above the moho
output= ”test.csv”       - Output file containing the filtered crustal earthquakes
latmin = -46             - Boundaries of the study area
latmax = -15  
lonmin = -80
lonmax = -60

2. Layer depth calculation with square grid method

-------Variables-------

corticales = 'corticales.csv' - .csv file containing the output of the filter (filtered crustal earthquakes)
crs="EPSG:4323"               - Spatial reference system 
tamaño_celda=0.1              -Cell size in units of the selected proyection (crs). 
traslape= 0.3                 -Cell overlap in units of the selected proyection. If overlap is added, then the resulting total cell size will be “tamaño_celda” + “traslape”. Eg. if the values 0.1 and 0.3 are chosen, then the resulting cells will have a total size of 0.4 with 75% overlap.
                               
D= 0.05                       -100 minus the earthquake percentile to use for layer depth calculation. For example, to calculate D95, set value to 0.05.
k_min= 20                     -Minimum number of events per cell for it to be considered satistically relevant.
guardar_shp = "No"            - “Si” / ”No”. Save data to a shapefile, yes or no. Yes = Si, No = No
shp= "shapefile.shp "         -Output shapefile name. 


3. Layer depth calculation with circular grid method

-------Variables-------

crs ="EPSG:4326"                - Spatial reference system
corticales = 'corticales.csv'   -- .csv file containing the output of the filter (filtered crustal earthquakes)
espaciamiento=0.1               - Spacing between the central nodes of each cell in units of the proyection system. Smaller spacing will result in a slower performance of the code.
k=15                            - Number of events per cell
r_max=0.2                       -Maximum distance from the central node to the k th event to consider the cell statistically relevant. 
r_min=0.1                       -Minimum radius of the cells.  
D=0.05                          -100 minus the earthquake percentile to use for layer depth calculation. For example, to calculate D95, set value to 0.05.
guardar_shp = "No"            - “Si” / ”No”. Save data to a shapefile, yes or no. Yes = Si, No = No
shp= "shapefile.shp "         -Output shapefile name. 

