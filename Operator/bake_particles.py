import bpy

class BakeParticlesOperator(bpy.types.Operator):
    """Bake all Particles to Keyframes. The baked instances are moved to a new collection with the name enterd above."""
    bl_idname = "object.bake_particles"
    bl_label = "Bake Particles"

    KEYFRAME_LOCATION : bpy.props.BoolProperty()
    KEYFRAME_ROTATION : bpy.props.BoolProperty()
    KEYFRAME_SCALE : bpy.props.BoolProperty()
    KEYFRAME_VISIBILITY : bpy.props.BoolProperty()  # Viewport and render visibility.  

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj :
            if obj.type == "MESH":
                if len(obj.particle_systems) > 0:
                    return True
        return False

    def create_objects_for_particles(self, ps, obj):
        # Duplicate the given object for every particle and return the duplicates.
        # Use instances instead of full copies.
        obj_list = []
        mesh = obj.data

        # Create a new collection and link it to the scene.
        collection_name = bpy.context.scene.particle_settings.collection_name
        particle_collection = bpy.data.collections.get(collection_name)

        if particle_collection is None:
           particle_collection = bpy.data.collections.new(collection_name)

        if bpy.context.scene.collection.children.get(collection_name) is None:
            bpy.context.scene.collection.children.link(particle_collection)

        for particle in ps.particles:
            dupli = bpy.data.objects.new(name=obj.name, object_data=mesh)
            particle_collection.objects.link(dupli)
            obj_list.append(dupli)
            
        return obj_list

    def match_and_keyframe_objects(self, ps, obj_list, start_frame, end_frame):
        # Match and keyframe the objects to the particles for every frame in the
        # given range.
        frame_offset = bpy.context.scene.particle_settings.frame_offset
        for frame in range(start_frame, end_frame + 1,frame_offset):
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
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot

        if self.KEYFRAME_VISIBILITY:
            if p.alive_state != 'ALIVE':
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

        # get emitter and instance
        emitter = bpy.context.object
        ps_list = emitter.particle_systems
        for i,ps in enumerate(ps_list):
            instance = ps.settings.instance_object

            depsgraph = bpy.context.evaluated_depsgraph_get()

            # Extract locations

            ps = depsgraph.objects[emitter.name].particle_systems[i]
            
            # update ps hack
            # bpy.data.particles[ps.name].count += 1
            # bpy.data.particles[ps.name].count -= 1

            start_frame = bpy.context.scene.frame_start
            end_frame = bpy.context.scene.frame_end
            obj_list = self.create_objects_for_particles(ps, instance)
            self.match_and_keyframe_objects(ps, obj_list, start_frame, end_frame)

        # Simplify
        bpy.ops.object.select_all(action='DESELECT')

        collection_name = bpy.context.scene.particle_settings.collection_name
        for obj in bpy.data.collections[collection_name].all_objects:
            obj.select_set(True)

       
        return {'FINISHED'}
