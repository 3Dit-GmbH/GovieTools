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
            else:
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

        flt_flags = [self.bitflag_filter_item if hasattr(
            obj[1].data, "body") and obj[1].data and obj[1].visible_get() is not "None" else 0 for obj in objectList]

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
            else:
                split.label(text="", icon=selOff)
                split = split.split(factor=0.4)
                split.label(text=item.name)

            split = split.split(factor=1)
                
            if hasattr(item.animation_data,"nla_tracks") and len(item.animation_data.nla_tracks) > 0:
                split.prop(item.animation_data.nla_tracks[0], "name", text="")
            elif item.animation_data.action:
                split.prop(item.animation_data.action, "name", text="")

    def filter_items(self, context, data, propname):
        objects_in_scene = data.objects

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # flt_flags = [self.bitflag_filter_item if obj.animation_data and obj.animation_data.action and obj.visible_get(
        # ) else 0 for obj in objects_in_scene]
        flt_flags = [self.bitflag_filter_item if  hasattr(obj.animation_data,"nla_tracks") > 0 and obj.visible_get(
        ) else 0 for obj in objects_in_scene]

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
                else:
                    split.label(text="", icon=selOff)
                    split = split.split(factor=0.6)
                    split.label(text=item.name)

                split = split.split(factor=1)
                split.prop(item, 'visibiliy_bool', text="")

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
        
        # ANIMATION
        layout.prop(scene,"open_animation_manage",text="Manage Animation", icon = 'TRIA_DOWN' if scene.open_animation_manage else 'TRIA_RIGHT' )
        if scene.open_animation_manage:
            layout.separator(factor=0.1)
            row = layout.row()
            row.separator(factor=0.1)
            box = row.box()

            box.prop(scene.animation_settings,"join_anim_name",text="Name")
            box.operator("scene.join_anim", text="Join Animation").anim_name = scene.animation_settings.join_anim_name
            box.operator("scene.rename_anim", text="Rename Animation").anim_name = scene.animation_settings.join_anim_name
            box.operator("scene.seperate_anim", text="Seperate Animation")
            row.separator(factor=0.1)
            layout.separator(factor=0.1)


        
        layout.prop(scene,"open_animation_particle",text="Bake Particles", icon = 'TRIA_DOWN' if scene.open_animation_particle else 'TRIA_RIGHT' )
        if scene.open_animation_particle:
            layout.separator(factor=0.1)
            row = layout.row()
            row.separator(factor=0.1)
            box = row.box()

            # particle settings
            row = box.row()
            row.prop(scene.particle_settings,"key_loc",text="Key Location")
            row.prop(scene.particle_settings,"key_rot",text="Key Rotation")
             
            row = box.row()
            row.prop(scene.particle_settings,"key_scale",text="Key Scale")
            row.prop(scene.particle_settings,"key_vis",text="Key Visibility")
            row = box.row()
            row.prop(scene.particle_settings,"frame_offset",text="Frame Offset")
            row.prop(scene.particle_settings,"collection_name",text="")

            # Bake Operator
            row = box.row()
            bake_particle_op = row.operator("object.bake_particles", text="Bake Particles")
            bake_particle_op.KEYFRAME_LOCATION = scene.particle_settings.key_loc
            bake_particle_op.KEYFRAME_ROTATION = scene.particle_settings.key_rot
            bake_particle_op.KEYFRAME_SCALE = scene.particle_settings.key_scale
            bake_particle_op.KEYFRAME_VISIBILITY = scene.particle_settings.key_vis

            row.separator(factor=0.1)
            layout.separator(factor=0.1)
        
        
        layout.prop(scene,"open_animation_simplifly",text="Simplify Animation", icon = 'TRIA_DOWN' if scene.open_animation_simplifly else 'TRIA_RIGHT' )
        if scene.open_animation_simplifly:
            layout.separator(factor=0.1)
            row = layout.row()
            row.separator(factor=0.1)
            box = row.box()
            row = box.row()
            row.prop(scene.animation_settings,"simplify_keyframes_enum",text="")
            row.prop(scene.animation_settings,"decimate_ratio",text="")
            simplify_keyframe_op = layout.operator("scene.simplify_keyframes",text="Simplify Keyframes")
            simplify_keyframe_op.mode = scene.animation_settings.simplify_keyframes_enum
            simplify_keyframe_op.decimate_ratio = scene.animation_settings.decimate_ratio
            row.separator(factor=0.1)
            layout.separator(factor=0.1)
        

class VisibilityPropertyPanel(bpy.types.Panel):
    bl_idname = "VIS_PT_custom_prop_panel"
    bl_label = "Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Govie Tools'
    bl_order = 4

    def draw(self, context):
        layout = self.layout
        scene = context.scene
         
        gui_functions.headline(layout,(0.2,"ACTIVE"),(0.6,"OBJECT NAME"),(1,"VISIBLE"))
                
        layout.template_list("VIS_UL_List", "", scene,
                             "objects", scene, "object_index")
        layout.operator("object.add_vis_property", text="Add Property")
        layout.operator("object.remove_vis_property", text="Remove Property")


