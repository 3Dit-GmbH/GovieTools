import bpy  # type: ignore
from pathlib import Path

from ..Functions import functions


class GOVIE_open_export_folder_Operator(bpy.types.Operator):
    bl_idname = "scene.open_export_folder"
    bl_label = "Open Folder"
    bl_description = "Open current GLB folder. You may need to export first for the folder to be created."

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

        bpy.ops.wm.url_open(
            url=str(blend_path.joinpath(glb_filename).parent.absolute())
        )

        return {"FINISHED"}


class GOVIE_Open_Link_Operator(bpy.types.Operator):
    bl_idname = "scene.open_link"
    bl_label = "Open Website"
    bl_description = "Go to GOVIE Website"

    url: bpy.props.StringProperty(name="url")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.wm.url_open(url=self.url)
        return {"FINISHED"}


class GOVIE_Add_Property_Operator(bpy.types.Operator):
    """Add the custom property on the current selected object"""

    bl_idname = "object.add_property"
    bl_label = "Add custom Property"

    property_type: bpy.props.StringProperty(name="custom_property_name")

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        else:
            return True

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if self.property_type == "visibility":
                obj["visibility"] = 1
                # obj.visibility_bool = 1
            if self.property_type == "clickable":
                obj["clickablePart"] = "clickablePart"

        return {"FINISHED"}


class GOVIE_Remove_Property_Operator(bpy.types.Operator):
    """Remove the custom property on the current selected object"""

    bl_idname = "object.remove_property"
    bl_label = "Remove visibility Property"

    property_type: bpy.props.StringProperty(name="custom_property_name")

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        else:
            return True

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if self.property_type == "visibility":
                if "visibility" in obj.keys():
                    del obj["visibility"]
            if self.property_type == "clickable":
                if "clickablePart" in obj.keys():
                    del obj["clickablePart"]

        return {"FINISHED"}


class GOVIE_Quick_Export_GLB_Operator(bpy.types.Operator):
    bl_idname = "scene.gltf_quick_export"
    bl_label = "EXPORT_GLTF"
    bl_description = "Save Blend file first ! The GLB file will be saved to 'pathOfBlendFile/glb/filename.glb'"

    @classmethod
    def poll(cls, context):
        if bpy.data.is_saved:
            return True
        else:
            return False

    def execute(self, context):
        # check spelling
        filename = context.scene.export_settings.glb_filename
        context.scene.export_settings.glb_filename = functions.convert_umlaut(filename)

        # check annotation names
        functions.rename_annotation()

        # blender file saved
        file_is_saved = bpy.data.is_saved

        if not file_is_saved:
            self.report({"INFO"}, "You need to save the Blend file first!")
            return {"FINISHED"}

        # get folder of blend file
        blend_path = Path(bpy.data.filepath).parent

        # get export settings
        glb_filename = context.scene.export_settings.glb_filename
        glb_filepath = blend_path.joinpath(glb_filename)

        if not glb_filepath.parent.exists():
            glb_filepath.parent.mkdir(parents=True)

        preset_path = "operator/export_scene.gltf/"
        export_preset_name = context.scene.export_settings.export_preset
        preset_filepath = bpy.utils.preset_find(export_preset_name, preset_path)

        gltf_export_param = {}

        # read preset parameters from file
        if preset_filepath:

            class Container(object):
                __slots__ = ("__dict__",)

            op = Container()
            preset_file = open(preset_filepath, "r")

            # storing the values from the preset on the class
            for line in preset_file.readlines()[3::]:
                exec(line, globals(), locals())

            # pass class dictionary to the operator
            gltf_export_param = op.__dict__

        join_objects = context.scene.export_settings.join_objects

        gltf_export_param["filepath"] = str(glb_filepath.absolute())

        # export glb
        if join_objects:
            functions.optimize_scene(gltf_export_param)
        else:
            bpy.ops.export_scene.gltf(**gltf_export_param)

        # change glb dropdown entry
        # context.scene.glb_file_dropdown = context.scene.export_settings.glb_filename

        return {"FINISHED"}


class GOVIE_CleanupMesh_Operator(bpy.types.Operator):
    bl_idname = "object.cleanup_mesh"
    bl_label = "Delete Loose and Degenerate Dissolve"
    bl_description = "Mesh Cleanup -> Delete Loose and Degenerate Dissolve"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        exclude_temp_list = []
        collections = bpy.context.view_layer.layer_collection.children

        # switch on all layers but remember vis settings
        for collection in collections:
            exclude_temp_list.append(collection.exclude)
            collection.exclude = False

        for obj in context.scene.objects:
            if obj.type == "MESH":
                functions.select_object(self, obj)
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.delete_loose()
                bpy.ops.mesh.dissolve_degenerate()
                bpy.ops.object.editmode_toggle()

        # set back layer settings
        for collection, exclude_temp_value in zip(collections, exclude_temp_list):
            collection.exclude = exclude_temp_value

        self.report({"INFO"}, "Meshes Cleaned !")
        return {"FINISHED"}


