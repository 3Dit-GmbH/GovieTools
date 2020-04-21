import bpy
import subprocess
import atexit

server_process = None

O = bpy.ops


def select_object(obj):
    C = bpy.context

    O.object.select_all(action='DESELECT')
    C.view_layer.objects.active = obj
    obj.select_set(True)

def start_server(server_path,file_path):
    global server_process 
    if server_process is not None:
        stop_server()
    server_process = subprocess.Popen([bpy.app.binary_path_python, server_path, file_path])

def stop_server():
    global server_process 
    if server_process is not None:
        print("Closed process " + str(server_process.pid))
        server_process.kill()

atexit.register(stop_server)