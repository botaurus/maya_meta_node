from __future__ import absolute_import

# Python
import json, traceback
# maya
import maya.cmds as cmds
# package
from . import _utils

_NAMESPACE = _NAMESPACE_ORIGINAL = "_TAA_"

def set_(nodes, name, value = None):
	nodes = _utils.make_list(nodes)

	serialize = False
	if isinstance(value, (list, tuple, int, long, float, bool, dict)):
		value = json.dumps(value)
		serialize = True

	if value is None:
		value = ""

	if not serialize and not isinstance(value, (str, unicode)):
		raise TypeError("{0} type not supported".format(type(value).__name__))

	full_tag = _NAMESPACE+name
	for node in nodes:
		if not has(node, name):
			cmds.addAttr(node, ln=full_tag, dt="string")

		cmds.setAttr(node+"."+full_tag, value, type="string")
		_set_serialized(node, full_tag, serialize)

def get(node, name, default = None):
	node = str(node)
	full_tag = _NAMESPACE + name
	if not cmds.objExists(node+"."+full_tag):
		return default

	value = cmds.getAttr(node+"."+full_tag)
	if _is_serialized(node, full_tag):
		try:
			value = json.loads(value)

		except:
			print "returning default, could not parse: {0}".format(value)
			value = default

	return value
	
def has(node, name):
	return cmds.objExists(str(node)+"."+_NAMESPACE + name)
	
def delete(nodes, name):
	nodes = _utils.make_list(nodes)
	full_tag = _NAMESPACE + name
	for node in nodes:
		if cmds.objExists(node+"."+full_tag):
			cmds.deleteAttr(node+"."+full_tag)

def ls(name, value = None, nodes = None):
	full_tag = _NAMESPACE + name
	if nodes:
		nodes = _utils.make_list(nodes)
		nodes = [x for x in nodes if cmds.objExists(x+"."+full_tag)]
	else:
		nodes = cmds.ls("*."+full_tag, r=1)
		nodes = [x.rpartition(".")[0] for x in nodes]

	if value is None:
		return nodes

	return [x for x in nodes if cmds.getAttr(x+"."+full_tag) == value]

def _is_serialized(node, full_tag):
	full_tag_serialized = full_tag + "_SERIALIZED"
	return cmds.objExists(node + "." + full_tag_serialized)
	
def _set_serialized(node, full_tag, serialize):
	#tag as serialized
	full_tag_serialized = full_tag + "_SERIALIZED"
	serial_tag_exists = cmds.objExists(node + "." + full_tag_serialized)
	if serialize and not serial_tag_exists:
		cmds.addAttr(node, ln=full_tag_serialized, dt="string")

	if not serialize and serial_tag_exists:
		cmds.deleteAttr(node+"."+full_tag_serialized)

def set_namespace(namespace = ""):
	global _NAMESPACE
	_NAMESPACE = namespace

def restore_namespace():
	global _NAMESPACE
	_NAMESPACE = _NAMESPACE_ORIGINAL



class AttributeWrapper(object):
	"""
		Pythonic interface for meta attributes
	"""
	__slots__ = ('_maya_node', '_prefix')

	def __init__(self, maya_node, prefix="_WRAP_"):
		self._maya_node = maya_node
		self._prefix = prefix

	def __getattr__(self, name):
		if name not in self:
			raise AttributeError('Attribute {0} does not exist on {1}.'.format(name, str(self._maya_node)))

		return get(self._maya_node.full_path, self._prefix + name)

	def __setattr__(self, name, value):
		if name in self.__slots__:
			return super(AttributeWrapper, self).__setattr__(name, value)

		return set_(self._maya_node.full_path, self._prefix + name, value)

	def __delattr__(self, name):
		delete(self._maya_node.full_path, self._prefix + name)

	def __len__(self):
		return len(self.__iter__())

	def __iter__(self):
		a = self._prefix
		prefix_len = len(_NAMESPACE+a)
		for name in cmds.listAttr(self._maya_node.full_path, userDefined=True):
			if not name.startswith(_NAMESPACE+self._prefix):
				continue

			yield name[prefix_len:]
		
	def __contains__(self, item):
		for name in self:
			if name == item:
				return True

		return False