class GOVIE_CheckTexNodes_Operator(bpy.types.Operator):
    """Check if there are any empty Texture Nodes in any Material and print that material"""

    bl_idname = "object.check_tex_nodes"
    bl_label = "Check Empty Tex Nodes"

    bpy.types.Scene.mat_name_list = []

    def execute(self, context):
        mat_name_list = context.scene.mat_name_list
        mat_name_list.clear()

        # get materials with texture nodes that have no image assigned
        for mat in bpy.data.materials:
            if mat.node_tree is None:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is None:
                    mat_name_list.append(mat.name)
                    self.report(
                        {"INFO"},
                        "Found empty image node in material {}".format(mat.name),
                    )
                    functions.select_object_by_mat(self, mat)

        if len(mat_name_list) == 0:
            self.report({"INFO"}, "No Empty Image Nodes")

        return {"FINISHED"}


class GOVIE_Add_UV_Animation_Operator(bpy.types.Operator):
    """Create UV Animation for selected object"""

    bl_idname = "object.add_uv_anim"
    bl_label = "Add UV Animation"

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        else:
            return True

    def execute(self, context):
        active_object = context.active_object
        new_name = active_object.name + "_uv_anim_controller"

        if bpy.data.objects.get(new_name):
            empty = bpy.data.objects[new_name]
        else:
            bpy.ops.object.empty_add(
                type="PLAIN_AXES", align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
            )
            empty = context.active_object
            empty.name = new_name

        # add custom property
        empty["uvAnim"] = active_object.name

        # save emtpy name in scene for later use
        context.scene["uv_anim_obj"] = empty.name

        # add driver to material mapping node
        if active_object and active_object.active_material:
            material = active_object.active_material

            # Find the Mapping node in the material's node tree
            mapping_node = None
            for node in material.node_tree.nodes:
                print(node.type)
                if node.type == "MAPPING":
                    mapping_node = node
                    break

            if mapping_node:
                # remove driver fist if there is one
                mapping_node.inputs["Location"].driver_remove("default_value", 0)
                driverX = (
                    mapping_node.inputs["Location"]
                    .driver_add("default_value", 0)
                    .driver
                )
                driverX.type = "SCRIPTED"
                driverX.expression = empty.name

                # Add the Empty object as a variable target
                var = driverX.variables.new()
                var.name = empty.name
                var.type = "TRANSFORMS"
                var.targets[0].id = bpy.data.objects[empty.name]
                var.targets[0].transform_type = "LOC_X"

                mapping_node.inputs["Location"].driver_remove("default_value", 1)
                driverY = (
                    mapping_node.inputs["Location"]
                    .driver_add("default_value", 1)
                    .driver
                )
                driverY.type = "SCRIPTED"
                driverY.expression = "-" + empty.name

                var = driverY.variables.new()
                var.name = empty.name
                var.type = "TRANSFORMS"
                var.targets[0].id = bpy.data.objects[empty.name]
                var.targets[0].transform_type = "LOC_Z"

            else:
                print("Mapping node not found in the material's node tree.")
        else:
            print("Active object or active material not found.")

        active_object.select_set(True)
        context.view_layer.objects.active = active_object

        return {"FINISHED"}


def register():
    bpy.utils.register_class(GOVIE_open_export_folder_Operator)
    bpy.utils.register_class(GOVIE_Open_Link_Operator)
    bpy.utils.register_class(GOVIE_Add_Property_Operator)
    bpy.utils.register_class(GOVIE_Remove_Property_Operator)
    bpy.utils.register_class(GOVIE_Quick_Export_GLB_Operator)
    bpy.utils.register_class(GOVIE_CleanupMesh_Operator)
    bpy.utils.register_class(GOVIE_CheckTexNodes_Operator)
    bpy.utils.register_class(GOVIE_Add_UV_Animation_Operator)


def unregister():
    bpy.utils.unregister_class(GOVIE_open_export_folder_Operator)
    bpy.utils.unregister_class(GOVIE_Open_Link_Operator)
    bpy.utils.unregister_class(GOVIE_Add_Property_Operator)
    bpy.utils.unregister_class(GOVIE_Remove_Property_Operator)
    bpy.utils.unregister_class(GOVIE_Quick_Export_GLB_Operator)
    bpy.utils.unregister_class(GOVIE_CleanupMesh_Operator)
    bpy.utils.unregister_class(GOVIE_CheckTexNodes_Operator)
    bpy.utils.unregister_class(GOVIE_Add_UV_Animation_Operator)
