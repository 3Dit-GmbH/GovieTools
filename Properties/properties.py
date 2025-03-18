import fnmatch
import os
from pathlib import Path
import glob

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
    glb_filename: StringProperty(name="Filename", default="./glb/filename.glb")
    join_objects: BoolProperty(name="Join Static Objects", default=False)
    export_preset: StringProperty(name="Export Preset", default="")


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


def get_export_presets(self, context):
    presets = []
    presets.append(("none", "none", "Use selected export preset for export"))

    # find all preset files for gltf exporter
    preset_directory = Path(bpy.utils.preset_paths("operator/export_scene.gltf/")[0])
    preset_files = glob.glob("*.py", root_dir=preset_directory.absolute())
    for p in preset_files:
        preset_name = p.split(".")[0]
        presets.append(
            (preset_name, preset_name, "Use selected export preset for export")
        )

    return presets


def update_presets(self, context):
    scene = self
    scene.export_settings.export_preset = scene.glb_preset_dropdown


bpy.types.Scene.glb_preset_dropdown = bpy.props.EnumProperty(
    items=get_export_presets, name="Export Preset", update=update_presets
)


def register():
    bpy.utils.register_class(Export_Settings)
    bpy.utils.register_class(ParticleSettings)
    bpy.utils.register_class(AnimationSettings)


def unregister():
    bpy.utils.unregister_class(Export_Settings)
    bpy.utils.unregister_class(ParticleSettings)
    bpy.utils.unregister_class(AnimationSettings)
