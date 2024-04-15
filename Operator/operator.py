import bpy
import os
from .. Functions import functions
import subprocess
import addon_utils


C = bpy.context
D = bpy.data
O = bpy.ops


# bpy.types.Scene.export_settings.glb_filename = bpy.props.StringProperty(
#     name="Filename", default="filename")


class GOVIE_open_export_folder_Operator(bpy.types.Operator):
    bl_idname = "scene.open_export_folder"
    bl_label = "Open Folder"
    bl_description = "Open current GLB folder"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        file_path = bpy.data.filepath
        project_dir = os.path.dirname(file_path)
        glb_path = os.path.join(project_dir, 'glb', '')

        if file_path != "":
            subprocess.call("explorer " + glb_path, shell=True)
        else:
            self.report({'INFO'}, 'You need to save Blend file first !')

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
                obj.visibiliy_bool = 1
            if self.property_type == "clickable":
                obj["bookmark"] = "bookmark"


        return {'FINISHED'}
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
                if "bookmark" in obj.keys():
                    del obj["bookmark"]        
            
            
        return {'FINISHED'}


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
        context.scene.export_settings.glb_filename = functions.convert_umlaut(
            filename)

        # check annotation names
        functions.rename_annotation()

        # GLBTextureTools installed ?
        if addon_utils.check("GLBTextureTools")[1]:
            save_preview_lightmap_setting = bpy.context.scene.texture_settings.preview_lightmap
            bpy.ops.object.preview_bake_texture(connect=False)
            bpy.ops.object.preview_lightmap(connect=False)
            bpy.ops.object.lightmap_to_emission(connect=True)

        # blender file saved
        file_is_saved = bpy.data.is_saved

        # create folder
        file_path = bpy.data.filepath
        project_dir = os.path.dirname(file_path)
        glb_path = os.path.join(project_dir, 'glb', '')

        if not os.path.exists(glb_path):
            os.makedirs(glb_path)

        # get export settigns
        filename = context.scene.export_settings.glb_filename
        filepath = glb_path+filename
        use_draco = context.scene.export_settings.use_draco
        export_selected = context.scene.export_settings.export_selected
        export_lights = context.scene.export_settings.export_lights
        export_animations = context.scene.export_settings.export_animations
        apply_modifiers = context.scene.export_settings.apply_modifiers
        use_sampling = context.scene.export_settings.use_sampling
        optimize_animation = context.scene.export_settings.optimize_animation
        group_by_nla = context.scene.export_settings.group_by_nla
        export_image_format = context.scene.export_settings.export_image_format
        draco_compression_level = context.scene.export_settings.draco_compression_level
        postion_quantization = context.scene.export_settings.postion_quantization
        normal_quantization = context.scene.export_settings.normal_quantization
        texcoord_quantization = context.scene.export_settings.texcoord_quantization
        export_all_influences = context.scene.export_settings.export_all_influences
        export_colors = context.scene.export_settings.export_colors
        join_objects = context.scene.export_settings.join_objects
        


        #blender version
        version = bpy.app.version_string

        gltf_export_param = {   "filepath":filepath,
                                "export_draco_mesh_compression_enable":use_draco,
                                "export_draco_mesh_compression_level":draco_compression_level,
                                "export_draco_position_quantization":postion_quantization,
                                "export_draco_normal_quantization":normal_quantization,
                                "export_draco_texcoord_quantization":texcoord_quantization,
                                "export_extras":True,
                                "export_lights":export_lights,
                                "export_animations":export_animations,
                                "export_morph":True,
                                "export_apply":apply_modifiers,
                                "export_image_format":export_image_format,
                                "export_nla_strips":group_by_nla,
                                "export_force_sampling":use_sampling,
                                "export_all_influences":export_all_influences,
                                "export_colors":export_colors,
                                "use_visible":True    }

        if version < '3.2.0': 
            gltf_export_param['export_selected'] = export_selected

        if version >= '3.2.0' and version < '3.3.1': 
            gltf_export_param['use_selection'] = export_selected 
            gltf_export_param['optimize_animation_size'] = optimize_animation 

        if version >= '3.3.1':
            gltf_export_param['use_selection'] = export_selected 
            gltf_export_param['export_optimize_animation_size'] = optimize_animation 
            
        if version >= '3.6':
            gltf_export_param['use_selection'] = export_selected 
            gltf_export_param['export_optimize_animation_size'] = optimize_animation
            gltf_export_param['use_active_scene'] = True
            if group_by_nla is False:
                gltf_export_param['export_animation_mode'] = "ACTIVE_ACTIONS"


        if file_is_saved:
            # export glb
            if join_objects:
                functions.optimize_scene(gltf_export_param)
            else:
                bpy.ops.export_scene.gltf(**gltf_export_param)
            # change glb dropdown entry
            context.scene.glb_file_dropdown = context.scene.export_settings.glb_filename

            if addon_utils.check("GLBTextureTools")[1]:
                bpy.ops.object.lightmap_to_emission(connect=False)
                bpy.ops.object.preview_lightmap(
                    connect=save_preview_lightmap_setting)

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
                functions.select_object(self, obj)
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
        exclude_temp_list = []
        collections = bpy.context.view_layer.layer_collection.children

        # switch on all layers but remember vis settings
        for collection in collections:
            exclude_temp_list.append(collection.exclude)
            collection.exclude = False

        for obj in bpy.data.objects:
            if obj.type == 'MESH':

                functions.select_object(self, obj)
                O.object.editmode_toggle()
                O.mesh.delete_loose()
                O.mesh.dissolve_degenerate()
                O.object.editmode_toggle()

        # set back layer settings
        for collection, exclude_temp_value in zip(collections, exclude_temp_list):
            collection.exclude = exclude_temp_value

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
        for mat in D.materials:
            if mat.node_tree is None:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is None:
                    mat_name_list.append(mat.name)
                    self.report(
                        {'INFO'}, "Found empty image node in material {}".format(mat.name))
                    functions.select_object_by_mat(self, mat)

        if len(mat_name_list) == 0:
            self.report({'INFO'}, 'No Empty Image Nodes')

        return {'FINISHED'}


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
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
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
                if node.type == 'MAPPING':
                    mapping_node = node
                    break

            if mapping_node:
                # remove driver fist if there is one
                mapping_node.inputs["Location"].driver_remove("default_value", 0)
                driverX = mapping_node.inputs["Location"].driver_add("default_value", 0).driver
                driverX.type = 'SCRIPTED'
                driverX.expression = empty.name
                
                 # Add the Empty object as a variable target
                var = driverX.variables.new()
                var.name = empty.name
                var.type = 'TRANSFORMS'
                var.targets[0].id = bpy.data.objects[empty.name]
                var.targets[0].transform_type = 'LOC_X' 

                mapping_node.inputs["Location"].driver_remove("default_value", 1)
                driverY = mapping_node.inputs["Location"].driver_add("default_value", 1).driver
                driverY.type = 'SCRIPTED'
                driverY.expression = "-" + empty.name              
                
                var = driverY.variables.new()
                var.name = empty.name
                var.type = 'TRANSFORMS'
                var.targets[0].id = bpy.data.objects[empty.name]
                var.targets[0].transform_type = 'LOC_Z' 
                
            else:
                print("Mapping node not found in the material's node tree.")
        else:
            print("Active object or active material not found.")

        active_object.select_set(True)
        context.view_layer.objects.active = active_object
       
        
        return {'FINISHED'}
    
    