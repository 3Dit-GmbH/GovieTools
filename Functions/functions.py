import bpy
import subprocess
import atexit
import time

server_process = None

O = bpy.ops


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

def start_server(server_path,file_path,port):
    global server_process 
    if server_process is not None:
        stop_server()
    server_process = subprocess.Popen([bpy.app.binary_path_python, server_path, file_path,str(port)])

def stop_server():
    global server_process 
    if server_process is not None:
        print("Closed process " + str(server_process.pid))
        server_process.kill()

def convert_umlaut(str):
    spcial_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
    return str.translate(spcial_char_map)



atexit.register(stop_server)