class GLBExportPanel(bpy.types.Panel):
    bl_idname = "GOVIE_PT_export_panel"
    bl_label = "GLB Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Govie Tools"
    bl_order = 5

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
                row.separator(factor=1)
                row.prop(scene.export_settings,"export_selected",text="Selected Only", toggle = True, icon="RESTRICT_SELECT_OFF")
                row.prop(scene.export_settings,"export_lights",text="Include Lights", toggle = True, icon="LIGHT")
                row.separator(factor=1)
     
                row = col.row(align = True)           
                row.separator(factor=1)
                row.prop(scene.export_settings,"export_animations",text="Include Animation", toggle = True, icon="RENDER_ANIMATION")
                row.prop(scene.export_settings,"apply_modifiers",text="Apply Modifiers", toggle = True, icon="MODIFIER")
                row.separator(factor=1)
    

            # Animation Settings
            if scene.export_settings.open_animation_settings_menu:
                box.alert = True
            box.prop(scene.export_settings,"open_animation_settings_menu",text="Animation", icon = 'TRIA_DOWN' if scene.export_settings.open_animation_settings_menu else 'TRIA_RIGHT' )
            if scene.export_settings.open_animation_settings_menu:
                box.alert = False
                col = box.column(align = True)
                row = col.row(align = True)   
                row.separator(factor=1)   
                row.prop(scene.export_settings,"use_sampling",text="Use Sampling", toggle = True, icon="OUTLINER_OB_CAMERA")
                row.prop(scene.export_settings,"group_by_nla",text="Group by NLA", toggle = True, icon="NLA")
                row.separator(factor=1)
                row = col.row(align = True)    
                row.separator(factor=1)
                row.prop(scene.export_settings,"export_all_influences",text="Include all Bone Influences", toggle = True, icon="BONE_DATA")
                row.separator(factor=1)

             # Compression Settings
            if scene.export_settings.open_compression_settings_menu:
                box.alert = True
            box.prop(scene.export_settings,"open_compression_settings_menu",text="Compression", icon = 'TRIA_DOWN' if scene.export_settings.open_compression_settings_menu else 'TRIA_RIGHT' )
            if scene.export_settings.open_compression_settings_menu:
                box.alert = False

                col = box.column()
                row = col.row(align = True)   
                row.separator(factor=1)
                row.prop(scene.export_settings,"export_image_format",text="Format")
                row.separator(factor=1)
                row = col.row()
                row.separator(factor=1)
                row.prop(scene.export_settings,"use_draco",text="Use Draco", toggle = True)
                row.separator(factor=1)

                if scene.export_settings.use_draco:
                    # Draco Settings
                    col = box.column(align = True)
                    row = col.row(align = True)   
                    row.separator(factor=1)
                    row.prop(scene.export_settings,"draco_compression_level",text="Compression Level")
                    row.prop(scene.export_settings,"postion_quantization",text="Position Quantisation")
                    row.separator(factor=1)

                    row = col.row(align = True)   
                    row.separator(factor=1)
                    row.prop(scene.export_settings,"normal_quantization",text="Normal Quantisation")
                    row.prop(scene.export_settings,"texcoord_quantization",text="Texture Coord. Quantisation")
                    row.separator(factor=1)

        layout.prop(scene.export_settings,"glb_filename")
        layout.prop(scene,"glb_file_dropdown")
        # layout.operator("export_scene.gltf", text="Dialog Export")
        layout.operator("scene.gltf_quick_export", text="Export")
        row = layout.row()
        row.operator("scene.open_export_folder",icon='FILEBROWSER')
        row.operator("scene.open_web_preview",text="Preview",icon='WORLD')
        
class HelpPanel(bpy.types.Panel):
    bl_idname = "GOVIE_PT_help_panel"
    bl_label = "Help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Govie Tools"
    bl_order = 6

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.label(text="To use the full potential of the add-on, ")
        layout.label(text=" you may sign up for a free govie account")
        layout.operator("scene.open_link",text="Govie Platform",icon='WORLD').url = "https://platform.govie.de/register#/?utm_source=blender-add-on&utm_medium=button"


        layout.label(text="Find help on how to use the add-ons and the govie editor")
        layout.operator("scene.open_link",text="Add-on Documentation",icon='HELP').url = "https://govie.de/tutorials-blender/?utm_source=blender-add-on&utm_medium=button#govie_tools"
        layout.operator("scene.open_link",text="Govie Tutorial",icon='HELP').url = "https://govie.de/tutorials?utm_source=blender-add-on&utm_medium=button"
