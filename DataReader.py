import sys
from dataStruct import *
from CasesAnalyzer import *
from ConditionSwitcher import *
import logging

class DataReader:
	def __init__(self, node):
		self.rootNode = node
		self.currentNode = None
		self.index = -1
		self.checkCondition()
		self.parseAllConditions()
		self.checkCases()
	def showRawData(self):
		self.rootNode.show()

	def parseAllConditions(self):
		self.rootNode.parseAllConditions()

	def FunctionNodes(self):
		for node in self.rootNode.nodes:
			if isinstance(node, FunctionNode):
				yield node

	def checkCondition(self):
		for func in self.FunctionNodes():
			for node in func.branchNodes():
				ConditionSwitcher(node).check()

	def checkCases(self):
		for func in self.FunctionNodes():
			logging.debug(func.id)
			logging.debug(func)
			for content in func.contentNodes():
				logging.debug(content.id)
				analyzer = CasesAnalyzer(content)
				analyzer.analyze()
				for case in content.cases:
					logging.debug(case)
				logging.debug(content)

	def nextFunction(self):
		self.index += 1
		if self.index < len(self.rootNode.nodes):
			self.currentNode = self.rootNode.nodes[self.index]
			return True
		return False

	def readFuncName(self):
		return self.currentNode.name

	def readFuncArgs(self):
		return self.currentNode.arg.strip().split(',')

	def readFuncNameAndArgs(self):
		return '%s(%s)' %(self.currentNode.name, self.currentNode.arg.strip())

	def readFuncRetType(self):
		return self.currentNode.retType

	def branches(self):
		for node in self.currentNode.branchNodes():
			if node.isDiff:
				yield str(node)

	def inputVars(self):
		vars = []
		for content in self.currentNode.contentNodes():
			for case in content.cases:
				for var in case:
					if var not in vars:
						vars.append(var)
		return vars

	def readUTItems(self):
		items = []
		for content in self.currentNode.contentNodes():
			if content.cases and len(content.cases[0]) > 0:
				item = []
				item.append(content.cases)
				item.append(str(content))
				items.append(item)
		return items

	def readTotalSteps(self):
		return self.currentNode.getLines()
