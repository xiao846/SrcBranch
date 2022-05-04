import sys,re
from util import *
import logging

class Condition:
	def __init__(self, isNot):
		self.isNot = isNot
		self.brother=None
		self.parent = None
	def setNot(self):
		if self.isNot:
			self.isNot = False
		else:
			self.isNot = True

class ConditonSet(Condition):
	def __init__(self, isNot=False):
		Condition.__init__(self, isNot)
		self.childNodes = []
		self.isEnd=False
		self.lastChild = None
	def append(self, child, isOrType):
		if isOrType or self.lastChild == None:
			self.childNodes.append(child)   #or
			#print 'add || type'
		else:
			#print 'add && type'
			self.lastChild.brother = child  #and
		child.parent = self
		self.lastChild = child
	def __str__(self):
		ret = None
		if self.isNot:
			ret ="!("
		else:
			ret ="("
		for child in self.childNodes:
			if ret[-1] != '(':
				ret = ret + "||"
			while child!=None:
				if ret[-1] != '(' and ret[-1]!='|':
					ret = ret + "&&"
				ret = ret + str(child)
				child = child.brother
		ret = ret +')'
		return ret
	def clearNot(self):
		if self.isNot:
			self.isNot = False
			old_childs = self.childNodes
			self.childNodes = []
			self.lastChild = None
			for child in old_childs:
				if child.brother == None:
					self.append(child, False)
					child.setNot()
					child.clearNot()
				else:
					new_set = None
					if len(old_childs) == 1:
						new_set = self
					else:
						new_set = ConditonSet()
						self.append(new_set, False)
					while child!=None:
						old_child = child
						child = child.brother
						old_child.brother = None
						new_set.append(old_child, True)
						old_child.setNot()
						old_child.clearNot()
		else:
			for child in self.childNodes:
				while child!=None:
					child.clearNot()
					child = child.brother
	def getCase(self, case, index):
		if len(self.childNodes) > 0:
			sub_index = index % len(self.childNodes)
			#print 5%3
			child = self.childNodes[sub_index]
			while child!=None:
				child.getCase(case, index)
				child = child.brother
	def getMaxOrBranch(self):
		now_value = len(self.childNodes)
		for child in self.childNodes:
			while child:
				now_value = max(now_value, child.getMaxOrBranch())
				child = child.brother
		return now_value
	def Cases(self):
		index = self.getMaxOrBranch()
		if index == 0:
			yield {}
		else:
			while index > 0:
				case = {}
				self.getCase(case, index)
				yield case
				index-=1
	def Vars(self):
		for child in self.childNodes:
			while child:
				for var in child.Vars():
					yield var
				child = child.brother



class ConditonElement(Condition):
	def __init__(self, isNot, match):
		Condition.__init__(self, isNot)
		#self.value = None
		if isinstance(match, str):
			self.var = match
			self.value = "true"
		else:
			self.var = match.group("var")
			self.value = match.group("value")
		if self.value == None:
			self.value = "true"
	def __str__(self):
		pre=''
		if self.isNot:
			pre='!'
		return '%s(%s==%s)' %(pre, self.var, self.value)
	def clearNot(self):
		if self.isNot:
			self.isNot = False
			if self.value == "true":
				self.value ="false"
			elif self.value == "false":
				self.value = "true"
			elif self.value[0] == '!':
				self.value = self.value[1:]
			else:
				self.value = '!'+self.value
	def getValue(self):
		return self.value
	def getCase(self, case, index):
		if case.get(self.var) == None:
			case[self.var] = self.getValue()
		else:
			values = case[self.var].split()
			if self.getValue() not in values:
				values.append(self.getValue())
				case[self.var] = ' '.join(values)

	def Vars(self):
		yield self.var

	def getMaxOrBranch(self):
		return 1

class RangeElement(ConditonElement):
	def __init__(self, isNot, match):
		ConditonElement.__init__(self, isNot, match)
		self.mark = match.group("mark")
	def clearNot(self):
		if self.isNot:
			self.isNot = False
			if self.mark == ">":
				self.mark ="<="
			elif self.mark == ">=":
				self.mark = "<"
			elif self.mark == "<":
				self.mark = ">="
			elif self.mark == "<=":
				self.mark = ">"
	def getValue(self):
		return '%s%s' %(self.mark, self.value)
	#def getCase(self, case, index):
	#	if case.get(self.var):
	#		case[self.var] = '%s %s%s' %(case[self.var], self.mark, self.value)
	#	else:
	#		case[self.var] = '%s%s' %(self.mark, self.value)
		

