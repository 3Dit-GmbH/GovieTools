import bpy  # type: ignore

from . import functions


def update_sel_item(self, value):
    scene = self
    list_object = scene.objects[scene.object_index]
    functions.select_object(self, list_object)


def remap_vis_prop(self, value):
    for obj in bpy.context.scene.objects:
        if obj.get("visibility") is not None:
            obj["visibility"] = int(obj.visibility_bool)


def headline(layout, *valueList):
    box = layout.box()
    row = box.row()

    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
