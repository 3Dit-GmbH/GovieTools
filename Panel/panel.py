import bpy
from .. Functions import gui_functions
from .. import Properties



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
         
        gui_functions.headline(layout,(0.2,"ACTIVE"),(0.6,"OBJECT NAME"),(1,"VISIBLE"))
                
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
    
        gui_functions.headline(layout,(0.2,"ACTIVE"),(0.4,"OBJECT NAME"),(1,"ANIMATION NAME"))
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

        gui_functions.headline(layout,(0.2,"ACTIVE"),(0.4,"OBJECT NAME"),(1,"TEXT"))
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
                row.prop(scene.export_settings,"use_sampling",text="Use Sampling", toggle = True, icon="OUTLINER_OB_CAMERA")
                row.prop(scene.export_settings,"group_by_nla",text="Group by NLA", toggle = True, icon="NLA")
                row.separator(factor=4)
                row = col.row(align = True)    
                row.separator(factor=4)
                row.prop(scene.export_settings,"export_all_influences",text="Include all Bone Influences", toggle = True, icon="BONE_DATA")
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
        layout.prop(scene,"glb_file_dropdown")
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
