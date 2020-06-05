import bpy
import os
from . functions import *


C = bpy.context
D = bpy.data
O = bpy.ops



# bpy.types.Scene.export_settings.glb_filename = bpy.props.StringProperty(
#     name="Filename", default="filename")


class GOVIE_Open_Folder_Operator(bpy.types.Operator):
    bl_idname = "scene.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open current GLB folder"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath) + "\\glb\\"
        
        if filepath is not "":
            subprocess.call("explorer " + directory, shell=True)
        else:
            self.report({'INFO'}, 'You need to save Blend file first !')

        return {"FINISHED"}



class GOVIE_Preview_Operator(bpy.types.Operator):
    bl_idname = "scene.open_web_preview"
    bl_label = "Open in Browser"
    bl_description = "Press export to display preview of exported file"

    url = "https://3dit-tools.s3.eu-central-1.amazonaws.com/StaticGLBViewer/index.html#model=http://127.0.0.1:8000/export.glb"

    @classmethod
    def poll(cls, context):
        filename = context.scene.export_settings.glb_filename
        
        path = bpy.path.abspath("//glb\\"+filename+".glb")
        if os.path.exists(path):
            return True
        return False


    def execute(self, context):
        filename = context.scene.export_settings.glb_filename
        file_path = bpy.path.abspath("//glb\\"+filename+".glb")

        script_file = os.path.realpath(__file__)
        script_dir = os.path.dirname(script_file)

        server_path = bpy.path.abspath(script_dir+"\Server\server.py")
        start_server(server_path,file_path)
        # run browser
        bpy.ops.wm.url_open(url = self.url)
        return {"FINISHED"}

class GOVIE_Open_Link_Operator(bpy.types.Operator):
    bl_idname = "scene.open_link"
    bl_label = "Open Website"
    bl_description = "Go to GOVIE Website"

    url : bpy.props.StringProperty(name="url")

    @classmethod
    def poll(cls, context):
        return True
    def execute(self, context):
        bpy.ops.wm.url_open(url=self.url)
        return {"FINISHED"}


class GOVIE_Add_Property_Operator(bpy.types.Operator):
    """Add the custom property on the current selected object"""
    bl_idname = "object.add_vis_property"
    bl_label = "Add visibility Property"
    

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        else:
            return True

    def execute(self, context):
        obj = context.object
        obj["visibility"] = 1
        obj.visibiliy_bool = 1

        return {'FINISHED'}


class GOVIE_Remove_Property_Operator(bpy.types.Operator):
    """Remove the custom property on the current selected object"""
    bl_idname = "object.remove_vis_property"
    bl_label = "Remove visibility Property"

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        if context.object.get("visibility") is None:
            return False
        else:
            return True

    def execute(self, context):
        obj = context.object
        try:
            del obj["visibility"]
        except:
            self.report({'INFO'}, 'Select object with visability Property')
            return {'FINISHED'}
        return {'FINISHED'}


class GOVIE_Quick_Export_GLB_Operator(bpy.types.Operator):
    bl_idname = "scene.gltf_quick_export"
    bl_label = "EXPORT_GLTF"
    bl_description = "Save Blender file to use this button ! The GLB file will be saved to 'pathOfBlendFile/glb/filename.glb'"

    @classmethod
    def poll(cls, context):
        if bpy.data.is_saved:
            return True
        else:
            return False

    def execute(self, context):
        # blender file saved 
        file_is_saved = bpy.data.is_saved
        # create folder
        path = bpy.path.abspath("//glb//")

        if not os.path.exists(path):
            os.makedirs(path)
            
        # get export settigns
        filename = context.scene.export_settings.glb_filename
        use_draco = context.scene.export_settings.use_draco
        export_selected = context.scene.export_settings.export_selected
        export_lights = context.scene.export_settings.export_lights
        export_animations = context.scene.export_settings.export_animations
        apply_modifiers = context.scene.export_settings.apply_modifiers
        use_sampling = context.scene.export_settings.use_sampling
        group_by_nla = context.scene.export_settings.group_by_nla
        use_draco = context.scene.export_settings.use_draco
        export_image_format = context.scene.export_settings.export_image_format
        draco_compression_level = context.scene.export_settings.draco_compression_level
        postion_quantization = context.scene.export_settings.postion_quantization
        normal_quantization = context.scene.export_settings.normal_quantization
        texcoord_quantization = context.scene.export_settings.texcoord_quantization

        if file_is_saved:
            # export glb
            texcoord_quantization = context.scene.export_settings.texcoord_quantization

            bpy.ops.export_scene.gltf(filepath=path+filename, 
                                    export_draco_mesh_compression_enable=use_draco,
                                    export_draco_mesh_compression_level=draco_compression_level,
                                    export_draco_position_quantization=postion_quantization,
                                    export_draco_normal_quantization=normal_quantization,
                                    export_draco_texcoord_quantization=texcoord_quantization,
                                    export_selected=export_selected,
                                    export_extras=True,
                                    export_lights=export_lights,
                                    export_animations=export_animations,
                                    export_apply=apply_modifiers,
                                    export_image_format=export_image_format,
                                    export_nla_strips=group_by_nla,
                                    export_force_sampling=use_sampling)
        else:
            self.report({'INFO'}, 'You need to save Blend file first !')

        return {'FINISHED'}


