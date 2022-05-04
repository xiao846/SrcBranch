import sys
from dataStruct import *
from condition import *
import logging
#hahahahahha
class CasesAnalyzer:
	"""docstring for ClassName"""
	def __init__(self, node):
		self.cases = node.cases
		self.node = node

	def _analyzeValue(self, index, key):
		if self.cases[index][key][0] == '>' or self.cases[index][key][0] == '<':
			return True
		array = self.cases[index][key].split(' ')
		if len(array) <=1:
			return True
		not_values = []
		target = None
		for value in array:
			if value[0] == '!':
				not_values.append(value[1:])
			elif target:
				logging.debug('- ' + str(self.cases[index]))
				return False
			else:
				target = value

		if target == None or len(not_values) == 0:
			return True

		if target  in not_values:
			logging.debug('- ' + str(self.cases[index]))
			return False

		self.cases[index][key] = target
		return True
	def _analyzeCase(self, index):
		for key in self.cases[index]:
			if self._analyzeValue(index, key) == False:
				return False
		return True
	def _appendCase(self, cases, case):
		if len(cases) == 0:
			cases.append(case)
		elif case not in cases:
			equal = False
			keyValues = case.items()
			for index in range(len(cases)):
				if len(cases[index]) > len(case):
					equal = True
					old_list = cases[index].items()
					for item in keyValues:
						if item not in old_list:
							equal = False
							break
					if equal :
						cases[index] = case
						break
				elif len(cases[index]) < len(case):
					equal = True
					for item in cases[index].items():
						if item not in keyValues:
							equal = False
							break
					if equal :
						break
			index+=1	
			if equal == False:
				cases.append(case)
	def analyze(self):
		tempCases = []
		for index in range(len(self.cases)):
			if self._analyzeCase(index):
				self._appendCase(tempCases, self.cases[index])
		if len(self.node.cases) > 0 and len(tempCases) == 0:
			self.node.errorInfo = 'bad code!'
			logging.warning('bad code!!!!\n'+ str(self.node.id) +'\n'+ str(self.node))
		self.node.cases = tempCases




