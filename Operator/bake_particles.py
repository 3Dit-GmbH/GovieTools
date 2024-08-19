import bpy


class BakeParticlesOperator(bpy.types.Operator):
    """Bake all Particles to Keyframes. The particles need to have an instance object set. The baked instances are moved to a new collection."""

    bl_idname = "object.bake_particles"
    bl_label = "Bake Particles"

    KEYFRAME_LOCATION: bpy.props.BoolProperty()
    KEYFRAME_ROTATION: bpy.props.BoolProperty()
    KEYFRAME_SCALE: bpy.props.BoolProperty()
    # Viewport and render visibility.
    KEYFRAME_VISIBILITY: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return False

        if not hasattr(obj, "particle_systems"):
            return False

        if not len(obj.particle_systems) > 0:
            return False

        for particlesys in obj.particle_systems:
            if bpy.data.particles[particlesys.settings.name].instance_object is None:
                return False

        return True

    def create_particle_collection(self, collection_name):
        # Create or clear the particle collection.
        # Create a new collection and link it to the scene.
        collection_name = bpy.context.scene.particle_settings.collection_name
        particle_collection = bpy.data.collections.get(collection_name)

        if particle_collection is None:
            particle_collection = bpy.data.collections.new(collection_name)

        if bpy.context.scene.collection.children.get(collection_name) is None:
            bpy.context.scene.collection.children.link(particle_collection)

        # remove all objects from the particle collection
        if len(particle_collection.objects) > 0:
            rem_obj_names = []
            for obj in particle_collection.objects:
                rem_obj_names.append(obj.name)

            for rem_name in rem_obj_names:
                bpy.data.objects.remove(bpy.data.objects[rem_name])

    def create_objects_for_particles(self, ps, obj, collection_name):
        # Duplicate the given object for every particle and return the duplicates.
        # Use instances instead of full copies.
        obj_list = []
        mesh = obj.data
        particle_collection = bpy.data.collections.get(collection_name)

        for particle in ps.particles:
            dupli = bpy.data.objects.new(name=obj.name, object_data=mesh)
            particle_collection.objects.link(dupli)
            obj_list.append(dupli)

            # copy modifiers to duplicates
            # adapted from: https://blender.stackexchange.com/a/4883
            for modifierOrig in obj.modifiers:
                modifierNew = dupli.modifiers.new(modifierOrig.name, modifierOrig.type)
                # collect names of writable properties
                properties = [
                    p.identifier
                    for p in modifierOrig.bl_rna.properties
                    if not p.is_readonly
                ]

                # copy those properties
                for prop in properties:
                    setattr(modifierNew, prop, getattr(modifierOrig, prop))

        return obj_list

    def match_and_keyframe_objects(self, ps, obj_list, start_frame, end_frame):
        # Match and keyframe the objects to the particles for every frame in the
        # given range.
        frame_offset = bpy.context.scene.particle_settings.frame_offset
        for frame in range(start_frame, end_frame + 1, frame_offset):
            bpy.context.scene.frame_set(frame)
            for p, obj in zip(ps.particles, obj_list):
                self.match_object_to_particle(p, obj)
                self.keyframe_obj(obj)

    def match_object_to_particle(self, p, obj):
        # Match the location, rotation, scale and visibility of the object to
        # the particle.
        loc = p.location
        rot = p.rotation
        size = p.size
        # Set rotation mode to quaternion to match particle rotation.
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = rot

        if self.KEYFRAME_VISIBILITY:
            if p.alive_state != "ALIVE":
                size *= 0.01

        obj.location = loc
        obj.scale = (size, size, size)

        # obj.hide_viewport = not(vis)
        # obj.hide_render = not(vis)

    def keyframe_obj(self, obj):
        # Keyframe location, rotation, scale and visibility if specified.
        if self.KEYFRAME_LOCATION:
            obj.keyframe_insert("location")
        if self.KEYFRAME_ROTATION:
            obj.keyframe_insert("rotation_quaternion")
        if self.KEYFRAME_SCALE:
            obj.keyframe_insert("scale")
        # if self.KEYFRAME_VISIBILITY:
        #     obj.keyframe_insert("hide_viewport")
        #     obj.keyframe_insert("hide_render")

    def execute(self, context):
        # go to start frame
        bpy.context.scene.frame_set(0)

        collection_name = bpy.context.scene.particle_settings.collection_name
        self.create_particle_collection(collection_name)

        # get emitter and instance
        emitter = bpy.context.object
        ps_list = emitter.particle_systems
        for i, ps in enumerate(ps_list):
            instance = ps.settings.instance_object

            depsgraph = bpy.context.evaluated_depsgraph_get()

            # Extract locations

            ps = depsgraph.objects[emitter.name].particle_systems[i]

            # update ps hack
            # bpy.data.particles[ps.name].count += 1
            # bpy.data.particles[ps.name].count -= 1

            start_frame = bpy.context.scene.frame_start
            end_frame = bpy.context.scene.frame_end
            obj_list = self.create_objects_for_particles(ps, instance, collection_name)
            self.match_and_keyframe_objects(ps, obj_list, start_frame, end_frame)

        # Simplify
        bpy.ops.object.select_all(action="DESELECT")

        for obj in bpy.data.collections[collection_name].all_objects:
            obj.select_set(True)

        return {"FINISHED"}


def register():
    bpy.utils.register_class(BakeParticlesOperator)


def unregister():
    bpy.utils.unregister_class(BakeParticlesOperator)
