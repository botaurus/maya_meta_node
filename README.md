# Maya Meta Node
Inspired by the red9 meta node
http://red9-consultancy.blogspot.com/
and notes from here
https://sites.google.com/site/mayariggingwiki/rigging-notes/modular-rigging/building-a-metadata-node-network

This has not been used much, its just an initial pass. The red9 package has a more mature meta node - but I found I had to do some ugly work arounds when using it so I built this.
# Usage

```
import maya.cmds as cmds
import maya_meta_node.meta.node as node
import maya_meta_node.meta.attributes as attributes

cube = cmds.polyCube()[0]
res = node.MetaNode.bind(cube)
res.attributes.somedata = "this is some meta data"

for x in node.ls():
	print x.attributes.somedata
```
