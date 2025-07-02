import os
import bpy
import math
import cv2
import logging
from mathutils import Vector

from ecs.sensor import Blender_DvsSensor
from ecs.lib import EventBuffer, EventDisplay, EventVideo, DatFile
from ecs.logger import capture_blender_output
from ecs.blender import Cube

class BlenderScene():
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger()

        self.scene = self.load_blend_file()
        self.ppsee = self.init_camera()

        self.init_render()

    def load_blend_file(self):
        with capture_blender_output():
            try:
                bpy.ops.wm.open_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))
            except:
                bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

        bpy.ops.object.select_all(action='DESELECT')

        return bpy.context.scene

    def init_camera(self):
        angle = [0.0,0.0,0.0]
        position = [0,0,10]

        if "Camera" in bpy.data.objects:
            bpy.data.objects['Camera'].select_set(True)
            bpy.ops.object.delete()

        if "Main_Drone" in bpy.data.objects:
            bpy.data.objects['Main_Drone'].select_set(True)

            existing_sensor = bpy.data.objects['LiDAR']
            angle = existing_sensor.rotation_euler
            position = existing_sensor.location

            bpy.ops.object.delete()

        ppsee = Blender_DvsSensor("Main_Drone")
        # ppsee.set_shape(640, 360)
        ppsee.set_sensor(nx=640, ny=360, pp=0.015)
        ppsee.set_dvs_sensor(th_pos=0.15, th_neg=0.15, th_n=0.05, lat=500, tau=300, jit=100, bgn=0.0001)
        ppsee.set_sensor_optics(8)


        scene = bpy.context.scene
        master_collection = bpy.context.collection
        master_collection.objects.link(ppsee.cam)
        
        scene.camera = ppsee.cam
        ppsee.set_angle(angle)
        ppsee.set_position(position)
        ppsee.set_speeds([0, 250, 0], [0.0, 0.0, 0.0])

        ppsee.init_tension()

        ppsee.init_bgn_hist(
            self.cfg.event_camera.noise_pos,
            self.cfg.event_camera.noise_neg
        )
        # ppsee.init_bgn_hist(os.path.join(self.cfg.render.input, self.cfg.render.noise_pos), os.path.join(self.cfg.render.input, self.cfg.render.noise_neg))

        return ppsee

    def init_render(self):
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.filepath = os.path.join(self.cfg.render.out, 'scene_frame_0.png')
        self.scene.render.resolution_x = self.ppsee.def_x
        self.scene.render.resolution_y = self.ppsee.def_y

        self.event_display = EventDisplay("Events", self.ppsee.def_x, self.ppsee.def_y, 10_000)
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.video_writer = cv2.VideoWriter(os.path.join(self.cfg.render.out, self.cfg.render.video_file), fourcc, 20.0, (self.ppsee.def_x, self.ppsee.def_y))
        self.event_buffer = EventBuffer(0)


        with capture_blender_output():
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

    def render(self, step=0):
        # dt = self.cfg.render.frame_delay
        dt = (1 / self.cfg.render.fps) * 10**6

        # TODO: Update Positions of all Objects
        # TODO: Why is the frame delay different for update_time and update functions?

        self.ppsee.update_time(1/dt)
        self.ppsee.print_position()

        with capture_blender_output():
            render_file = f'scene_frame_{step}.png'

            self.scene.render.filepath = os.path.join(self.cfg.render.out, render_file)
            bpy.ops.render.render(write_still=1)

        im = cv2.imread(os.path.join(self.cfg.render.out, render_file))
        self.video_writer.write(im)

        if step == 0:
            self.ppsee.init_image(im)
        else:
            pk = self.ppsee.update(im, dt)
            # self.event_display.update(pk, dt)
            self.event_buffer.increase_ev(pk)
            # bpy.data.objects['Light'].data.energy += 0.01
    
    def complete(self):
        self.video_writer.release()

        ts, x, y, p = self.event_buffer.export()

        self.logger.info(ts.shape)

        filename = os.path.join(self.cfg.render.out, self.cfg.render.event_file)
        output_file = DatFile(filename)
        output_file.write(ts, x, y, p, 'dvs', width=640, height=360)

        with capture_blender_output():
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

        event_video = EventVideo(self.cfg)
        event_video.create()
