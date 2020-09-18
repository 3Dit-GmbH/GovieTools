from . import functions

def glb_file_dropdown_update(self,test):
    print(test)
    print(self)

def update_sel_item(self,value):
    scene = self
    list_object = scene.objects[scene.object_index]
    functions.select_object(list_object)
    
def remap_vis_prop(self,value):
    context = value
    if (context.object.get('visibility') is not None):
        context.object["visibility"] = context.object.visibiliy_bool

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])