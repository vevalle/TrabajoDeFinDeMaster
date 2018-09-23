# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import csv
import os 
import threading
import json as js
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from time import time #importamos la función time para capturar tiempos
 
rutas = []

# Create your models here.
class Position: 
    def __init__(self, latitude, longitude):
        self.lat = latitude
        self.long = longitude
		
    def show(self): 
        return str(self.long) + "," + str(self.lat) 
      
	  
class Square: 
    def __init__(self, xMin, xMax, yMin, yMax):
        self.center = Position(xMin+((xMax-xMin)/2), yMin+((yMax-yMin)/2))
        self.top_left = Position(xMin, yMax)
        self.top_right = Position(xMax, yMax)
        self.bottom_left = Position(xMin, yMin)
        self.bottom_right = Position(xMax, yMin)
                   
    def show(self):
        dic = {}
        dic['TopLeft'] = (self.top_left.lat, self.top_left.long)
        dic['TopRight'] = (self.top_right.lat, self.top_right.long)
        dic['BottomLeft'] = (self.bottom_left.lat, self.bottom_left.long)
        dic['BottomRight'] = (self.bottom_right.lat, self.bottom_right.long)
        
        return dic
		
		
class Modelo(models.Model):
	
	@classmethod
	def deleteFiles(arg, nFiles):
		i = 0
		while i < nFiles:
			accidents_file_index = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Accidents_" + str(i)+ ".csv")
			if os.path.exists(accidents_file_index): 
				os.remove(accidents_file_index) 
			i = i + 1

	@classmethod
	def inicializateHeader(arg, names):
		header = {}
		i = 0
		names = names.split(',')
		for name in names:
			header[i] = name
			i = i + 1
		return header

	
	@classmethod
	def getInfoAccident(arg, header, attributes):
		info = {}
		attributesPositions = [3, 4, 6, 9, 10, 11, 24, 25, 26, 28, 29]
		for attributesPosition in attributesPositions:
			info[header[attributesPosition]] = attributes[attributesPosition]  
		return info
	
	
	@classmethod
	def getMyHeader(arg, header):
		myHeader = []
		headerPositions = [3, 4, 6, 9, 10, 11, 24, 25, 26, 28, 29]
		i = 0
		for headerPosition in headerPositions:
			myHeader.append(header[headerPosition])
			i = i + 1
		return myHeader

	
	@classmethod
	def showAccident(accident):
		for key in accident: 
			print(key, ":", accident[key])
	 
	 
	@classmethod	
	def calculateMaxMinXY(arg, xMin, xMax, yMin, yMax, latitude, longitude): 
		try:
			if float(xMin) == 999999999.0 or float(xMin) > float(latitude): 
				xMin = float(latitude) 
			if float(xMax) == -999999999.0 or float(xMax) < float(latitude): 
				xMax = float(latitude) 
			if float(yMin) == 999999999.0 or float(yMin) > float(longitude): 
				yMin = float(longitude)
			if float(yMax) == -999999999.0 or float(yMax) < float(longitude): 
				yMax = float(longitude)   
			return xMin, xMax, yMin, yMax
		except: 
			print("Could not")
	
	
	@classmethod
	def sixDecimals(arg, number, nDecimales):
		parts = number.split('.')
		if len(parts) == 2:
			nRealDecimals = len(parts[1])
			if nDecimales < nRealDecimals:
				return float(parts[0]+"."+parts[1][0:nDecimales].replace('}', ''))
			else: 
				return float(parts[0]+"."+parts[1][0:nRealDecimals-1].replace('}', ''))
		else:
			return float(parts[0]+".0")
	
	@classmethod				  
	def calculateSquares(arg, xMin, xMax, yMin, yMax, nCuadrantes, nDecimales):  
		miniSquares = []
		coords = []
		
		xAux = xMin
		yAux = yMax
		
		xDistance = (xMax - xMin)/nCuadrantes 
		yDistance = (yMax - yMin)/nCuadrantes   
		 
		file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Accidents_index.csv')
		with open(file, 'w', newline='') as csvfile:
			csv.writer(csvfile, delimiter=',')
			fieldnames = {"TopLeft", "TopRight", "BottomRight", "BottomLeft"}
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			if os.stat(file).st_size == 0:
				writer.writeheader()
			i = 0
			while i < (nCuadrantes*nCuadrantes):
				square = Square(xAux, xAux+xDistance, yAux-yDistance, yAux)
				miniSquares.append(square)
				writer.writerow(square.show()) 
				
				coordsPolygon = []
				dic = {'lat': Modelo.sixDecimals(str(square.top_left.lat),nDecimales), 'lng': Modelo.sixDecimals(str(square.top_left.long),nDecimales)}
				coordsPolygon.append(dic)
				dic = {'lat': Modelo.sixDecimals(str(square.bottom_right.lat),nDecimales), 'lng': Modelo.sixDecimals(str(square.bottom_right.long),nDecimales)}
				coordsPolygon.append(dic)
				dic = {'lat': Modelo.sixDecimals(str(square.bottom_left.lat),nDecimales), 'lng': Modelo.sixDecimals(str(square.bottom_left.long),nDecimales)}
				coordsPolygon.append(dic)
				dic = {'lat': Modelo.sixDecimals(str(square.top_left.lat),nDecimales), 'lng': Modelo.sixDecimals(str(square.top_left.long),nDecimales)}
				coordsPolygon.append(dic)
				dic = {'lat': Modelo.sixDecimals(str(square.bottom_right.lat),nDecimales), 'lng': Modelo.sixDecimals(str(square.bottom_right.long),nDecimales)}
				coordsPolygon.append(dic)
				dic = {'lat': Modelo.sixDecimals(str(square.top_right.lat),nDecimales), 'lng': Modelo.sixDecimals(str(square.top_right.long),nDecimales)}
				coordsPolygon.append(dic)
				coords.append(coordsPolygon)
				
				i = i + 1
				if i%nCuadrantes == 0: 
					xAux = xMin
					yAux = yAux - yDistance
				else: 
					xAux = xAux + xDistance
			csvfile.close()   
		return miniSquares, coords

	
	@classmethod
	def getNumberOfSquare(arg, miniSquares, position):
		numSquare = 0
		for miniSquare in miniSquares: 
			xMin = float(miniSquare.top_left.lat)
			xMax = float(miniSquare.bottom_right.lat)
			yMin = float(miniSquare.bottom_left.long)
			yMax = float(miniSquare.top_right.long)
			try:
				if float(position.lat) >= xMin and  float(position.lat) <= xMax and float(position.long) <= yMax and float(position.long) >= yMin : 
					return numSquare
				else: 
					numSquare = numSquare + 1 
			except: 
				print("Unable to convert")
		return -1
	
	
	@classmethod	
	def divideMap(arg, json):
		numDiv = int(str(json).split("=")[1].replace("'", ""))
		print(json)
		print(numDiv)
		
		accidents = {}
		locations = []
		coords = []
		numAccidents = []
		
		xMin = 999999999.0
		xMax = -999999999.0
		yMin = 999999999.0
		yMax = -999999999.0  
		
		Modelo.deleteFiles(numDiv*numDiv)
		
		accidents_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Accidents_2016.csv')
		with open(accidents_file, "r") as file: 
			lines = file.read().splitlines()
			header = Modelo.inicializateHeader(lines.pop(0))
			for line in lines: 
				attributes = line.split(',')
				accidentId = attributes[0]
				latitude = attributes[4]
				longitude = attributes[3]
				if latitude is not "" or longitude is not "": 
					accident = Modelo.getInfoAccident(header, attributes)
					accidents[accidentId] = accident
					xMin, xMax, yMin, yMax = Modelo.calculateMaxMinXY(xMin, xMax, yMin, yMax, latitude, longitude)
			
			print("xMin:" + str(xMin))
			print("xMax:"+ str(xMax))
			print("yMin:" + str(yMin))
			print("yMax:"+ str(yMax))
			
			square = Square(xMin, xMax, yMin, yMax); 
			miniSquares, coords = Modelo.calculateSquares(xMin, xMax, yMin, yMax, numDiv, 6)
			
			for miniSquare in miniSquares: 
				locations.append({'lat': Modelo.sixDecimals(str(miniSquare.center.lat),6), 'lng': Modelo.sixDecimals(str(miniSquare.center.long),6)})
				numAccidents.append(0)
			
			for key in accidents: 
				accident = accidents[key]
				position = Position(accident["Latitude"], accident["Longitude"])
				square = Modelo.getNumberOfSquare(miniSquares, position)
				numAccidents[square] = numAccidents[square]+1
				file_square = "Accidents_" + str(square) + ".csv"
				accidents_file_index = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_square)
				with open(accidents_file_index, 'a', newline='') as csvfile:
					csv.writer(csvfile, delimiter=',')
					fieldnames = Modelo.getMyHeader(header)
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					if os.stat(accidents_file_index).st_size == 0:
						writer.writeheader()
					writer.writerow(accident)
				csvfile.close()
		
		return coords, locations, numAccidents
	
	
	@classmethod
	def getMiniSquares(arg, nDecimales): 
		miniSquares = []
		file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Accidents_index.csv')
		with open(file, "r") as file: 
			lines = file.read().splitlines()
			lines.pop(0)
			for line in lines: 
				i = 0
				latitudes = []
				longitudes = []
				# Se eliminan los caracteres especiales y se obtienen los puntos(lat, long) que forman el cuadrante #
				line = line.replace('"', '').replace('(', '').replace(')', '').replace(' ', '')
				positions = line.split(',')
				# Se añade la latitud y la longitud a su respectiva lista en función de la posicion que ocupa #
				for pos in positions: 
					if i%2 == 0: 
						latitudes.append(Modelo.sixDecimals(positions[i],nDecimales))
					else: 
						longitudes.append(Modelo.sixDecimals(positions[i],nDecimales))
					i = i + 1
				# Se construye el cuadrante 
				square = Square(min(latitudes), max(latitudes), min(longitudes), max(longitudes))
				# Se añade el cuadrante a la lista
				miniSquares.append(square)
		return miniSquares
	
	
	@classmethod
	def getArguments(arg, json):
		# Se extraen los valores introducidos en el panel izquierdo de la pantalla
		dic = {} 
		#Chapuza que no se de donde viene 
		parts = str(json).replace("b'", "").split("[")
		arguments = parts[0].split(",")
		for argument in arguments: 
			key_val = argument.replace("{", "").split(":")
			if key_val[0] == '"Time"': 
				dic[key_val[0]] = key_val[1] + ":" + key_val[2]
			else : 
				dic[key_val[0]] = key_val[1]	
		# Se obtienen los puntos de la ruta que devuelve Google Maps
		print(parts[1])
		points = parts[1].split(",")
		return dic, points
	
	@classmethod
	def existePosition(arg, positions, posSearch): 
		for position in positions: 
			if position.lat == posSearch.lat and position.long == posSearch.long: 
				return position
		return Position(-1, -1) 
		
	@classmethod
	def createDicFilePositionsNum(arg, points, miniSquares, nDecimales): 
		# Clasifica las posiciones devueltas por Google Maps en cuandrantes y cuenta el numero de veces que sale en el fichero  
		i = 0
		dic_index_accidents = {}
		
		while i < len(points): 
			# Se extraen los x primeros decimales para comparar con el archivo
			latSearch = Modelo.sixDecimals(str(points[i]['lat']),nDecimales)
			lngSearch = Modelo.sixDecimals(str(points[i]['lng']),nDecimales)
		
			# Se indententifica el cuadrante al que pertenece el punto
			posSearch = Position(float(latSearch), float(lngSearch))
			square = Modelo.getNumberOfSquare(miniSquares, posSearch)
			file_square = "Accidents_" + str(square) + ".csv"  
			# Se crea un diccionario para saber que accidentes estan en cada cuadrante
			# {"Accidents_1.csv: Pos(lat, lng), Pos(lat, lng), ..."} #
			if file_square not in dic_index_accidents:
				positions = []
				positions.append(posSearch)
				dic_index_accidents[file_square] = positions
			else: 
				positions = dic_index_accidents[file_square]
				position = Modelo.existePosition(positions, posSearch)
				if position.lat == -1 and position.long == -1:
					positions.append(posSearch)
				dic_index_accidents[file_square] = positions
			i = i + 2
			
		return dic_index_accidents
	
	@classmethod
	def setConfiguration(arg, str_json):
		json_dat = js.loads(str_json);
		with open('configuration.json', 'w') as file:
			js.dump(json_dat, file)
	
	
	# ---- METODOS PARA LA COMPARACION DE LOS ACCIDENTES DE ACUERDO A LA CONFIGURACION ---- #
	
	@classmethod
	def getNumberMethod(arg, what, method): 
		switcher = {
			'Location':{'5 decimales (Ej. 51.13469)':5, '4 decimales (Ej. 51.1346)':4, '3 decimales (Ej. 51.134)':3, '2 decimales (Ej. 51.13)':2},
			'Date':{'Dia del mes (1, 2, 3, etc)':1, 'Dia de la semana (Lunes, Martes, etc)':2,'Dia de diario / Fin de semana':3}, 
			'Time':{'Hora exacta (Hora y minutos)':1, 'Solo hora':2,'Intervalos de hora similares':3}
		}
		return switcher[what][method]
		
	@classmethod
	def comparativeDate(arg, method, dateForm, dateAccident, dayOfWeekAccident):
		nMethod = Modelo.getNumberMethod("Date", method)
		
		if nMethod == 1:
			return Modelo.sameNumberDay(dateForm[0:2], dateAccident[0:2])
		elif nMethod == 2: 
			return Modelo.sameDayOfWeek(dateForm, dayOfWeekAccident)
		elif nMethod == 3: 
			return Modelo.sameWorkdayOrWeekend(dateForm, dayOfWeekAccident)
			
		return False 
	
	@classmethod
	def sameNumberDay(arg, dayForm, dayAccident):
		if dayForm == dayAccident:
			return True
			
		return False 
	
	@classmethod
	def sameDayOfWeek(arg, dateForm, dayOfWeekAccident):
		day_of_week = datetime.weekday(datetime.strptime(dateForm, "%d/%m/%Y"))+2
		if day_of_week == 8: 
			day_of_week = 1
		if str(day_of_week) == dayOfWeekAccident: 
			return True
			
		return False
	
	@classmethod
	def sameWorkdayOrWeekend(arg, dateForm, dayOfWeekAccident):
		workdays = ['2', '3', '4', '5', '6']
		weekend = ['1', '7']
		
		day_of_week = datetime.weekday(datetime.strptime(dateForm, "%d/%m/%Y"))+2
		if day_of_week == 8: 
			day_of_week = 1
		
		if str(day_of_week) in workdays and dayOfWeekAccident in workdays: 
			return True
		elif str(day_of_week) in weekend and dayOfWeekAccident in weekend: 
			return True
			
		return False
	
	@classmethod
	def comparativeTime(arg, method, timeForm, timeAccident):
		if timeAccident != "":
			nMethod = Modelo.getNumberMethod("Time", method)
			
			if nMethod == 1:
				return Modelo.sameTime(timeForm, timeAccident)
			elif nMethod == 2: 
				return Modelo.sameTime(timeForm[0:2], timeAccident[0:2])
			elif nMethod == 3: 
				return Modelo.getHoursInterval(timeForm[0:2], timeAccident[0:2])
				
		return False 
	
	@classmethod
	def sameTime(arg,timeForm, timeAccident):
		if timeForm == timeAccident:
			return True
			
		return False
	
	@classmethod
	def getHoursInterval(arg, hourForm, hourAccident):
		hour = int(hourAccident)
		if hour >= 0 and hour < 6:
			return hourForm in ["00", "01", "02", "03", "04", "05"]
		elif hour >= 6 and hour < 10 : 
			return hourForm in ["06", "07", "08", "09"]
		elif hour >= 10 and hour < 13: 
			return hourForm in ["10", "11", "12"]
		elif hour >= 13 and hour < 16:
			return hourForm in ["13", "14", "15"]
		elif hour >= 16 and hour < 20: 
			return hourForm in ["16", "17", "18", "19"]
		elif hour >= 20 and hour < 23:
			return hourForm in ["20", "21", "22", "23"]
		
		return False
			
	@classmethod
	def getWeather(arg, index):
		index = int(index)
		if index == 1: 
			return "Soleado"
		elif index == 2:
			return "LLuvioso"
		elif index == 3: 
			return "Nevado"
		elif index == 4: 
			return "Vendaval"
		else:
			return "Otro"
	
	@classmethod
	def getSeverity(arg, index):
		index = int(index)
		if index == 1: 
			return "Grave"
		elif index == 2:
			return "Moderada"
		else: 
			return "Leve"
		

	@classmethod
	def compareCaracteristics(arg, arguments, attributes,config):
		# Si va peor meter los pesos dentro del if
		caracteristics = 1
		weight = 1
		# Comparacion info meteorologica
		if arguments['Weather'].replace('"',"") == Modelo.getWeather(int(attributes[7])):
			caracteristics = caracteristics + 1
			weight = weight + int(config['wWeather'])/100
		# Comparativa fecha 
		if Modelo.comparativeDate(config['mDate'],arguments['Day'].replace('"',""),attributes[3], attributes[4]): 
			caracteristics = caracteristics + 1
			weight = weight + int(config['wDate'])/100
		# Comparacion hora
		if Modelo.comparativeTime(config['mTime'],arguments['Time'].replace('"',""),attributes[5]):
			caracteristics = caracteristics + 1
			weight = weight + int(config['wTime'])/100
		
		return caracteristics, weight
	

	@classmethod
	def getAccidentsInFile(arg,accidents_file_index,positions,arguments,config,accidents_to_show,values,caracteristics,weights):
		nDecimales = int(Modelo.getNumberMethod('Location', config['mLocation']))

		with open(accidents_file_index, "r") as file: 
				# Indica el fichero al que pertenecen los accidentes 
				print(accidents_file_index)
				lines = file.read().splitlines()
				lines.pop(0)
				j = 2
				for line in lines:
					attributes = line.split(',')
					parts = attributes[0].split('.')
					long = float(parts[0]+"."+parts[1][0:nDecimales])
					parts = attributes[1].split('.')
					lat = float(parts[0]+"."+parts[1][0:nDecimales])
					severity = Modelo.getSeverity(attributes[2])
					for pos in positions:
						if pos.lat == lat and pos.long == long:
							accidents_to_show.append({"lat": lat, "lng": long})
							nCaracteristics, weight = Modelo.compareCaracteristics(arguments, attributes, config)
							caracteristics.append(nCaracteristics)
							weights.append(weight)
							#Resumen accidentes panel
							dateToShow = attributes[3] + " " + attributes[5]
							weather = Modelo.getWeather(attributes[7])
							values.append({"date":dateToShow, "weather": weather, "severity": severity})
					j = j + 1


	@classmethod
	def getSquares(arg, arguments):
		global rutas
		rutas = []
		
		tiempo_inicial = time()
		
		# Obtiene los valores de la configuración
		f = open("configuration.json")
		config = js.load(f)
		f.close()

		# Obtiene la precision de la ubicación (numero decimales)
		nDecimales = int(Modelo.getNumberMethod('Location', config['mLocation']))
		
		miniSquares = Modelo.getMiniSquares(nDecimales)
		# Numero de ruta / puntos de esa ruta
		for key, values in arguments['Points'].items():
			print(key)
			print("---------------------------------------------")
			threads = list()
			result = {}
			accidents_to_show = []
			caracteristics = []
			weights = []
			other_values = []
			# accidents_35: [pos, pos, pos, pos], accidents_36: [pos, pos, ...]
			dic_index_accidents = Modelo.createDicFilePositionsNum(values, miniSquares, nDecimales)
			
			# Para cada archivo busco si tengo accidente en esa posicion (por la que ya pasa la ruta)
			for file_square, positions in dic_index_accidents.items():
				accidents_file_index = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_square)
				t = threading.Thread(target=Modelo.getAccidentsInFile, args=(accidents_file_index,positions,arguments,config,accidents_to_show,other_values,caracteristics,weights));
				threads.append(t);
				t.start()
				#Modelo.getAccidentsInFile(accidents_file_index,positions,arguments,config,accidents_to_show,values,caracteristics,weights)
			
			for i in threads:
				i.join()
				
			result['accidents_to_show'] = accidents_to_show
			result['caracteristics'] = sum(caracteristics)
			result['weights'] = sum(weights)
			result['values'] = other_values
			result['coincidences'] = caracteristics
			
			#print(len(result['accidents_to_show']))
			rutas.append(result)
			
		tiempo_final = time() 
		tiempo_ejecucion = tiempo_final - tiempo_inicial
			
		print("Tiempo de ejecucion: " + str(tiempo_ejecucion))
		print("---------------------------------------------")
		
		return Modelo.getBestRoute()
	
	@classmethod
	def getBestRoute(arg):
		better = 999
		pos = 0
		#print(len(rutas))
		for i in range(0, len(rutas)): 
			if len(rutas[i]['accidents_to_show']) != 0:
				clasificacion = rutas[i]['weights']
				#print("La clasificacion es: " + str(clasificacion))
				if clasificacion < better: 
					better = clasificacion
					pos = i
		
		#print("The best is : " + str(pos))
		#print(rutas[pos]['weights'])
		#print(rutas[pos]['caracteristics'])
		
		return rutas[pos]['accidents_to_show'], rutas[pos]['values'], rutas[pos]['coincidences'], pos
	
	@classmethod	
	def getWorstRoute(arg): 
		worst = -999
		pos = 0
		print(len(rutas))
		for i in range(0, len(rutas)): 
			if len(rutas[i]['accidents_to_show']) != 0:
				clasificacion = rutas[i]['weights']
				if clasificacion > worst: 
					worst = clasificacion
					pos = i
		
		print("The worst is : " + str(pos))
		print(rutas[pos]['weights'])
		print(rutas[pos]['caracteristics'])
		
		return rutas[pos]['accidents_to_show'], rutas[pos]['values'], rutas[pos]['coincidences'], pos
	
	@classmethod
	def getMiddleRoute(arg): 
		a, b, c, posBetter = Modelo.getBestRoute()
		a, b, c, posWorst = Modelo.getWorstRoute()

		pos = 0
		
		for x in range(0,3): 
			if x != posBetter and x != posWorst: 
				pos = x
		
		print("The middle is : " + str(pos))
		if pos < len(rutas):
			return rutas[pos]['accidents_to_show'], rutas[pos]['values'], rutas[pos]['coincidences'], pos
		else: 
			return Modelo.getBestRoute()
	
	@classmethod
	def getGraphicValuesTime(arg, hours):  
		list = []
		dic = {'00:00-02:00': 0,'02:00-04:00': 0,'04:00-06:00': 0,'06:00-08:00': 0, '08:00-10:00': 0, '10:00-12:00': 0,'12:00-14:00': 0,'14:00-16:00': 0,'16:00-18:00': 0,'18:00-20:00': 0,'20:00-22:00': 0,'22:00-00:00': 0}
		for hour_group in dic.keys(): 
			hour = int(hour_group.split(":")[0])
			#print(hour)
			if hour < 9: 
				dic[hour_group] = dic[hour_group] + (hours.count('0'+str(hour)) + hours.count('0'+str(hour+1)))
			elif hour == 9: 
				dic[hour_group] = dic[hour_group] + hours.count('0'+str(hour)) + hours.count(str(hour+1))
			else :
				dic[hour_group] = dic[hour_group] + hours.count(str(hour)) + hours.count(str(hour+1))
			list.append([hour_group, dic[hour_group]])
		
		return list
		
	@classmethod
	def getGraphicValuesWeather(arg, weathers):  
		list = []
		#print(weathers)
		dic = {'Soleado': 0,'Vendaval': 0,'LLuvioso': 0, 'Nevado': 0, 'Otro': 0}
		for weather in dic.keys(): 
			dic[weather] = dic[weather] + weathers.count(weather)
			list.append({'name': weather, 'y':dic[weather]})
		
		return list
	
	@classmethod
	def getGraphicValuesSeverity(arg, severitys):  
		list = []
		#print(severitys)
		dic = {'Grave': 0,'Moderada': 0,'Leve': 0}
		for severity in dic.keys(): 
			dic[severity] = dic[severity] + severitys.count(severity)
			list.append({'name': severity, 'y':dic[severity]})
		
		return list
				
	@classmethod
	def getGraphicValues(arg, hours, weathers, severitys): 
		hours = Modelo.getGraphicValuesTime(hours)
		weathers = Modelo.getGraphicValuesWeather(weathers)
		severitys = Modelo.getGraphicValuesSeverity(severitys)
		return hours, weathers, severitys
		
			
	
		