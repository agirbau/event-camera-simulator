import os
import sys
import cv2
import bpy
import logging
import math
import numpy as np
from mathutils import Vector, Euler
from ecs.sensor import DvsSensor
from ecs.lib import EventBuffer, EventDisplay, EventVideo, DatFile
from ecs.logger import capture_blender_output

class BlenderDVSCamera(DvsSensor):
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger()

        self.camera = self.init_camera()
        
        w,h = self.cfg.event_camera.resolution
        self.set_shape(w, h)
        self.set_dvs_sensor(th_pos=0.15, th_neg=0.15, th_n=0.05, lat=500, tau=300, jit=100, bgn=0.0001)
        self.init_tension()
        self.init_bgn_hist(
            self.cfg.event_camera.noise_pos,
            self.cfg.event_camera.noise_neg
        )

        self.event_buffer = EventBuffer(0)

    def init_camera(self):
        if "DVS" in bpy.data.objects:
            bpy.data.objects['DVS'].select_set(True)
            bpy.ops.object.delete()

        cam_data = bpy.data.cameras.new("DVS")
        
        cam_data.lens = self.cfg.event_camera.focal_length
        cam_data.sensor_width = self.cfg.event_camera.sensor_size
        cam_data.clip_end = 5000

        camera = bpy.data.objects.new("DVS", cam_data)
        camera.location = Vector(self.cfg.event_camera.position)
        camera.rotation_euler = Euler([math.radians(r) for r in self.cfg.event_camera.rotation])

        self.scene = bpy.context.scene
        self.scene.camera = camera

        master_collection = bpy.context.collection
        master_collection.objects.link(camera)

        return camera

    def update_position(self, step):
        position = np.array(self.camera.location)
        velocity = np.array(self.cfg.camera.velocity)

        delta_time = 1 / self.cfg.render.fps
        elapsed_time = step * delta_time
        new_position = position + velocity * elapsed_time
        self.camera.location = new_position

        self.logger.debug(f"Updated DVS Position: {new_position}")

    def collect_image(self, step):
        # dt = (1 / self.cfg.render.fps) * 10**6
        dt = 1000

        with capture_blender_output():
            render_file = os.path.join(self.cfg.render.out, 'frames',  f'scene_frame_{step}.png')
            self.scene.render.filepath = render_file
            bpy.ops.render.render(write_still=1)

        im = cv2.imread(render_file)

        if step == 0:
            self.logger.info(f"Init Event Camera Image: {im.shape}")
            self.init_image(im)
        else:
            self.logger.debug(f"Frame Delay: {dt}")
            self.logger.debug(f"Image shape: {im.shape}")

            pk = self.update(im, dt)

            self.logger.debug(f"PK: {pk}")
            self.event_buffer.increase_ev(pk)

    def complete(self):
        w,h = self.cfg.event_camera.resolution
        ts, x, y, p = self.event_buffer.export()
        filename = os.path.join(self.cfg.render.out, self.cfg.render.event_file)

        self.logger.debug(f"Timestamps: {ts.shape}")

        output_file = DatFile(filename)
        output_file.write(ts, x, y, p, 'dvs', width=w, height=h)

        event_video = EventVideo(self.cfg)
        event_video.create()
