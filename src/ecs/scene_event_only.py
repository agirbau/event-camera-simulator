import os
import bpy
import logging
from ecs.logger import capture_blender_output
from ecs.sensor import BlenderCamera, BlenderObject, BlenderDVSCamera, BlenderLiDAR

class SceneEventOnly():
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger()

        self.scene = self.load_blend_file()
        self.camera = BlenderCamera(cfg)
        self.lidar = BlenderLiDAR(cfg)
        self.dvs = BlenderDVSCamera(cfg)
        self.mavic = BlenderObject(cfg, 'dji_mavic', 'DJI Mavic 3 Classic Drone')

        self.init_render()
        self.save()

        self.logger.info("Loaded Event Only Scene Renderer")

    def load(self):
        with capture_blender_output():
            bpy.ops.wm.open_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

    def save(self):
        with capture_blender_output():
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

    def load_blend_file(self):
        try:
            self.load()
        except:
            self.save()

        bpy.ops.object.select_all(action='DESELECT')

        return bpy.context.scene

    def init_render(self):
        w,h = self.cfg.event_camera.resolution

        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.resolution_x = w
        self.scene.render.resolution_y = h
        self.scene.render.fps = self.cfg.render.fps

    def render(self, step=0):
        self.logger.debug(f"Render Frame: {step}/{self.cfg.render.steps}")

        self.dvs.update_position(step)
        self.mavic.update_position(step)
        self.camera.update_position(step)
        # self.lidar.update_position(step)

        self.dvs.collect_image(step)
        self.camera.collect_image(step)
        # self.lidar.collect_image(step)
    
    def complete(self):
        self.dvs.complete()
        self.camera.complete()
        # self.lidar.complete()
        self.save()