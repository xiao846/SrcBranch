import sys,re
from dataStruct import *

def getVars(node):
	if node.condition:
		parser = ConditionParser(node.condition)
		parser.parse()
		return parser.getVars()
	return []




class ConditionSwitcher:
	"""docstring for ConditionSwitcher"""
	def __init__(self, node):
		#super(ConditionSwitcher, self).__init__()
		self.node = node
	def isInOldBranchNodes(self, var):
		func = self.node.getFunctionNode()
		for old_node in func.branchNodes():
			if self.node == old_node or self.node.isSubNode(old_node):
				break
			elif old_node.key == 'case':
				continue
			else:
				Vars = getVars(old_node)
				if var in Vars:
					return True
		return False

	def isInParentNode(self, var):
		parent = self.node.parent
		while isinstance(parent, BranchNode):
			if parent.key != 'if':
				parent = parent.parent
				continue
			Vars = getVars(parent)
			if var in Vars:
				return True
			parent = parent.parent
		return False

	def check(self):
		if isinstance(self.node, BranchNode) == False:
			return
		if self.node.key != 'if' and self.node.key != 'switch': 
			return
		if isinstance(self.node.brother, ContentNode):
			Vars = getVars(self.node)
			for var in Vars:
				match = re.match(r'(?P<var>[\w]+)(\.|->).*', var)
				rep_var = var
				if match:
					rep_var = match.group('var')
				pattern = r'\s*%s\s*=\s*(?P<value>.*?)\s*;\s*' %(rep_var)
				#print pattern
				#print ''.join(self.node.brother.content)
				#print self.node.brother
				#print pattern
				try:
					match = re.match(pattern, str(self.node.brother))
				except:
					match = None
				#if match:
				#	print match.group('value')
				if match and (self.isInParentNode(var) or self.isInOldBranchNodes(var)):
				#if match:
					#new = self.node.condition.replace(var, match.group('value'))
					#print '%s->%s' %(self.node.condition, new)
					#print'switch ok'
					#self.node.condition = new
					self.node.replace(rep_var, match.group('value'))
					if isinstance(self.node.next, BranchNode) and self.node.next.key == 'else':
						self.node.next.replace(rep_var, match.group('value'))
		#elif self.node.brother == None and self.node.parent.key =='else' and self.node.key == 'if':



