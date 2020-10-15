import bpy
import subprocess
import atexit
import time

server_process = None

O = bpy.ops


def select_object(obj):
    C = bpy.context

    O.object.select_all(action='DESELECT')
    C.view_layer.objects.active = obj
    obj.select_set(True)

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


