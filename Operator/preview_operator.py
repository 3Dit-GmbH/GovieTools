import os

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
        project_dir = os.path.dirname(bpy.data.filepath)
        filename = context.scene.export_settings.glb_filename
        glb_path = os.path.join(project_dir, "glb", "")
        glb_file = glb_path + filename + ".glb"

        if os.path.exists(glb_file):
            return True
        return False

    def execute(self, context):
        project_dir = os.path.dirname(bpy.data.filepath)
        filename = context.scene.export_settings.glb_filename
        glb_dir = os.path.join(project_dir, "glb", "")
        glb_file_path = glb_dir + filename + ".glb"

        functions.start_server(glb_file_path, self.port)
        # run browser
        bpy.ops.wm.url_open(url=self.url)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(GOVIE_Preview_Operator)


def unregister():
    bpy.utils.unregister_class(GOVIE_Preview_Operator)
