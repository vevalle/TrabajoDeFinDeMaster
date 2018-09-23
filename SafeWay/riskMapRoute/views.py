# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from riskMapRoute.models import Modelo
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def divideMap(request):
	received_json_data = request.body
	coordsResponse, locationsResponse, numsResponse = Modelo.divideMap(received_json_data)
	return JsonResponse({"coordenadas": coordsResponse, "ubicaciones": locationsResponse, "nAccidentes": numsResponse})

@csrf_exempt
def getSquares(request):
	data_string = json.loads(request.POST.get('json_data'))
	arguments = {"Day": data_string['Day'],"Time": data_string['Time'],"Weather": data_string['Weather'],"Vehicle": data_string['Vehicle'], "Distance": data_string['Distance'],"Duration": data_string['Duration'],"Points": data_string['Points']}
	posAccidents, values, coincidences, pos = Modelo.getSquares(arguments)
	return JsonResponse({"positions": posAccidents, "values": values, "coincidences": coincidences, "index": pos})

@csrf_exempt
def getBestRoute(request): 
	posAccidents, values, coincidences, pos = Modelo.getBestRoute()
	return JsonResponse({"positions": posAccidents, "values": values, "coincidences": coincidences, "index": pos})

@csrf_exempt
def getWorstRoute(request): 
	posAccidents, values, coincidences, pos = Modelo.getWorstRoute()
	return JsonResponse({"positions": posAccidents, "values": values, "coincidences": coincidences, "index": pos})

@csrf_exempt
def getMiddleRoute(request): 
	posAccidents, values, coincidences, pos = Modelo.getMiddleRoute()
	return JsonResponse({"positions": posAccidents, "values": values, "coincidences": coincidences, "index": pos})

@csrf_exempt
def getGraphicValues(request): 
	data_string = json.loads(request.POST.get('json_data'))
	hours, weathers, severitys = Modelo.getGraphicValues(data_string['Hours'], data_string['Weathers'], data_string['Severitys'])
	return JsonResponse({"hours": hours, "weathers": weathers, "severitys": severitys})
	
@csrf_exempt
def setConfiguration(request):
	received_json_data = request.body
	print(received_json_data)
	Modelo.setConfiguration(received_json_data)
	return JsonResponse({"exito": True})
	
# Create your views here.
class HomePageView(TemplateView):
	def get(self, request, **kwargs):
		return render(request, 'index.html', context=None)
	
