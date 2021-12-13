# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from pprint import pprint
import json
from .lib.checker import nsCheck
from django.views import View
# Create your views here.

class checkerAPI(APIView):
	"""docstring for checkerAPI"""
	def post(self,request):
		domain = request.POST['get_domains']
		# pprint(type(domains))
		# pprint(domains)
		# rVal = []
		g = nsCheck()
		# for domain in domains:
		rVal = g.get_info(domain)
		# rVal.append(res)

		return Response(rVal)


