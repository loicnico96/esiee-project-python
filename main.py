# -*- coding: utf-8 -*-

import csv
import json
import math
import numpy
import urllib.request
import os, os.path
import zipfile
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as basemap
import matplotlib.patches as mpatches


# File uncompression function
def unzip (zip_name):
	output_dir = os.path.splitext (zip_name) [0]
	with zipfile.ZipFile (zip_name) as zip_file: 
		for file_name in zip_file.namelist ():
			zip_file.extract (file_name, output_dir)

# Proxy settings
proxy_address = "http://147.215.1.189:3128/"
proxy = urllib.request.ProxyHandler ({ "http" : proxy_address })
proxy_opener = urllib.request.build_opener (proxy)
urllib.request.install_opener (proxy_opener)

			


data = []

# Histogram parameters
HIST_TITLE	= "Hôtels classés en Ile-de-France"
HIST_X_AXIS	= "Capacité d'accueil"
HIST_Y_AXIS	= "Nombre d'hôtels"
HIST_KEY	= "capacite_d_accueil_personnes"
HIST_BIN	= 50
HIST_COLOR	= "#0000FF"
HIST_ALPHA	= 0.5

# Downloading database (CSV format)
url_data = "http://data.iledefrance.fr/explore/dataset/les_hotels_classes_en_ile-de-france/download?format=csv"
urllib.request.urlretrieve (url_data, "database.csv")

# Reading database
with open ("database.csv", "r", encoding = "utf8") as csv_file:
	csv_reader = csv.DictReader (csv_file, delimiter = ";")
	for row in csv_reader:
		if row[HIST_KEY] != '':
			data.append (row)



# Extracting values
hist_values	= [int(row[HIST_KEY]) for row in data]

# Calculating histogram classes
hist_bins	= [x * HIST_BIN for x in range (0, math.ceil(max(hist_values) / HIST_BIN))]
# Creating histogram
plt.hist (hist_values, facecolor = HIST_COLOR, alpha = HIST_ALPHA, bins = hist_bins)
# Displaying histogram
plt.title (HIST_TITLE)
plt.xlabel (HIST_X_AXIS)
plt.ylabel (HIST_Y_AXIS)
plt.axis([0, 1000, 0, 900]) #Nous n'avons pas mis dans l'histogramme les valeurs très grandes pour une meilleure lisibilité.
plt.grid (True)

# Displaying statistics
plt.text (220, 810, "Il y a %d hôtels classés en Ile-de-France" % len (hist_values)) 
plt.text (220, 760,"avec une capacité totale de %d personnes." % sum (hist_values))
plt.text (220, 710, "La capacité varie de %d à %d personnes par hôtel." % (min (hist_values), max (hist_values)))
plt.text (220, 660, "La médiane est : %d." % numpy.median (hist_values))
plt.text (220, 610, "La moyenne est : %.2f." % numpy.average (hist_values))
plt.text (220, 560, "La variance est : %.2f." % numpy.var (hist_values))
plt.text (220, 510, "L'écart-type est : %.2f." % numpy.std (hist_values))

plt.show ()
	
	


# Map parameters
BMAP_TITLE	= "Capacité des hôtels en Ile-de-France"
BMAP_TITLE_2= "Nombre de chambres des hôtels en Ile-de-France"
BMAP_LONMIN	= 1.2
BMAP_LONMAX	= 3.8
BMAP_LATMIN	= 48.0
BMAP_LATMAX	= 49.4
BMAP_MARKER	= "o"
BMAP_ALPHA	= 0.65
BMAP_URL	= "http://public.opendatasoft.com/explore/dataset/geoflar-departements/download/?format=shp&timezone=Europe/Berlin"

# Downloading map shapefiles (ZIP file)
urllib.request.urlretrieve (BMAP_URL, "map_bounds.zip")
# Extracting compressed files
unzip ("map_bounds.zip")
# Removing ZIP file
os.remove ("map_bounds.zip")

