import maya.OpenMaya as om

def make_list(obj):
	if obj == None:
		return type_()

	if isinstance(obj, list):
		return obj

	return list((obj,))

class OpenMayaNode(object):
	def __init__(self, dag_path):
		sel_list = om.MSelectionList()
		sel_list.add(dag_path)
		self.mobj = om.MObject()
		sel_list.getDependNode(0, self.mobj)

	def __str__(self):
		return self.path

	@property
	def path(self):
		if om.MObject.hasFn(self.mobj, om.MFn.kDagNode):
			dp = om.MDagPath()
			om.MDagPath.getAPathTo(self.mobj, dp)
			return dp.partialPathName()
		else:
			dp = om.MFnDependencyNode(self.mobj)
			return dp.name()

	@property
	def full_path(self):
		if om.MObject.hasFn(self.mobj, om.MFn.kDagNode):
			dp = om.MDagPath()
			om.MDagPath.getAPathTo(self.mobj, dp)
			return dp.fullPathName()
		else:
			dp = om.MFnDependencyNode(self.mobj)
			return dp.name()