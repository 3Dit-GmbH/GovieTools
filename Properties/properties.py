import fnmatch
import os

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from ..Functions import gui_functions


class Export_Settings(bpy.types.PropertyGroup):
    glb_filename: StringProperty(name="Filename", default="filename")
    export_selected: BoolProperty(name="Export Only Selected", default=False)
    join_objects: BoolProperty(name="Join Static Objects", default=False)
    export_lights: BoolProperty(name="Export Lights", default=False)
    export_animations: BoolProperty(name="Export Animation", default=True)
    apply_modifiers: BoolProperty(name="Apply Modifiers", default=True)
    export_colors: BoolProperty(name="Export Vertex Colors", default=True)
    use_sampling: BoolProperty(name="Resample Animation", default=False)
    optimize_animation: BoolProperty(name="Optimize Animation", default=False)
    group_by_nla: BoolProperty(name="Group by NLA", default=True)
    export_all_influences: BoolProperty(
        name="Include all Bone Influences", default=False
    )
    export_image_format: EnumProperty(
        name="Image Compression",
        items=(
            (
                "AUTO",
                "Automatic",
                "Determine the image format from the blender image name.",
            ),
            ("JPEG", "JPEG", "Convert Images to JPEG, images with alpha still use PNG"),
        ),
    )
    use_draco: BoolProperty(name="Draco Compression", default=True)
    draco_compression_level: IntProperty(name="Compression Level", default=6)
    postion_quantization: IntProperty(
        name="Position Quantisation", default=14, min=0, max=30
    )
    normal_quantization: IntProperty(
        name="Normal Quantisation", default=10, min=0, max=30
    )
    texcoord_quantization: IntProperty(
        name="Tex-Coord. Quantisation", default=12, min=0, max=30
    )


bpy.utils.register_class(Export_Settings)

bpy.types.Scene.export_settings = PointerProperty(type=Export_Settings)
bpy.types.Scene.object_index = IntProperty(
    name="Index for Visibility UI List", update=gui_functions.update_sel_item
)
bpy.types.Object.visibility_bool = BoolProperty(
    name="Mapping for Property Value", update=gui_functions.remap_vis_prop
)
bpy.types.Scene.open_verification_menu = BoolProperty(default=False)
bpy.types.Scene.open_animation_manage = BoolProperty(default=False)
bpy.types.Scene.open_animation_particle = BoolProperty(default=False)
bpy.types.Scene.open_animation_simplifly = BoolProperty(default=False)
bpy.types.Scene.open_uv_animation_menu = BoolProperty(default=False)


class ParticleSettings(bpy.types.PropertyGroup):
    key_loc: BoolProperty(name="Key Location", default=1)
    key_rot: BoolProperty(name="Key Rotation", default=1)
    key_scale: BoolProperty(name="Key Scale", default=1)
    key_vis: BoolProperty(name="Key Visibility", default=0)
    frame_offset: IntProperty(name="Frame Offset", default=1)
    collection_name: StringProperty(name="Collection Name", default="Collection Name")


bpy.utils.register_class(ParticleSettings)
bpy.types.Scene.particle_settings = PointerProperty(type=ParticleSettings)


class AnimationSettings(bpy.types.PropertyGroup):
    simplify_keyframes_modes = [
        (
            "RATIO",
            "Ratio",
            "Use a percentage to specify how many keyframes you want to remove.",
        ),
        (
            "ERROR",
            "Error ",
            "Use an error margin to specify how much the curve is allowed to deviate from the original path.",
        ),
    ]

    simplify_keyframes_enum: EnumProperty(
        name="Simplify Mode",
        description="Choose mode to decimate keyframes",
        items=simplify_keyframes_modes,
    )
    join_anim_name: StringProperty(name="Animation Name", default="Animation Name")
    decimate_ratio: FloatProperty(name="Decimate Ratio", default=0.1)


bpy.utils.register_class(AnimationSettings)
bpy.types.Scene.animation_settings = PointerProperty(type=AnimationSettings)


def get_glb_files(self, context):
    glb_files = []

    file_path = bpy.data.filepath
    project_dir = os.path.dirname(file_path)
    glb_path = os.path.join(project_dir, "glb", "")

    if not os.path.exists(glb_path):
        return glb_files

    listOfFiles = os.listdir(glb_path)
    pattern = "*.glb"
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            filename, file_extension = os.path.splitext(entry)
            glb_files.append((filename, filename, "Override file :" + entry))

    return glb_files


def update_filename(self, value):
    scene = self
    scene.export_settings.glb_filename = scene.glb_file_dropdown


bpy.types.Scene.glb_file_dropdown = bpy.props.EnumProperty(
    items=get_glb_files, name="Exported GLB's", update=update_filename
)


def register():
    bpy.utils.register_class(Export_Settings)
    bpy.utils.register_class(ParticleSettings)
    bpy.utils.register_class(AnimationSettings)


def unregister():
    bpy.utils.unregister_class(Export_Settings)
    bpy.utils.unregister_class(ParticleSettings)
    bpy.utils.unregister_class(AnimationSettings)
