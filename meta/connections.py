from __future__ import absolute_import

# maya
import maya.cmds as cmds
# package
from . import _utils

_NAMESPACE = _NAMESPACE_ORIGINAL = "_CONN_"

def connect(parent, children, attr = "meta"):
	children = _utils.make_list(children)
	parent = str(parent)

	full_attr = _NAMESPACE + attr
	if not cmds.objExists(parent+"."+full_attr):
		cmds.addAttr(parent, ln=full_attr, multi =1, at="message")
	
	for child in children:
		connected = cmds.listConnections(parent+"."+full_attr)
		if child in connected: continue

		if len(connected) == 0:
			count = 0
		else:
			res = cmds.getAttr(parent+"."+full_attr, mi=1)
			res.sort()
			count = res[-1] + 1

		cmds.connectAttr("{0}.message".format(child), parent+"."+full_attr+("[%i]"%count), f=1)

def disconnect(parent, children, attr = "meta"):
	children = _utils.make_list(children)
	parent = str(parent)
	full_attr = _NAMESPACE+attr
	for child in children:
		for conn in cmds.listConnections("{0}.message".format(child), p=1):
			if conn.find(full_attr)>-1 and conn.find(parent)>-1:
				cmds.disconnectAttr("{0}.message".format(child), conn)

def delete_connection(parent, attr = "meta"):
	parent = str(parent)
	full_attr = _NAMESPACE + attr
	if cmds.objExists(parent+"."+full_attr):
		cmds.deleteAttr(parent+"."+full_attr)

def list_connected(parent, attr = "meta"):
	parent = str(parent)
	full_attr = _NAMESPACE + attr
	if cmds.objExists(parent +"."+full_attr):
		return cmds.listConnections(parent +"."+full_attr)
	else:
		return []

def has_connection(parent, attr = "meta"):
	parent = str(parent)
	full_attr = _NAMESPACE + attr
	return cmds.objExists(parent+"."+full_attr)

def parent(children, parent):
	children = _utils.make_list(children)
	parent = str(parent)
	for child in children:
		current_parents = list_connected(child, "parent")
		if current_parents:
			for current_parent in current_parents:
				disconnect(current_parent, child, attr="children")
		connect(parent, child, attr="children")
		delete_connection(child, attr="parent")
		connect(child, parent, attr = "parent")

def unparent(children):
	children = _utils.make_list(children)
	for child in children:
		current_parents = list_connected(child, "parent")
		if current_parents:
			for current_parent in current_parents:
				disconnect(current_parent, child, attr="children")
		delete_connection(child, attr="parent")

def list_children(parent):
	parent = str(parent)
	return list_connected(parent, "children")

def set_tag_namespace(namespace = ""):
	global _NAMESPACE
	_NAMESPACE = namespace

def restore_tag_namespace():
	global _NAMESPACE
	_NAMESPACE = _NAMESPACE_ORIGINAL