class ConditionParser:
	def __init__(self, condition):
		self.condition = condition.strip()
		self.root = ConditonSet()
		self.conditionPatterns = (
		(r'(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)\s*==\s*(?P<value>[A-Z0-9][a-zA-Z_0-9]*)$',		False),
		(r'(?P<value>[A-Z0-9][a-zA-Z_0-9]*)\s*==\s*(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)$',		False),
		(r'(?P<value>NULL)_POINTER\s*\(\s*([\w]+\s*=\s*)?(\(.*?\))?(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*(\(.*?\))?)\s*\)$',		False),
		(r'(::)?strcmp\(\s*(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*)\s*,\s*(?P<value>\".*?\")\s*\)\s*==\s*0$',		False),
		(r'(::)?strcmp\(\s*(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*)\s*,\s*(?P<value>\".*?\")\s*\)\s*(!=\s*0)?\s*',	True),
		(r'(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))\s*==\s*([a-zA-Z][a-zA-Z_0-9]*::)?(?P<value>[A-Z0-9][\w]*)$',		False),#aa->bb() == cc
		(r'([a-zA-Z][a-zA-Z_0-9]*::)?(?P<value>[A-Z0-9][\w]*)\s*==\s*(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))$',		False),#cc == aa->bb()
		(r'(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))\s*(==\s*(?P<value>(true|false|default)))?$',		False),#aa->bb()
		(r'(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*)\s*(==\s*(?P<value>(true|false|default)))?$',		False), #aa->bb
		(r'((?P<value>(true|false))\s*==)?\s*(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))$',		False),#aa->bb()
		(r'((?P<value>(true|false))\s*==)?\s*(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*)$',		False), #aa->bb
		(r'(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)\s*!=\s*(?P<value>[A-Z0-9][a-zA-Z_0-9]*)\s*',		True),
		(r'(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)\s*!=\s*(?P<value>true|false)\s*',		True),
		(r'(?P<value>[A-Z0-9][a-zA-Z_0-9]*)\s*!=\s*(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)\s*',		True),
		(r'(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))\s*!=\s*([a-zA-Z][a-zA-Z_0-9]*::)?(?P<value>[A-Z0-9][a-zA-Z_0-9]*)',	True),#aa->bb() != cc
		(r'([a-zA-Z][a-zA-Z_0-9]*::)?(?P<value>[A-Z0-9][a-zA-Z_0-9]*)\s*!=\s*(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))\s*', True),#cc == aa->bb()

		(r'(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)\s*(?P<mark>\>=?|\<=?)\s*(?P<value>[A-Z0-9][a-zA-Z_0-9]*)$',	False, True),
		(r'(?P<value>[A-Z0-9][a-zA-Z_0-9]*)\s*(?P<mark>\>=?|\<=?)\s*(?P<var>[a-z][a-zA-Z_0-9\.\-\>\[\]]*)$',	False, True),
		(r'(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))\s*(?P<mark>\>=?|\<=?)\s*([a-zA-Z][a-zA-Z_0-9]*::)?(?P<value>[A-Z0-9][\w]*)$',	False, True),#aa->bb() == cc
		(r'([a-zA-Z][a-zA-Z_0-9]*::)?(?P<value>[A-Z0-9][\w]*)\s*(?P<mark>\>=?|\<=?)\s*(?P<var>[a-zA-Z][a-zA-Z_0-9\.\-\>\[\]]*\(.*?\))$',	False, True),#cc == aa->bb()


		(r'([\w]+\s*=\s*)?(\(.*?\))?(\+\+|\-\-)?(?P<var>[^=]*?)\s*==\s*(\(.*?\))?([a-zA-Z][a-zA-Z_0-9]*(::|\-\>))?(?P<value>\_?[\-A-Z0-9][\w]*)$',		False),
		(r'([\w]+\s*=\s*)?(\(.*?\))?(?P<var>[^=]*?)\s*==\s*(?P<value>true|false)$',		False),
		(r'(\(.*?\))?([a-zA-Z][a-zA-Z_0-9]*(::|\-\>))?(?P<value>\_?[\-A-Z0-9][\w]*)\s*==\s*([\w]+\s*=\s*)?(\(.*?\))?(\+\+|\-\-)?(?P<var>[^=]*?)$',		False),
		(r'([\w]+\s*=\s*)?(\(.*?\))?(\+\+|\-\-)?(?P<var>[^=]*?)\s*!=\s*(\(.*?\))?([a-zA-Z][a-zA-Z_0-9]*(::|\-\>))?(?P<value>\_?[\-A-Z0-9][\w]*)$',		True),
		(r'(\(.*?\))?([a-zA-Z][a-zA-Z_0-9]*(::|\-\>))?(?P<value>\_?[\-A-Z0-9][\w]*)\s*!=([\w]+\s*=\s*)?(\(.*?\))?(\+\+|\-\-)?(?P<var>[^=]*?)\s*$',		True),
		(r'([\w]+\s*=\s*)?(\(.*?\))?(\+\+|\-\-)?(?P<var>[^=]*?)\s*(?P<mark>\>=?|\<=?)\s*(\(.*?\))?([a-zA-Z][a-zA-Z_0-9]*(::|\-\>))?(?P<value>\_?[\-A-Z0-9][\w]*)$', False, True),
		)
		#self.notConditionPatterns = (
		#					)
	def _isMatch(self, text, is_not):
		is_range = False
		for pattern in self.conditionPatterns:
			m = re.match(pattern[0], text)
			if m:
				#print pattern[0]
				if pattern[1]:
					if is_not:
						is_not = False
					else:
						is_not = True
				if len(pattern) ==3:
					is_range = pattern[2]

				return m, is_not, is_range
		return None, is_not, is_range
	#def _isNotMatch(self, text):
	#	for pattern in self.notConditionPatterns:
	#		m = re.match(pattern, text)
	#		if m:
	#			return m
	#	return None


	def parse(self):
		curruntSet = self.root
		target = self.condition
		logging.debug('parse start!')
		logging.debug(target)
		is_not = False
		is_orType = True
		while len(target) > 0:
			#print target
			if target[0] == '(':
				target, is_clear = isBracketNotNeed(target, is_not)
				if is_clear:
					continue
				conditon_set = ConditonSet(is_not)
				is_not = False
				curruntSet.append(conditon_set, is_orType)
				curruntSet = conditon_set
				target = target[1:].strip()
				#print curruntSet
			elif target[0] == ')':
				curruntSet.isEnd = True
				curruntSet = curruntSet.parent
				target = target[1:].strip()
			elif target[0] == '!':
				is_not = True
				target = target[1:].strip()
			elif target[0] == '|' and target[1] == '|':
				is_orType = True
				target = target[2:].strip()
			elif target[0] == '&' and target[1] == '&':
				is_orType = False
				target = target[2:].strip()
			else:
				#print target
				sub_target = subString(target)
				#print "sub_target " + sub_target
				target = target[len(sub_target):].strip()
				sub_target = sub_target.strip()

				#if re.match(r'.*(!=|==|\>=?|\<=?).*', sub_target):
				match, is_not, is_range = self._isMatch(sub_target, is_not)
				if match:
					if is_range:
						element = RangeElement(is_not, match)
					else:
						element = ConditonElement(is_not, match)
				else:
					element = ConditonElement(is_not, sub_target)
					logging.warning(sub_target+' parse Error not find match')
						#break
				#else:
				#	element = ConditonElement(is_not, sub_target)
				curruntSet.append(element, is_orType)
				is_not = False
				logging.debug(element)
		self.root.isEnd = True
		if curruntSet != self.root:
			logging.error('ConditionParser Error')
		else:
			logging.debug('parse OK')
			#print self.root
		self.clearNot()

	def clearNot(self):
		self.root.clearNot()
		#print self.root
	def getCases(self):
		cases = []
		for case in self.root.Cases():
			if case not in cases:
				cases.append(case)
			#appendCase(cases, case)
			#cases.append(case)
		return cases
	def showCases(self):
		for case in self.root.Cases():
			logging.debug(case)
	def getVars(self):
		Vars = []
		for var in self.root.Vars():
			if var not in Vars:
				Vars.append(var)
		return Vars




	def test(self):
		s = "asdfghjkfghasd"
		#s.pop(0)
		print s[1:]
		print s[len('asdf'):]
		print s.replace('fgh', '', 2)

#testCondition = " ! NULL_POINTER(getProperty(\"print.dataSource\"))"
#parser = ConditionParser(testCondition)
#parser.parse()
#parser.clearNot()
#parser.showCases()
#parser.test()