import bpy
from . functions import *
from bpy.props import StringProperty,BoolProperty,IntProperty,PointerProperty


def updateSelItem(self,value):
    scene = self
    selListObj = scene.objects[scene.object_index]
    select_object(selListObj)
    
def remapVisProp(self,value):
    context = value
    if (context.object["visibility"]):
        context.object["visibility"] = context.object.visibiliy_bool

class Export_Settings(bpy.types.PropertyGroup):  
    open_export_settings_menu: BoolProperty(default = False)    
    open_scene_settings_menu: BoolProperty(default = False)    
    open_animation_settings_menu: BoolProperty(default = False)    
    open_compression_settings_menu: BoolProperty(default = False)    
    glb_filename: StringProperty(name="Filename",default="filename")   
    export_selected: BoolProperty(default = False)
    export_lights: BoolProperty(default = False)
    export_animations: BoolProperty(default = True)
    apply_modifiers: BoolProperty(default = False)
    use_sampling:BoolProperty(default = False)
    group_by_nla:BoolProperty(default = True)
    export_image_format: bpy.props.EnumProperty(
        name="Image Compression",
        items=(
               ('AUTO', 'Automatic', 'Determine the image format from the blender image name.'),
               ('JPEG', 'JPEG', 'Convert Images to JPEG, images with alpha still use PNG'),
               ('PNG', 'PNG', 'Convert Images to PNG'),
            ))
    use_draco: BoolProperty(default = True)
    draco_compression_level: IntProperty(default = 6)
    postion_quantization: IntProperty(default = 14,min=0,max=30)
    normal_quantization: IntProperty(default = 10,min=0,max=30)
    texcoord_quantization: IntProperty(default = 12,min=0,max=30)



bpy.utils.register_class(Export_Settings)

bpy.types.Scene.export_settings = PointerProperty(type=Export_Settings)
bpy.types.Scene.object_index = IntProperty(name = "Index for Visibility UI List", default = 0,update=updateSelItem)
bpy.types.Object.visibiliy_bool = BoolProperty(name = "Mapping for Property Value", default = 0,update=remapVisProp)
bpy.types.Scene.open_verification_menu = BoolProperty(default=False)


def run_help_operator(self,context):
   bpy.ops.scene.help_govie(image_name ="help_overlay_govie_tools.png" )

bpy.types.Scene.help_govie_tools = BoolProperty(default=False,update=run_help_operator)

class ANNO_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        
        selOff = 'RADIOBUT_OFF'
        selOn = 'RADIOBUT_ON'
        
        row = layout.row()
        split = row.split(factor=0.2)

        if context.object is not None:
            if (item.name == context.object.name):
                split.label(text="", icon=selOn)
            else :
                split.label(text="", icon=selOff)
            
        split = split.split(factor=0.4)
        split.label(text=item.name)
        split = split.split(factor=1)
        split.prop(item.data, "body", text="")

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        objectList = objects.items()

        # Default return values.
        flt_flags = []
        flt_neworder = []

        flt_flags = [self.bitflag_filter_item if hasattr(obj[1].data, "body") and obj[1].data and obj[1].visible_get() is not "None" else 0 for obj in objectList]

        return flt_flags, flt_neworder

class ANIM_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
       
        if context.object is not None:    
            selOff = 'RADIOBUT_OFF'
            selOn = 'RADIOBUT_ON'

            row = layout.row(align=True)
            split = row.split(factor=0.2)
            if (item.name == context.object.name):
                split.label(text="", icon=selOn)
                split = split.split(factor=0.4)
                split.prop(item, "name", text="")
            else :
                split.label(text="", icon=selOff)
                split = split.split(factor=0.4)
                split.label(text=item.name)  
                
            split = split.split(factor=1)
            if item.animation_data.action:
                split.prop(item.animation_data.action, "name", text="")
        # if item.animation_data.nla_tracks:
        #     split.prop(item.animation_data.nla_tracks[0], "name", text="")


    def filter_items(self, context, data, propname):
        objects_in_scene = data.objects

        # Default return values.
        flt_flags = []
        flt_neworder = []

        flt_flags = [self.bitflag_filter_item if obj.animation_data and obj.animation_data.action and obj.visible_get() else 0 for obj in objects_in_scene]

        return flt_flags, flt_neworder


