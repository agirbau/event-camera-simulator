import os
import bpy

from ecs.sensor import Blender_DvsSensor

class Drone():
    def __init__(self, cfg, name):
        self.cfg = cfg
        self.name = name
        self.obj = self._create_object()
        self.camera = self._init_camera()

    def _create_object(self):
        if self.name in bpy.data.objects:
            bpy.data.objects[self.name].select_set(True)
        else:
            bpy.ops.mesh.primitive_cube_add()

        obj = bpy.context.active_object
        obj.name = self.name
        return 

    def _init_camera(self):
        if self.name in bpy.data.objects:
            bpy.data.objects[self.name].select_set(True)

            existing_sensor = bpy.data.objects[self.name]
            angle = existing_sensor.rotation_euler
            position = existing_sensor.location

            bpy.ops.object.delete()


        ppsee = Blender_DvsSensor(self.name)
        ppsee.set_sensor(nx=360, ny=160, pp=0.015)
        ppsee.set_dvs_sensor(th_pos=0.15, th_neg=0.15, th_n=0.05, lat=500, tau=300, jit=100, bgn=0.0001)
        ppsee.set_sensor_optics(8)
        scene = bpy.context.scene
        master_collection = bpy.context.collection

        master_collection.objects.link(ppsee.cam)
        scene.camera = ppsee.cam
        ppsee.set_angle(angle)
        ppsee.set_position(position)
        ppsee.set_speeds([0, 1000, 0], [0.0, 0.0, 0.0])

        ppsee.init_tension()
        ppsee.init_bgn_hist(os.path.join(self.cfg.render.input, self.cfg.render.noise_pos), os.path.join(self.cfg.render.input, self.cfg.render.noise_neg))

        return ppsee

    def set_location(self, location):
        self.obj.location = location

    def set_rotation(self, angle):
        self.obj.rotation_euler = angle

    def set_speed(self, speed):
        self.speed = speed

    def update_timestep(self, dt, speed):
        # TODO: Update the position depending on the speed vector
        pass