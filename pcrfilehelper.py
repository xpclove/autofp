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

		# try:
		# 	self.reader.ImportFile(self.fit)
		# except Exception as e:
		# 	print(Exception, ":", e, "in pcrfilehelper.py FromPcrFile")
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
			# self.remove_b_prefix(filename)
			print("write pcr file ok!")


	def remove_b_prefix(filename):
		import re
		"""
		Remove all b'xxx' string prefixes in a text file, converting them to xxx.
		Handles both single and double quoted strings after the b prefix.
		
		Args:
			filename (str): Path to the file to be processed
		"""
		try:
			# Read file content
			with open(filename, 'r', encoding='utf-8') as f:
				content = f.read()
			
			# Pattern matches b'...' or b"..."
			pattern = r"b'(.*?)'"
			
			# Replacement keeps only the inner content
			processed_content = re.sub(pattern, r"\1", content)
			
			# Write back to file
			with open(filename, 'w', encoding='utf-8') as f:
				f.write(processed_content)
				
			print("Successfully processed", filename)
			
		except FileNotFoundError:
			print("Error: File  not found")
		except Exception as e:
			print("Error processing file:")

	@staticmethod 
	def writeToPcrFileFromFit(fit,filename):
		pcrFileWriter(fit,str(filename))
		# self.remove_b_prefix(filename)
		print("write pcr file ok!")