class VIS_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        
        selOff = 'RADIOBUT_OFF'
        selOn = 'RADIOBUT_ON'

        # 'DEFAULT' and 'COMPACT' layout types should usually use the same draw code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:        
            
            row = layout.row()
            split = row.split(factor=0.2)

            if context.object is not None:
                if (item.name == context.object.name):
                    split.label(text="", icon=selOn)
                    split = split.split(factor=0.6)
                    split.prop(item, "name", text="")
                else :
                    split.label(text="", icon=selOff)
                    split = split.split(factor=0.6)
                    split.label(text=item.name)  

                split = split.split(factor=1)
                split.prop(item, 'visibiliy_bool',text="")

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        objectList = objects.items()

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # get only items that have visibility property
        flt_flags = [self.bitflag_filter_item if obj[1].get(
            "visibility") is not None and obj[1].visible_get() else 0 for obj in objectList]
        

        return flt_flags, flt_neworder

# -------------------------- PANEL -------------------------
def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
    

class VisibilityPropertyPanel(bpy.types.Panel):
    bl_idname = "VIS_PT_custom_prop_panel"
    bl_label = "Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Govie Tools'
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene
         
        headline(layout,(0.2,"ACTIVE"),(0.6,"OBJECT NAME"),(1,"VISIBLE"))
                
        layout.template_list("VIS_UL_List", "", scene,
                             "objects", scene, "object_index")
        layout.operator("object.add_vis_property", text="Add Property")
        layout.operator("object.remove_vis_property", text="Remove Property")



class AnimationPanel(bpy.types.Panel):
    bl_idname = "ANIM_PT_custom_prop_panel"
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Govie Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
    
        headline(layout,(0.2,"ACTIVE"),(0.4,"OBJECT NAME"),(1,"ANIMATION NAME"))
        layout.template_list("ANIM_UL_List", "", scene,"objects", scene, "object_index")
        
class AnnotationPanel(bpy.types.Panel):
    bl_idname = "ANNO_PT_custom_prop_panel"
    bl_label = "Annotation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Govie Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        headline(layout,(0.2,"ACTIVE"),(0.4,"OBJECT NAME"),(1,"TEXT"))
        layout.template_list("ANNO_UL_List", "", scene, "objects", scene, "object_index")
        layout.operator("object.convert_text", text="Convert Text")
        