class GOVIE_Convert_Text_Operator(bpy.types.Operator):
    bl_idname = "object.convert_text"
    bl_label = "EXPORT_GLTF"
    bl_description = "Convert text curves to mesh instances and put them in new collection named annotation"

    @classmethod
    def poll(cls, context):
        for obj in bpy.data.objects:
            if obj.type == 'FONT' and obj.visible_get():
                return context

    def execute(self, context):
        D = bpy.data

        # add collection
        colName = "Annotation"

        if D.collections.get(colName) is None:
            D.collections.new(colName)

        newCol = D.collections.get(colName)

        # link collection to scene
        if newCol.name not in context.scene.collection.children:
            context.scene.collection.children.link(newCol)

        for obj in bpy.data.objects:
            if obj.type == 'FONT':

                # create new object for mesh
                select_object(obj)
                O.object.convert(target='MESH', keep_original=True)

                textMesh = context.object
                newName = obj.name + " Mesh"

                # remove textMesh from current collection
                for col in D.collections:
                    if textMesh in set(col.objects):
                        col.objects.unlink(textMesh)

                # get index of textMesh in newCol
                indexTextMesh = newCol.objects.find(newName)

                # if not in collection, put it in
                if indexTextMesh == -1:
                    textMesh.name = newName

                    # add to new colleciton
                    newCol.objects.link(textMesh)

                # if already in collection just override it's data
                else:
                    newCol.objects[indexTextMesh].data = textMesh.data

                # bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


class GOVIE_CleanupMesh_Operator(bpy.types.Operator):
    bl_idname = "object.cleanup_mesh"
    bl_label = "Delete Loose and Degenerate Dissolve"
    bl_description = "mesh cleanup -> Delete Loose and Degenerate Dissolve"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        os.system('cls')
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                select_object(obj)
                O.object.editmode_toggle()
                O.mesh.delete_loose()
                O.mesh.dissolve_degenerate()
                O.object.editmode_toggle()

        self.report({'INFO'}, 'Meshes Cleaned !')
        return {'FINISHED'}


class GOVIE_CheckTexNodes_Operator(bpy.types.Operator):
    """Check if there are any empty Texture Nodes in any Material and print that material"""
    bl_idname = "object.check_tex_nodes"
    bl_label = "Check Empty Tex Nodes"

    bpy.types.Scene.mat_name_list = []

    def execute(self, context):
        D = bpy.data
        mat_name_list = context.scene.mat_name_list
        mat_name_list.clear()

        # get materials with texture nodes that have no image assigned
        materialsWithEmptyTexNode = [
            mat for mat in D.materials for node in mat.node_tree.nodes if node.type == "TEX_IMAGE" and node.image is None]

       # add to list
        for mat in materialsWithEmptyTexNode:
            mat_name_list.append(mat.name)

        for obj in D.objects:
            if obj.type == "MESH":
                object_materials = [slot.material for slot in obj.material_slots]
                material_detected = set(object_materials).intersection(set(materialsWithEmptyTexNode))
                if len(material_detected) > 0:
                    select_object(obj)

        if len(mat_name_list) == 0:
            self.report({'INFO'}, 'No Empty Image Nodes')

        return {'FINISHED'}
