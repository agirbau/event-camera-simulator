import os
import bpy
import cv2
import logging
import math
import numpy as np
from mathutils import Vector, Euler
from ecs.logger import capture_blender_output

class BlenderCamera():
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger()

        self.camera = self.init_camera()
        self.video_writer = self.init_video()

    def init_video(self):
        w,h = self.cfg.camera.resolution

        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        return cv2.VideoWriter(os.path.join(self.cfg.render.out, self.cfg.render.video_file), fourcc, self.cfg.render.fps, (w, h))

    def init_camera(self):
        if "Camera" in bpy.data.objects:
            bpy.data.objects['Camera'].select_set(True)
            bpy.ops.object.delete()

        cam_data = bpy.data.cameras.new("Camera")
        
        cam_data.lens = self.cfg.camera.focal_length
        cam_data.sensor_width = self.cfg.camera.sensor_size
        cam_data.clip_end = 5000

        camera = bpy.data.objects.new("Camera", cam_data)
        camera.location = Vector(self.cfg.camera.position)
        camera.rotation_euler = Euler([math.radians(r) for r in self.cfg.camera.rotation])

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

        self.logger.debug(f"Updated Camera Position: {new_position}")

    def collect_image(self, step):
        with capture_blender_output():
            render_file = os.path.join(self.cfg.render.out, 'frames',  f'scene_frame_{step}.png')
            self.scene.render.filepath = render_file
            bpy.ops.render.render(write_still=1)

        im = cv2.imread(render_file)
        self.video_writer.write(im)

    def complete(self):
        self.video_writer.release()