class GLBExportPanel(bpy.types.Panel):
    bl_idname = "GOVIE_PT_export_panel"
    bl_label = "GLB Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Govie Tools"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene,"open_verification_menu",text="Verification", icon = 'TRIA_DOWN' if scene.open_verification_menu else 'TRIA_RIGHT' )
        if scene.open_verification_menu:
            mat_name_list = context.scene.mat_name_list

            box = layout.box()
            if len(mat_name_list)>0:
                box.label(text="Check Materials :")
                for mat_name in mat_name_list:
                    box.label(text=mat_name)

            box.operator("object.check_tex_nodes", text="Find Empty Image Nodes")
            box.operator("object.cleanup_mesh", text="Cleanup Mesh")


        layout.prop(scene.export_settings,"open_export_settings_menu",text="Export Settings", icon = 'TRIA_DOWN' if scene.export_settings.open_export_settings_menu else 'TRIA_RIGHT' )
        if scene.export_settings.open_export_settings_menu:
            box = layout.box()
            # Scene Settings
            if scene.export_settings.open_scene_settings_menu:
                box.alert = True
            box.prop(scene.export_settings,"open_scene_settings_menu",text="Scene", icon = 'TRIA_DOWN' if scene.export_settings.open_scene_settings_menu else 'TRIA_RIGHT')
            if scene.export_settings.open_scene_settings_menu:
                box.alert = False  

                col = box.column(align = True)
                row = col.row(align = True)           
                row.separator(factor=4)
                row.prop(scene.export_settings,"export_selected",text="Selected Only", toggle = True, icon="RESTRICT_SELECT_OFF")
                row.prop(scene.export_settings,"export_lights",text="Include Lights", toggle = True, icon="LIGHT")
                row.separator(factor=4)
     
                row = col.row(align = True)           
                row.separator(factor=4)
                row.prop(scene.export_settings,"export_animations",text="Include Animation", toggle = True, icon="RENDER_ANIMATION")
                row.prop(scene.export_settings,"apply_modifiers",text="Apply Modifiers", toggle = True, icon="MODIFIER")
                row.separator(factor=4)
    

            # Animation Settings
            if scene.export_settings.open_animation_settings_menu:
                box.alert = True
            box.prop(scene.export_settings,"open_animation_settings_menu",text="Animation", icon = 'TRIA_DOWN' if scene.export_settings.open_animation_settings_menu else 'TRIA_RIGHT' )
            if scene.export_settings.open_animation_settings_menu:
                box.alert = False
                col = box.column(align = True)
                row = col.row(align = True)   
                row.separator(factor=4)   
                row.prop(scene.export_settings,"use_sampling",text="Use Sampling", toggle = True, icon="MODIFIER")
                row.prop(scene.export_settings,"group_by_nla",text="Group by NLA", toggle = True, icon="MODIFIER")
                row.separator(factor=4)

             # Compression Settings
            if scene.export_settings.open_compression_settings_menu:
                box.alert = True
            box.prop(scene.export_settings,"open_compression_settings_menu",text="Compression", icon = 'TRIA_DOWN' if scene.export_settings.open_compression_settings_menu else 'TRIA_RIGHT' )
            if scene.export_settings.open_compression_settings_menu:
                box.alert = False

                col = box.column()
                
                row = col.row(align = True)   
                row.separator(factor=4)  
                row.prop(scene.export_settings,"use_draco",text="Use Draco", toggle = True)
                row.separator(factor=4)  
                if scene.export_settings.use_draco:
                    # Draco Settings
                    row = col.row(align = True)   
                    row.separator(factor=4)  
                    row.prop(scene.export_settings,"export_image_format",text="Format")
                    row.separator(factor=4)  

                    col = box.column(align = True)
                    row = col.row(align = True)   
                    row.separator(factor=4)
                    row.prop(scene.export_settings,"draco_compression_level",text="Compression Level")
                    row.prop(scene.export_settings,"postion_quantization",text="Position Quantisation")
                    row.separator(factor=4)

                    row = col.row(align = True)   
                    row.separator(factor=4)
                    row.prop(scene.export_settings,"normal_quantization",text="Normal Quantisation")
                    row.prop(scene.export_settings,"texcoord_quantization",text="Texture Coord. Quantisation")
                    row.separator(factor=4)

        layout.prop(scene.export_settings,"glb_filename")
        # layout.operator("export_scene.gltf", text="Dialog Export")
        layout.operator("scene.gltf_quick_export", text="Export")
        row = layout.row()
        row.operator("scene.open_folder",icon='FILEBROWSER')
        row.operator("scene.open_web_preview",text="Preview",icon='WORLD')
        
class HelpPanel(bpy.types.Panel):
    bl_idname = "GOVIE_PT_help_panel"
    bl_label = "Help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Govie Tools"
    bl_order = 4

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.operator("scene.open_link",text="Govie Platform",icon='WORLD').url = "https://platform.govie.de/"
        layout.prop(scene,"help_govie_tools",text="Help",icon = 'HELP')