# Calculating points to display
plons, plats, pcap, pstars = [], [], [], []
# Extracting department lists
depts = { row["dept"] for row in data }
# Extracting data for each departement
for dept in depts:
	
	# Obtaining the list of hotels for this department
	hotels = [row for row in data if row["dept"] == dept]
	# Calculating mean of longitudes
	if dept!="92":
		plons.append (sum ([float(hotel["lng"]) for hotel in hotels]) / len (hotels))
	else:
		plons.append ((sum ([float(hotel["lng"]) for hotel in hotels]) / len (hotels))-0.05)
		# Special case because of the shape of this department

	# Calculating mean of latitudes
	plats.append (sum ([float(hotel["lat"]) for hotel in hotels]) / len (hotels))
	# Calculating total capacity
	pcap.append (sum ([int(hotel[HIST_KEY]) for hotel in hotels]))
	# Calculating mean of rankings (in stars)
	pstars.append (sum ([int(hotel["classement"].split()[0]) for hotel in hotels]) / len (hotels))
	
	
# Calculating size and color of points (values between 0 and 1)

plt.winter()

psizes = [s / 85 for s in pcap]

# Displaying map background
bmap = basemap (projection = "merc", llcrnrlon = BMAP_LONMIN, llcrnrlat = BMAP_LATMIN, urcrnrlon = BMAP_LONMAX, urcrnrlat = BMAP_LATMAX)
# Displaying shape boundaries
bmap.readshapefile ("map_bounds/geoflar-departements", "map_bounds", drawbounds = True)
# Displaying points
plons, plats = bmap (plons, plats)
bmap.scatter (plons, plats, s = psizes, c= pstars, alpha = BMAP_ALPHA, marker = BMAP_MARKER)

# Displaying keys
leg_etoilefaible= mpatches.Rectangle((1,2), height = 1, width = 2, facecolor = (89/255,89/255,1))
leg_etoileeleve = mpatches.Rectangle((1,3), height = 1, width = 2, facecolor=(89/255,1,172/255))
plt.legend([leg_etoilefaible,leg_etoileeleve],["Nombre moyen d'étoiles faible","Nombre moyen d'étoiles élevé"] , loc =4)

# Displaying map
plt.title (BMAP_TITLE)
plt.show ()



# Displaying map background
bmap = basemap (projection = "merc", llcrnrlon = BMAP_LONMIN, llcrnrlat = BMAP_LATMIN, urcrnrlon = BMAP_LONMAX, urcrnrlat = BMAP_LATMAX)
# Displaying shape boundaries
bmap.readshapefile ("map_bounds/geoflar-departements", "map_bounds", drawbounds = True)
# Displaying points
plons, plats = bmap ([float(row["lng"]) for row in data], [float(row["lat"]) for row in data])
bmap.scatter (plons, plats, s = [int(row["nombre_de_chambres"]) / 5 for row in data], c= [colors.hsv_to_rgb((120 * (int(row["classement"].split()[0]) - 1) / 4 / 360, 1, 1)) for row in data], alpha = BMAP_ALPHA, marker = BMAP_MARKER)

# Displaying keys
leg_etoilefaible= mpatches.Rectangle((1,2), height = 1, width = 2, facecolor = (232/255,24/255,24/255))
leg_etoilemoyen = mpatches.Rectangle((1,3), height = 1, width = 2, facecolor=(1,1,89/255))
leg_etoileeleve = mpatches.Rectangle((1,4), height = 1, width = 2, facecolor=(115/255,223/255,0))
plt.legend([leg_etoilefaible,leg_etoilemoyen,leg_etoileeleve,],["Nombre d'étoiles faible","Nombre d'étoiles moyen","Nombre d'étoiles élevé"] , loc =4)

# Displaying map
plt.title (BMAP_TITLE_2)
plt.show ()
