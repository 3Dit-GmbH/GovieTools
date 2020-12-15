import bpy
import os, fnmatch
from .. Functions import gui_functions
from bpy.props import StringProperty,BoolProperty,IntProperty,PointerProperty,EnumProperty,FloatProperty



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
    export_colors: BoolProperty(default = True)
    use_sampling:BoolProperty(default = False)
    group_by_nla:BoolProperty(default = True)
    export_all_influences:BoolProperty(default = False)
    export_image_format:EnumProperty(
        name="Image Compression",
        items=(
               ('AUTO', 'Automatic', 'Determine the image format from the blender image name.'),
               ('JPEG', 'JPEG', 'Convert Images to JPEG, images with alpha still use PNG')
            ))
    use_draco: BoolProperty(default = True)
    draco_compression_level: IntProperty(default = 6)
    postion_quantization: IntProperty(default = 14,min=0,max=30)
    normal_quantization: IntProperty(default = 10,min=0,max=30)
    texcoord_quantization: IntProperty(default = 12,min=0,max=30)



bpy.utils.register_class(Export_Settings)

bpy.types.Scene.export_settings = PointerProperty(type=Export_Settings)
bpy.types.Scene.object_index = IntProperty(name = "Index for Visibility UI List", update=gui_functions.update_sel_item)
bpy.types.Object.visibiliy_bool = BoolProperty(name = "Mapping for Property Value", update=gui_functions.remap_vis_prop)
bpy.types.Scene.open_verification_menu = BoolProperty(default=False)

class ParticleSettings(bpy.types.PropertyGroup):
    key_loc: BoolProperty(name="Key Location", default=1)
    key_rot: BoolProperty(name="Key Rotation", default=1)
    key_scale: BoolProperty(name="Key Scale", default=1)
    key_vis: BoolProperty(name="Key Visibility", default=0)
    frame_offset: IntProperty(name="Frame Offset", default=1)
    collection_name: StringProperty(
        name="Collection Name", default="Collection Name")


bpy.utils.register_class(ParticleSettings)
bpy.types.Scene.particle_settings = PointerProperty(type=ParticleSettings)


class AnimationSettings(bpy.types.PropertyGroup):
    simplify_keyframes_modes = [
        ("RATIO", "RATIO",
         "Use a percentage to specify how many keyframes you want to remove."),
        ("ERROR", "ERROR ", "Use an error margin to specify how much the curve is allowed to deviate from the original path.")
    ]

    simplify_keyframes_enum: EnumProperty(
        name='Simplify Mode', description='Choose mode to decimate keyframes', items=simplify_keyframes_modes)
    join_anim_name: StringProperty(
        name="Animation Name", default="Animation Name")
    decimate_ratio: FloatProperty(name="Decimate Ratio", default=0.1)


bpy.utils.register_class(AnimationSettings)
bpy.types.Scene.animation_settings = PointerProperty(type=AnimationSettings)

def get_glb_files(self, context):
    glb_files = []
        
    blend_path = bpy.data.filepath
    glb_path = os.path.dirname(blend_path)+"\glb\\"

    if not os.path.exists(glb_path):
        return glb_files

    listOfFiles = os.listdir(glb_path)
    pattern = "*.glb"
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            filename, file_extension = os.path.splitext(entry)
            glb_files.append((filename,filename,"Override file :" + entry))

    return glb_files

def update_filename(self, value):
    scene = self
    scene.export_settings.glb_filename = scene.glb_file_dropdown


bpy.types.Scene.glb_file_dropdown = bpy.props.EnumProperty(
    items=get_glb_files,
    name="Exported GLB's",
    update=update_filename)


def run_help_operator(self,context):
   bpy.ops.scene.help_govie(image_name ="help_overlay_govie_tools.png" )

bpy.types.Scene.help_govie_tools = BoolProperty(default=False,update=run_help_operator)