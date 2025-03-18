import bpy  # type: ignore

from ..Functions import gui_functions
from ..Properties import properties


class ANIM_UL_List(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
        flt_flag,
    ):
        if context.object is not None:
            selOff = "RADIOBUT_OFF"
            selOn = "RADIOBUT_ON"

            row = layout.row(align=True)
            split = row.split(factor=0.2)
            if item.name == context.object.name:
                split.label(text="", icon=selOn)
                split = split.split(factor=0.4)
                split.prop(item, "name", text="")
            else:
                split.label(text="", icon=selOff)
                split = split.split(factor=0.4)
                split.label(text=item.name)

            split = split.split(factor=1)

            has_action_name = getattr(
                getattr(getattr(item, "animation_data", None), "action", None),
                "name",
                None,
            )
            has_nla_name = getattr(
                getattr(getattr(item, "animation_data", None), "nla_tracks", None),
                "active",
                None,
            )

            if has_action_name:
                split.prop(item.animation_data.action, "name", text="")
            if has_nla_name:
                split.prop(item.animation_data.nla_tracks.active, "name", text="")

    def filter_items(self, context, data, propname):
        objects_in_scene = data.objects

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # flt_flags = [self.bitflag_filter_item if getattr(getattr(getattr(obj,"animation_data",None),"action",None),"name",None) and obj.visible_get(
        # ) else 0 for obj in objects_in_scene]

        for obj in objects_in_scene:
            has_action_name = getattr(
                getattr(getattr(obj, "animation_data", None), "action", None),
                "name",
                None,
            )
            has_nla_name = getattr(
                getattr(getattr(obj, "animation_data", None), "nla_tracks", None),
                "active",
                None,
            )
            if has_action_name or has_nla_name:
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)

        return flt_flags, flt_neworder


class VIS_UL_List(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
        flt_flag,
    ):
        selOff = "RADIOBUT_OFF"
        selOn = "RADIOBUT_ON"

        # 'DEFAULT' and 'COMPACT' layout types should usually use the same draw code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            split = row.split(factor=0.2)

            if context.object is not None:
                if item.name == context.object.name:
                    split.label(text="", icon=selOn)
                    split = split.split(factor=0.6)
                    split.prop(item, "name", text="")
                else:
                    split.label(text="", icon=selOff)
                    split = split.split(factor=0.6)
                    split.label(text=item.name)

                split = split.split(factor=1)
                split.prop(item, "visibility_bool", text="")

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        objectList = objects.items()

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # get only items that have visibility property
        flt_flags = [
            self.bitflag_filter_item
            if obj[1].get("visibility") is not None and obj[1].visible_get()
            else 0
            for obj in objectList
        ]

        return flt_flags, flt_neworder


class CLICK_UL_List(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
        flt_flag,
    ):
        selOff = "RADIOBUT_OFF"
        selOn = "RADIOBUT_ON"

        # 'DEFAULT' and 'COMPACT' layout types should usually use the same draw code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            split = row.split(factor=0.2)

            if context.object is not None:
                if item.name == context.object.name:
                    split.label(text="", icon=selOn)
                    split = split.split(factor=0.6)
                    split.prop(item, "name", text="")
                else:
                    split.label(text="", icon=selOff)
                    split = split.split(factor=0.6)
                    split.label(text=item.name)

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        objectList = objects.items()

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # get only items that have visibility property
        flt_flags = [
            self.bitflag_filter_item
            if obj[1].get("clickablePart") is not None and obj[1].visible_get()
            else 0
            for obj in objectList
        ]

        return flt_flags, flt_neworder


class GovieToolsPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Govie Tools"

    @classmethod
    def poll(cls, context):
        return context.object is not None


class ANIM_PT_Main(GovieToolsPanel, bpy.types.Panel):
    bl_idname = "ANIM_PT_Main"
    bl_label = "Animation"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        gui_functions.headline(
            layout, (0.2, "ACTIVE"), (0.4, "OBJECT NAME"), (1, "ANIMATION NAME")
        )

        layout.template_list(
            "ANIM_UL_List", "", scene, "objects", scene, "object_index"
        )


