Instrucciones y explicación de código para calcular el espesor sismogénico. 

#######################################################################################

REQUERIMIENTOS

El archivo "espesor_sismogenico.yml" contiene las librerías necesarias y puede ser utilizado en un terminal de Anaconda
para crear un ambiente adecuado para ejecutar el cogido.

Archivos con los siguientes nombres deben encontrarse en el directorio donde se ejecutará el código:

-"slab.txt" Modelo slab2.0 (Hayes, 2018) https://doi.org/10.5066/F7PV6JNV.
-Un archivo .csv que contenga el catálogo sísmico. Este debe contener columnas con la latitud, longitud, profundidad, magnitud, error vertical y error horizontal.
Los nombres de estas columnas deben ser:
latitud
longitud
profundidad
magnitud
err_prof
err_h
Estas columnas solo deben contener valores numéricos. Por ejemplo, en caso de desconocer la magnitud, esta debe quedar en blanco y no como algún otro tipo de carácter (N/A, etc.) 
La profundidad debe estar en kilómetros positivos (ej. 10 km y no -10 km). 

#######################################################################################

INSTRUCCIONES

Además de estas instrucciones se incluye un jupyter notebook (ejemplo.ipynb) donde se ejemplifica la ejecución del código. 
A continuación, se detallan las partes del código y sus variables. 

El cogido se divide en 3 partes:

1. Filtro: 

Para realizar un adecuado cálculo del espesor sismogénico, es necesario filtrar el catálogo.
El código filtra 
 - eliminando sismos mal localizados o sin magnitud (todos aquellos con magnitud o profundidad = 0).
 - eliminando aquellos con magnitud menor a la magnitud de completitud del catalogo.
 - según error en la localización.
 - eliminando todos los sismos que ocurren bajo el slab.
Para este último aspecto, se usa como referencia el modelo slab2.0. Si se desea se puede asignar un rango 
sobre el slab donde los sismos también serán eliminados (considerando que los eventos de subducción no se 
restringen a un único plano delimitado por la superficie del slab) 

Filtrar los datos toma bastante tiempo.
En caso de desconocer la magnitud de completitud, el código permite calcularla mediante el método de curvatura máxima (Maximum Curvature Technique). 
Sin embargo, para poder ejecutar el codigo, es necesario indicar una magnitud de completitud, aunque esta no sea la real.Para evitar esperar a que
se filtre el catálogo antes de calcular la magnitud de completitud, está la opción de ejecutar solo el cálculo de magnitud de completitud o el codigo completo.


-----Variables------
archivo = 'catalog.csv'  - nombre del catálogo sísmico 
sep= ';'                 - separador del archivo .csv
calcular_Mc = "Si"       - Si o No. En caso de Si, solo se ejecutara la sección de Mc. En caso de No, se ejecutará todo el código.
Mc= 1.2                  - Magnitud de completitud. 
err_prof=5               -Error en profundidad máximo permitido para los sismos del catalogo 
err_h=10                 -Error horizontal máximo permitido para los sismos del catalogo
margen_slab= 5           -Margen sobre el slab
margen_moho=0            - Margin above the moho
output= "test.csv"       - Archivo conteniendo los sismos filtrados
latmin = -46             - Limites del area de estudio
latmax = -15
lonmin = -80
lonmax = -60

2. Cálculo del espesor sismogénico utilizando una grilla cuadrada

El código entrega dos opciones para el cálculo del espesor sismogénico, una de ellas es mediante una grilla cuadrada, donde se define el
tamaño de las celdas, un traslape entre ellas, porcentaje de sismos de referencia para el cálculo del espesor y la cantidad de sismos mínima
por celda para que estas sean consideradas estadísticamente validas en el cálculo.

-------Variables-------
corticales = 'corticales.csv' -Archivo .csv que contiene los sismos filtrados. Si se utiliza el resultado del código para filtrar, este se llama corticales.csv
                               y contiene la estructura necesaria para la ejecución del código (misma que la descrita para el archivo que contiene el catalogo
                               original)
crs="EPSG:4323"               -Coordenadas geográficas EPSG:4326 = WGS84 
tamaño_celda=0.1              -El tamaño de las celdas (en unidades de la proyección usada) 
traslape= 0.3                 -Superposición entre celdas, en la unidad de la proyección elegida. Si se agrega traslape, el tamaño final de la celda será igual
                               a tamaño_celda + traslape. Recomiendo elegir un traslape que resulte en un tamaño de celda final divisible por el traslape elegido. 
                               Por ejemplo, tamaño_celda=1, traslape=0.5, para un tamaño final de 1.5, produciendo una superposición de 1/3 entre celdas. 
                               De lo contrario, se formará una grilla irregular. La figura 1 del código puede ayudar a definir estos parámetros.
                               Si se desea trabajar sin traslape, ingresar 0. 
D= 0.05                       -Porcentaje de sismos para el utilizar en el cálculo del espesor sismogénico. En base a esto, se define el espesor sismogénico como la 
                               capa sobre la cual ocurre X% de los sismos, siendo D% = 100 - X. Por ejemplo, si se desea trabajar con el espesor sismogénico siendo la
                               capa sobre la cual ocurre el 95% de los sismos, D =0.05 
k_min= 20                     -Cantidad mínima de sismos por celda
guardar_shp = "No"            -Si/No. Si = se guarda el resultado como un shapefile. No = no se guarda un shapefile.
shp= "shapefile.shp "         -Nombre para guardar archivo. Tiene que ser .shp


3. Cálculo del espesor sismogénico utilizando una grilla circular

Otra opción para el cálculo es utilizar una grilla donde el tamaño de las celdas no es fijo y en su lugar se define en función de una cantidad de sismos dada. En este caso,
se crea una grilla de puntos equidistantes entre sí. Desde cada punto se toma un radio definido (r_min) dentro del cual se calcula la cantidad de sismos. Si dentro de ese radio hay
más de una cantidad definida de sismos (k) ese será el tamaño de la celda. En caso contrario, la celda crecerá, hasta abarcar k sismos, alcanzando un radio maximo definido (r_max)
Es necesario definir el espaciamiento entre los puntos, la cantidad de sismos por celda, el radio mínimo y máximo de las celdas y porcentaje de sismos de referencia para el cálculo 
del espesor sismogenico. 

crs ="EPSG:4326"                -proyección 
corticales = 'corticales.csv'   -Archivo .csv que contiene los sismos filtrados.
espaciamiento=0.1               -Espaciamiento entre celdas en función la unidad de la proyección (grados o metros). Un menor espaciamiento hara el codigo más lento
k=15                            -Cantidad de sismos por celda 
r_max=0.2                       -Distancia máxima (grados o metros, depende de la proyección) hasta los k sismos para considerar la celda valida
r_min=0.1                       -Radio mínimo de las celdas 
D=0.05                          -Porcentaje de sismos para el utilizar en el cálculo del espesor sismogénico.
guardar_shp = "No"              -Si/No
shp= "shapefile.shp "           -Nombre para guardar archivo. Tiene que ser .shp

