#!/usr/bin/env python
from diffpy.pyfullprof.pcrfilereader import *
from diffpy.pyfullprof.pcrfilewriter import *

class pcrFileHelper:
	def __init__(self):
		self.fit=None
		self.reader=None
		self.param_list=None
		self.refineList=[]
		self.normalList=[]
		self.fixedList=[]
		
	def readFromPcrFile(self,filename=""):
		self.fit=Fit(None)
		if filename=="":
			filename=self.fileName
		pcrfile=open(filename,"r")
		pcr_context=pcrfile.read()
		pcrfile.close()
		pcrfile=open(filename,"w")
		pcr_context=pcr_context.replace("# CRY","CRY")
		print("change ok!") # change the phase name("# CRY")
		pcrfile.write(pcr_context)
		pcrfile.close()
		
		self.reader=ImportFitFromFullProf(str(filename))
		self.reader.ImportFile(self.fit)
		self.param_list=self.fit.Refine.constraints
		self.fileName=str(filename)
		print("read pcr file ok!")

	def getFixedList(self):
		#
		#
		return self.fixedList
		pass


	def getRefineList(self):
		#
		#
		#
		return self.refineList
		pass

	def getNormalList(self):
		#
		#
		#
		return self.normalList
		pass

	def setParam(self,Constraint,CodeWord):
		#
		#
		#
		#
		pass


	def startRefine(self):
		#
		#
		#
		pass


	def setRefineParam(self,index,code=False):
		if code==True:
			if(self.param_list[index].codeWord==0.0):
				self.param_list[index].codeWord=1.0
		if code==False:
			self.param_list[index].codeWord=0.0
	def writeToPcrFile(self,filename):
		if self.fit!=None:
			pcrFileWriter(self.fit,str(filename))
			print("write pcr file ok!")

	@staticmethod 
	def writeToPcrFileFromFit(fit,filename):
		pcrFileWriter(fit,str(filename))
