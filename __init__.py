# Copyright (c) 2024 Lorenz Wieseke via 3D Interaction Technologies GmbH
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Govie Tools",
    "author": "Lorenz Wieseke, 3D Interaction Technologies GmbH (contact@govie.de)",
    "description": "Transform your model into a web-optimized GLB file for use in the Govie Editor.",
    "blender": (4,0,0),
    "version": (1,0,0),
    "location": "View 3D > Property Panel (N-Key in 3D View)",    
    "warning": "This add-on officially supports Blender version 4",
    "category": "Scene",
    "wiki_url": "https://govie-editor.de/en/help/govie-tools?utm_source=blender-add-on&utm_medium=button",
    "tracker_url": "https://github.com/3Dit-GmbH/GovieTools/issues",
}

from . import auto_load
from .Functions import functions
import os

auto_load.init()

def register():
    auto_load.register()
    functions.get_addon_dir(os.path.realpath(__file__))

def unregister():
    auto_load.unregister()
    functions.stop_server()
