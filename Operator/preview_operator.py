import bpy
import os
from .. Functions import functions


class GOVIE_Preview_Operator(bpy.types.Operator):
    bl_idname = "scene.open_web_preview"
    bl_label = "Open in Browser"
    bl_description = "Press export to display preview of exported file (only works if online access is allowed)"

    port = 8000
    url = "https://3dit-tools.s3.eu-central-1.amazonaws.com/StaticGLBViewerV2/index.html"

    @classmethod
    def poll(cls, context):
        if hasattr(bpy.app, 'online_access'):
            return bpy.app.online_access

        file_path = bpy.data.filepath
        project_dir = os.path.dirname(file_path)
        filename = context.scene.export_settings.glb_filename
        glb_path = os.path.join(project_dir, 'glb', '')
        glb_file = glb_path + filename + ".glb"

        if os.path.exists(glb_file):
            return True
        return False

    def execute(self, context):
        file_path = bpy.data.filepath
        project_dir = os.path.dirname(file_path)
        filename = context.scene.export_settings.glb_filename
        glb_dir = os.path.join(project_dir, 'glb', '')
        glb_file_path = glb_dir + filename + ".glb"

        functions.start_server(glb_file_path, self.port)
        # run browser
        bpy.ops.wm.url_open(url=self.url)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(GOVIE_Preview_Operator)


def unregister():
    bpy.utils.unregister_class(GOVIE_Preview_Operator)
