import os
import signal
import subprocess
import sys
from pathlib import Path

import bpy  # type: ignore

addon_dir = ""
server_pid = None


def get_addon_dir(file):
    global addon_dir
    addon_dir = os.path.dirname(file)


def select_object(self, obj):
    try:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
    except RuntimeError:
        self.report({"INFO"}, "Object {} not in View Layer".format(obj.name))


def select_object_by_mat(self, mat):
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        object_materials = [slot.material for slot in obj.material_slots]
        if mat in object_materials:
            select_object(self, obj)


def start_server(glb_file_path, port):
    global server_pid

    if server_pid is not None:
        stop_server()

    server_file_path = os.path.join(addon_dir, "Server", "server.py")

    sub_args = [Path(sys.executable)]

    if hasattr(bpy.app, "python_args"):
        for a in bpy.app.python_args:
            sub_args.append(a)
    else:
        sub_args.append("-I")

    sub_args.append(server_file_path)
    sub_args.append(glb_file_path)
    sub_args.append(str(port))

    server_process = subprocess.Popen(sub_args)

    server_pid = server_process.pid


def stop_server():
    global server_pid

    if server_pid is None:
        print("No process id for the server. Has it been started?")
        return

    try:
        os.kill(server_pid, signal.SIGTERM)
        print("Closed process " + str(server_pid))
    except OSError:
        print("Could not kill server process")


def convert_umlaut(str):
    spcial_char_map = {ord("ä"): "ae", ord("ü"): "ue", ord("ö"): "oe", ord("ß"): "ss"}
    return str.translate(spcial_char_map)


def rename_annotation():
    for o in bpy.context.scene.objects:
        if o.name.startswith("Under"):
            o.data.name = o.name


def get_or_create_joined_collection(scene):
    joined_collection = scene.collection.children.get("JoinedObjects")
    if not joined_collection:
        joined_collection = bpy.data.collections.new(name="JoinedObjects")
        scene.collection.children.link(joined_collection)
    return joined_collection


def has_material_variants(mesh):
    return bool(mesh.gltf2_variant_pointer)


def join_objects_without_visibility_property(export_selected):
    current_scene = bpy.context.scene

    # Only visible objects get exported
    invisible_objects = []

    for o in current_scene.objects:
        if not o.visible_get():
            invisible_objects.append(o)

    for o in invisible_objects:
        bpy.data.objects.remove(o)

    # If set, export only objects that are selected
    if export_selected:
        not_selected_objects = []
        for o in current_scene.objects:
            if not o.select_get():
                not_selected_objects.append(o)

        for o in not_selected_objects:
            bpy.data.objects.remove(o)

    # Select only objects that can be joined
    bpy.ops.object.select_all(action="SELECT")

    for o in current_scene.objects:
        if "visibility" in o.keys():
            o.select_set(False)
            # also deselect all children
            for child in o.children_recursive:
                child.select_set(False)
            continue

        if "clickablePart" in o.keys():
            o.select_set(False)
            # also deselect all children
            for child in o.children_recursive:
                child.select_set(False)
            continue

        if o.animation_data is not None:
            o.select_set(False)
            continue

        if o.type != "MESH":
            o.select_set(False)
            continue

        if has_material_variants(o.data):
            o.select_set(False)
            continue

    if len(current_scene.objects) == 0:
        print("No objects available to join")
        return False

    # make the first selected object active
    for o in current_scene.objects:
        if o.select_get():
            current_scene.view_layers[0].objects.active = o
            break

    bpy.ops.object.join()
    return True


def optimize_scene(gltf_export_param):
    bpy.ops.wm.save_mainfile()
    # Work on a copy of the scene
    bpy.ops.scene.new(type="FULL_COPY")
    if "use_selection" in gltf_export_param:
        join_objects_without_visibility_property(gltf_export_param["use_selection"])
    else:
        join_objects_without_visibility_property(False)

    bpy.ops.export_scene.gltf(**gltf_export_param)
    bpy.ops.scene.delete()
    bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
