import bpy


class JoinAnimationOperator(bpy.types.Operator):
    bl_idname = "scene.join_anim"
    bl_label = "Join Animation"
    bl_description = "Join animations for all selected objects by making an NLA strip for each object and naming the track consistently"
    bl_options = {"REGISTER"}

    anim_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        sel_objects = context.selected_objects
        for obj in sel_objects:
            if obj.animation_data is None:
                continue
            if obj.animation_data.action is None:
                continue
            # if hasattr(obj.animation_data,"action"):
            action = obj.animation_data.action
            track = obj.animation_data.nla_tracks.new()
            track.strips.new(self.anim_name, int(action.frame_start), action)
            track.name = self.anim_name
            obj.animation_data.action = None
        return {"FINISHED"}


class SeperateAnimationOperator(bpy.types.Operator):
    bl_idname = "scene.seperate_anim"
    bl_label = "Separate Animation"
    bl_description = "Transform NLA strips back to Keyframes to make them editable again. Make sure to select all objects you want to transform back."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        sel_objects = context.selected_objects
        for obj in sel_objects:
            if obj.animation_data is None:
                continue

            if len(obj.animation_data.nla_tracks) == 0:
                continue

            # set actions
            track = obj.animation_data.nla_tracks[0]
            action_name = track.strips[0].name
            action = bpy.data.actions.get(action_name)
            obj.animation_data.action = action

            # remove track
            obj.animation_data.nla_tracks.remove(track)

        return {"FINISHED"}


class RenameNLAAnimationOperator(bpy.types.Operator):
    bl_idname = "scene.rename_anim"
    bl_label = "Rename Animation"
    bl_description = "Rename NLA Tracks on selected objects"
    bl_options = {"REGISTER"}

    anim_name: bpy.props.StringProperty()
    index = 0

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        sel_objects = context.selected_objects
        for obj in sel_objects:
            track = obj.animation_data.nla_tracks[self.index]
            track.name = self.anim_name

        return {"FINISHED"}
