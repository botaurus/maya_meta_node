# Maya
import maya.cmds as cmds
# techart
# package
from . import connections
from . import attributes
from . import _utils as _utils

PREFIX = "_METANODE_"
INTERNAL = "internal_"
META_CLASS_ATTR = PREFIX+INTERNAL+"class"
MAYA_NODE_TYPES = set()
CLASS_MAP = {}

def _qualified_class_name(cls):
	return cls.__module__ + "." + cls.__name__

def register_maya_node_type(type_):
	MAYA_NODE_TYPES.add(type_)

def register_meta_node_classes():
	CLASS_MAP[MetaNode.__name__] = MetaNode
	for cls in _iter_subclasses(MetaNode):
		if cls.QUALIFIED_NAME:
			_CLASS_MAP[_qualified_class_name(cls)] = cls
		else:		
			_CLASS_MAP[cls.__name__] = cls


class MetaNode(object):
	# use the full name of the module + the class name useful when you want
	# several meta nodes to have the same name, but need to distiguish them
	QUALIFIED_NAME = False 

	def __init__(self, dag_path):
		self.node = _utils.OpenMayaNode(dag_path)
		self.attributes = attributes.AttributeWrapper(self.node, prefix=PREFIX+"_mnattr")

	@classmethod
	def bind(cls, dag_path):
		if not cmds.objExists(dag_path+"."+META_CLASS_ATTR):
			if not cls.QUALIFIED_NAME:
				meta_class = cls.__name__
			else:
				meta_class = _qualified_class_name(cls)

			attributes.set_(dag_path, META_CLASS_ATTR, value=meta_class)

		return cls(dag_path)

	def connections(self, attribute=''):
		attribute = PREFIX + attribute
		connections.list_connected(self.node.full_path, attr=attribute)

	def connect(self, children, attribute=''):
		attribute = PREFIX+attribute
		connections.connect(self.node.full_path, children, attr=attribute)

	def disconnect(self, children, attribute=''):
		attribute = PREFIX+attribute
		connections.disconnect(self.node.full_path, children, attr=attribute)


def _get_meta_class_name(dag_path):
	return attributes.get(dag_path, META_CLASS_ATTR, default=None)

def remove_meta():
	pass

def ls(dag_paths=None, meta_type=None):
	if dag_paths == None:
		dag_paths = cmds.ls(type=tuple(MAYA_NODE_TYPES))

		# Convert metaType to a class descriptor.
	if meta_type != None:
		if isinstance(meta_type, basestring):
			meta_type = CLASS_MAP[meta_type]
	else:
		meta_type = MetaNode

	found = []

	for dp in dag_paths:
		class_key = _get_meta_class_name(dp)
		if not class_key:
			continue

		if not class_key in CLASS_MAP:
			continue

		class_ = CLASS_MAP[class_key]
		if meta_type:
			if not issubclass(class_, meta_type):
				continue

		meta_node = class_(dp)
		found.append(meta_node)

	return found


def load(dag_paths, error_on_missing_class_type=True, warning_on_missing_class_type=True):
	return_list = False
	if isinstance(dag_paths, (list, tuple, set)):
		return_list = True

	dag_paths = _utils.make_list(dag_paths)

	# Tries to load them, if it can't, just return the dag
	possible_meta_nodes = []

	for dp in dag_paths:
		if isinstance(dp, MetaNode):
			possible_meta_nodes.append(dp)
			continue

		class_key = _get_meta_class_name(dp)
		if class_key == None:
			possible_meta_nodes.append(dp)
			continue

		if class_key in CLASS_MAP:
			possible_meta_nodes.append(CLASS_MAP[class_key](dp))
		else:
			message = '{0!r} is not a registered MetaNode type.'.format(class_key)
			if error_on_missing_class_type:
				raise ValueError(message)
			else:
				if warning_on_missing_class_type:
					cmds.warning(message)
				possible_meta_nodes.append(node)

	if return_list:
		return possible_meta_nodes
	else:
		return possible_meta_nodes[0]

def _get_subclasses(cls, seen):
	try:
		subs = cls.__subclasses__()
	except TypeError: # fails only when cls is type
		subs = cls.__subclasses__(cls)

	for sub in subs:
		if sub in seen:
			continue
		seen.add(sub)
		yield sub
		for sub in _get_subclasses(sub, seen):
			yield sub

def _iter_subclasses(cls):
	for subclass in _get_subclasses(cls, set()):
		yield subclass


# Start our list of node types and MetaNode classes.
register_maya_node_type('network')
register_meta_node_classes()