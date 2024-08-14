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

import os

from .Functions import functions
from .Operator import (
    bake_particles,
    join_animation,
    operator,
    preview_operator,
    simplify_keyframes,
)
from .Panel import panel

bl_info = {
    "name": "Govie Tools",
    "author": "Lorenz Wieseke, 3D Interaction Technologies GmbH (contact@govie.de)",
    "description": "Transform your model into a web-optimized GLB file for use in the Govie Editor.",
    "blender": (4, 2, 0),
    "version": (1, 0, 12),
    "location": "View 3D > Property Panel (N-Key in 3D View)",
    "warning": "",
    "category": "Scene",
    "wiki_url": "https://govie-editor.de/en/help/govie-tools?utm_source=blender-add-on&utm_medium=button",
    "tracker_url": "https://github.com/3Dit-GmbH/GovieTools/issues",
}


def register():
    bake_particles.register()
    join_animation.register()
    preview_operator.register()
    simplify_keyframes.register()
    operator.register()
    panel.register()
    functions.get_addon_dir(os.path.realpath(__file__))


def unregister():
    bake_particles.unregister()
    join_animation.unregister()
    preview_operator.unregister()
    simplify_keyframes.unregister()
    operator.unregister()
    panel.unregister()
    functions.stop_server()