class ANIM_PT_Sub_Manage(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "ANIM_PT_Main"
    bl_label = "Manage Animation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        anim_settings = context.scene.animation_settings
        layout = self.layout
        layout.prop(anim_settings, "join_anim_name", text="Name")
        layout.operator(
            "scene.join_anim", text="Join Animation"
        ).anim_name = anim_settings.join_anim_name
        layout.operator(
            "scene.rename_anim", text="Rename Animation"
        ).anim_name = anim_settings.join_anim_name
        layout.operator("scene.seperate_anim", text="Separate Animation")


class ANIM_PT_Sub_Particles(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "ANIM_PT_Main"
    bl_label = "Bake Particles"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        particle_settings = context.scene.particle_settings
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        # particle settings
        column = layout.column(align=True, heading="Key")
        column.prop(particle_settings, "key_loc", text="Location")
        column.prop(particle_settings, "key_rot", text="Rotation")

        column.prop(particle_settings, "key_scale", text="Scale")
        column.prop(particle_settings, "key_vis", text="Visibility")
        layout.separator()
        layout.prop(particle_settings, "frame_offset", text="Frame Offset")
        layout.prop(particle_settings, "collection_name")

        # Bake Operator
        bake_particle_op = layout.operator(
            "object.bake_particles", text="Bake Particles"
        )
        bake_particle_op.KEYFRAME_LOCATION = particle_settings.key_loc
        bake_particle_op.KEYFRAME_ROTATION = particle_settings.key_rot
        bake_particle_op.KEYFRAME_SCALE = particle_settings.key_scale
        bake_particle_op.KEYFRAME_VISIBILITY = particle_settings.key_vis


class ANIM_PT_Sub_Simplify(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "ANIM_PT_Main"
    bl_label = "Simplify Animation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        anim_settings = context.scene.animation_settings
        layout.prop(anim_settings, "simplify_keyframes_enum", text="Mode")
        if anim_settings.simplify_keyframes_enum == "RATIO":
            layout.prop(anim_settings, "decimate_ratio", text="Ratio")
        else:
            layout.prop(anim_settings, "decimate_ratio", text="Error Margin")
        simplify_keyframe_op = layout.operator(
            "scene.simplify_keyframes", text="Simplify Keyframes"
        )
        simplify_keyframe_op.mode = anim_settings.simplify_keyframes_enum
        simplify_keyframe_op.decimate_ratio = anim_settings.decimate_ratio


class ANIM_PT_Sub_UVAnim(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "ANIM_PT_Main"
    bl_label = "UV Animation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("object.add_uv_anim", text="Add UV Animation")


class VIS_PT_Main(GovieToolsPanel, bpy.types.Panel):
    bl_idname = "VIS_PT_Main"
    bl_label = "Visibility"
    bl_order = 4

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Make objects hideable in the govie editor")

        gui_functions.headline(
            layout, (0.2, "ACTIVE"), (0.6, "OBJECT NAME"), (1, "VISIBLE")
        )

        layout.template_list("VIS_UL_List", "", scene, "objects", scene, "object_index")
        op_add = layout.operator("object.add_property", text="Add Property")
        op_rm = layout.operator("object.remove_property", text="Remove Property")
        op_add.property_type = "visibility"
        op_rm.property_type = "visibility"


class CLICK_PT_Main(GovieToolsPanel, bpy.types.Panel):
    bl_idname = "CLICK_PT_Main"
    bl_label = "Clickable Object"
    bl_order = 5

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Make objects clickable in the govie editor")

        gui_functions.headline(layout, (0.2, "ACTIVE"), (0.8, "OBJECT NAME"))

        layout.template_list(
            "CLICK_UL_List", "", scene, "objects", scene, "object_index"
        )
        op_add = layout.operator("object.add_property", text="Add Property")
        op_rm = layout.operator("object.remove_property", text="Remove Property")
        op_add.property_type = "clickable"
        op_rm.property_type = "clickable"


class GOVIE_PT_Export_Main(GovieToolsPanel, bpy.types.Panel):
    bl_idname = "GOVIE_PT_Export_Main"
    bl_label = "GLB Export"
    bl_order = 5

    def draw(self, context):
        return


class GOVIE_PT_Export_Sub_Verify(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "GOVIE_PT_Export_Main"
    bl_label = "Cleanup"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        mat_name_list = context.scene.mat_name_list

        if len(mat_name_list) > 0:
            layout.label(text="Check Materials:")
            for mat_name in mat_name_list:
                layout.label(text=mat_name)

        layout.operator("object.check_tex_nodes", text="Find Empty Image Nodes")
        layout.operator("object.cleanup_mesh", text="Cleanup Mesh")


class GOVIE_PT_Export_Sub_Settings(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "GOVIE_PT_Export_Main"
    bl_idname = "GOVIE_PT_Export_Sub_Settings"
    bl_label = "Export Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        # align properties to the right
        layout.use_property_split = True
        # hide keyframing icon
        layout.use_property_decorate = False
        exp_settings = context.scene.export_settings

        column = layout.column(align=True, heading="Preset")
        column.prop(context.scene, "glb_preset_dropdown")

        # layout.separator()
        column = layout.column(align=True, heading="Optimization")
        column.prop(
            exp_settings,
            "join_objects",
        )


class GOVIE_PT_EXPORT_Sub_Export(GovieToolsPanel, bpy.types.Panel):
    bl_parent_id = "GOVIE_PT_Export_Main"
    bl_label = "Export and Preview"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene.export_settings, "glb_filename")
        # layout.prop(scene, "glb_file_dropdown")
        layout.operator("scene.gltf_quick_export", text="Export")
        row = layout.row()
        row.operator("scene.open_export_folder", icon="FILEBROWSER")
        row.operator("scene.open_web_preview", text="Preview", icon="WORLD")


class HelpPanel(GovieToolsPanel, bpy.types.Panel):
    bl_idname = "GOVIE_PT_help_panel"
    bl_label = "Help"
    bl_order = 6

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        lang = bpy.app.translations.locale
        if lang == "en_US":
            layout.label(text="To use the full potential of the add-on,")
            layout.label(text="you may sign up for a free govie account.")
            layout.label(text="Further documentation can be found here:")
            layout.operator(
                "scene.open_link", text="Govie Tools Documentation", icon="HELP"
            ).url = "https://govie-editor.de/en/help/govie-tools/"

        if lang == "de_DE":
            layout.label(text="Um das volle Potential dieses Add-ons zu nutzen,")
            layout.label(
                text="empfehlen wir einen kostenlosen Account des Govie Editors anzulegen"
            )
            layout.label(text="Weitere Dokumentation findet sich hier:")
            layout.operator(
                "scene.open_link", text="Add-on Documentation", icon="HELP"
            ).url = "https://govie-editor.de/help-section/blender/"


def register():
    bpy.utils.register_class(ANIM_UL_List)
    bpy.utils.register_class(VIS_UL_List)
    bpy.utils.register_class(CLICK_UL_List)
    bpy.utils.register_class(ANIM_PT_Main)
    bpy.utils.register_class(ANIM_PT_Sub_Manage)
    bpy.utils.register_class(ANIM_PT_Sub_Particles)
    bpy.utils.register_class(ANIM_PT_Sub_Simplify)
    bpy.utils.register_class(ANIM_PT_Sub_UVAnim)
    bpy.utils.register_class(VIS_PT_Main)
    bpy.utils.register_class(CLICK_PT_Main)
    bpy.utils.register_class(GOVIE_PT_Export_Main)
    bpy.utils.register_class(GOVIE_PT_Export_Sub_Verify)
    bpy.utils.register_class(GOVIE_PT_Export_Sub_Settings)
    bpy.utils.register_class(GOVIE_PT_EXPORT_Sub_Export)
    bpy.utils.register_class(HelpPanel)


def unregister():
    bpy.utils.unregister_class(ANIM_UL_List)
    bpy.utils.unregister_class(VIS_UL_List)
    bpy.utils.unregister_class(CLICK_UL_List)
    bpy.utils.unregister_class(ANIM_PT_Main)
    bpy.utils.unregister_class(ANIM_PT_Sub_Manage)
    bpy.utils.unregister_class(ANIM_PT_Sub_Particles)
    bpy.utils.unregister_class(ANIM_PT_Sub_Simplify)
    bpy.utils.unregister_class(ANIM_PT_Sub_UVAnim)
    bpy.utils.unregister_class(VIS_PT_Main)
    bpy.utils.unregister_class(CLICK_PT_Main)
    bpy.utils.unregister_class(GOVIE_PT_Export_Main)
    bpy.utils.unregister_class(GOVIE_PT_Export_Sub_Verify)
    bpy.utils.unregister_class(GOVIE_PT_Export_Sub_Settings)
    bpy.utils.unregister_class(GOVIE_PT_EXPORT_Sub_Export)
    bpy.utils.unregister_class(HelpPanel)
