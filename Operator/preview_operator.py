import os
from pathlib import Path

import bpy

from ..Functions import functions


class GOVIE_Preview_Operator(bpy.types.Operator):
    bl_idname = "scene.open_web_preview"
    bl_label = "Open in Browser"
    bl_description = "Press export to display a preview of the exported file"

    port = 8000
    url = (
        "https://3dit-tools.s3.eu-central-1.amazonaws.com/StaticGLBViewerV2/index.html"
    )

    @classmethod
    def poll(cls, context):
        # get folder of blend file
        blend_path = Path(bpy.data.filepath).parent

        # get export settings
        glb_filename = context.scene.export_settings.glb_filename

        if blend_path.joinpath(glb_filename).parent.exists():
            return True
        else:
            return False

    def execute(self, context):
        # get folder of blend file
        blend_path = Path(bpy.data.filepath).parent

        # get export settings
        glb_filename = context.scene.export_settings.glb_filename
        if not glb_filename.endswith(".glb"):
            glb_filename = "{}.glb".format(glb_filename)

        functions.start_server(blend_path.joinpath(glb_filename).absolute(), self.port)
        # run browser
        bpy.ops.wm.url_open(url=self.url)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(GOVIE_Preview_Operator)


def unregister():
    bpy.utils.unregister_class(GOVIE_Preview_Operator)
