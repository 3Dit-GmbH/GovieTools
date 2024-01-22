import bpy
import subprocess
import json
import os, signal

import sys
from pathlib import Path


O = bpy.ops
addon_dir = ""

def get_addon_dir(file):
    global addon_dir
    addon_dir = os.path.dirname(file)

def select_object(self, obj):
    C = bpy.context
    O = bpy.ops
    try:
        O.object.select_all(action='DESELECT')
        C.view_layer.objects.active = obj
        obj.select_set(True)
    except:
        self.report({'INFO'}, "Object {} not in View Layer".format(obj.name))
    
def select_object_by_mat(self, mat):
    obj_found = None
    D = bpy.data
    for obj in D.objects:
        if obj.type != "MESH":
            continue
        object_materials = [slot.material for slot in obj.material_slots]
        if mat in object_materials:
            obj_found = obj
            select_object(self, obj)

def get_config_file():
    process_list_path = os.path.join(addon_dir,"Server","process_list.json")
    return process_list_path

def start_server(glb_file_path,port):
    
    process_list_path = get_config_file()
    
    # read pid from file
    with open(process_list_path) as f:
        pid_list = json.load(f)

    if len(pid_list)>0:
        cleaned_pid_list = stop_server()
        pid_list = cleaned_pid_list

    python_path = Path(sys.executable)
    server_file_path = os.path.join(addon_dir,"Server","server.py")

    server_process = subprocess.Popen([python_path, server_file_path, glb_file_path,str(port)])
    pid_list.append(server_process.pid)
    
    # write pid to file
    with open(process_list_path,'w') as f:
         json.dump(pid_list, f)

def stop_server():
    
    process_list_path = get_config_file()

    # read pid from file
    with open(process_list_path) as f:
        pid_list = json.load(f)
        
    for pid in pid_list:
        try:
            os.kill(pid, signal.SIGTERM)
            pid_list.remove(pid)
            print("Closed process " + str(pid))
        except OSError:
            continue
    

    # write pid to file
    with open(process_list_path,'w') as f:
         json.dump(pid_list, f)
         
    return pid_list


def convert_umlaut(str):
    spcial_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
    return str.translate(spcial_char_map)

def rename_annotation():
    for o in bpy.data.objects:
        if o.name.startswith('Under'):
            o.data.name = o.name

# merge objects

def get_or_create_joined_collection(scene):
    # Check if "JoinedObjects" collection already exists
    joined_collection = scene.collection.children.get("JoinedObjects")

    if not joined_collection:
        # If not, create a new collection
        joined_collection = bpy.data.collections.new(name="JoinedObjects")
        scene.collection.children.link(joined_collection)

    return joined_collection

def join_objects_without_animation_or_visibility(gltf_export_param):
    # Deselect all objects (implicitly sets the mode to OBJECT)
    bpy.ops.object.select_all(action='DESELECT')

    # Reference the current scene
    current_scene = bpy.context.scene

    # Get or create the "JoinedObjects" collection
    joined_collection = get_or_create_joined_collection(current_scene)

    # Iterate through all objects in the current scene
    for obj in current_scene.objects:
        # Check if the object is a mesh and has neither animation nor visibility property
        if obj.type == 'MESH' and obj.animation_data is None and obj.get('visibility') is None:
            joined_collection.objects.link(obj)

    # Select all objects in the joined collection
    for obj in joined_collection.objects:
        obj.select_set(True)

    # Set the active object (needed for bpy.ops.object.join())
    bpy.context.view_layer.objects.active = joined_collection.objects[0] if joined_collection.objects else None

    # Join the selected objects
    bpy.ops.object.join()

    # Rename the joined object
    joined_object = bpy.context.active_object
    joined_object.name = "JoinedObject"
    bpy.ops.export_scene.gltf(**gltf_export_param)

    

def optimize_scene(gltf_export_param):
    # Create a copy of the current scene
    bpy.ops.scene.new(type='FULL_COPY')
    copied_scene = bpy.context.scene

    # Run the join_objects_without_animation_or_visibility() function on the copied scene
    join_objects_without_animation_or_visibility(gltf_export_param)

    # Delete the copied scene
    bpy.data.scenes.remove(copied_scene)
