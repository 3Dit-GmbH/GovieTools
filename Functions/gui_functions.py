from . import functions
import bpy

def update_sel_item(self,value):
    scene = self
    list_object = scene.objects[scene.object_index]
    functions.select_object(list_object)
    
def remap_vis_prop(self,value):
    for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if obj.get('visibility') is not None:
                    obj["visibility"] = obj.visibiliy_bool

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])