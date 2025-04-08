import os
import bpy
import math
import cv2
import logging
from mathutils import Vector

from ecs.sensor import Blender_DvsSensor
from ecs.lib import EventBuffer, EventDisplay, EventVideo, DatFile
from ecs.logger import capture_blender_output

class BlenderScene():
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger()

        self.scene = self.load_blend_file()
        self.ppsee = self.init_camera()

        self.init_lighting()
        self.init_cube()
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
        if "Camera" in bpy.data.objects:
            bpy.data.objects['Camera'].select_set(True)
            bpy.ops.object.delete()

        if "Sensor" in bpy.data.objects:
            bpy.data.objects['Sensor'].select_set(True)
            bpy.ops.object.delete()

        ppsee = Blender_DvsSensor("Sensor")
        ppsee.set_sensor(nx=360, ny=160, pp=0.015)
        ppsee.set_dvs_sensor(th_pos=0.15, th_neg=0.15, th_n=0.05, lat=500, tau=300, jit=100, bgn=0.0001)
        ppsee.set_sensor_optics(8)
        scene = bpy.context.scene
        master_collection = bpy.context.collection

        master_collection.objects.link(ppsee.cam)
        scene.camera = ppsee.cam
        ppsee.set_angle([0.0, 0.0, 0.0])
        ppsee.set_position([0.0, 0.0, 10.0])
        ppsee.set_speeds([0.0, 0, 0], [0.0, 0.0, 10])

        ppsee.init_tension()
        ppsee.init_bgn_hist(os.path.join(self.cfg.render.input, self.cfg.render.noise_pos), os.path.join(self.cfg.render.input, self.cfg.render.noise_neg))

        return ppsee

    def init_cube(self):

        if "Cube" in bpy.data.objects:
            bpy.data.objects['Cube'].select_set(True)
            bpy.ops.object.delete()
        
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        matname = "CheeseMapping"
        texname = "texCheeseMapping"

        newcube = bpy.context.active_object
        newcube.name = 'Cube'

        material = bpy.data.materials.new(name=matname)
        material.use_nodes = True
        nodes = material.node_tree.nodes

        for node in nodes:
            nodes.remove(node)

        texture = bpy.data.textures.new(texname, 'IMAGE')
        texture.extension = 'REPEAT'
        texture.image = bpy.data.images.load(os.path.join(os.getcwd(), self.cfg.render.input, self.cfg.render.texture))

        shader_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        shader_node.location = (0, 0)

        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.location = (-300, 0)
        texture_node.image = texture.image

        material_output_node = nodes.new(type='ShaderNodeOutputMaterial')
        material_output_node.location = (300, 0)

        links = material.node_tree.links
        links.new(texture_node.outputs["Color"], shader_node.inputs["Base Color"])
        links.new(shader_node.outputs["BSDF"], material_output_node.inputs["Surface"])

        newcube.data.materials.append(material)

    def init_lighting(self):
        if "Light" in bpy.data.objects:
            bpy.data.objects['Light'].select_set(True)
            bpy.ops.object.delete()

        light_data = bpy.data.lights.new(name="Light", type='SUN')
        light_object = bpy.data.objects.new(name="Light", object_data=light_data)

        bpy.context.collection.objects.link(light_object)
        
        light_object.location = Vector((5, 5, 5))
        light_object.rotation_euler = Vector((0.785, 0, 0.785))
        light_data.energy = 2
        light_data.color = Vector((1.0, 1.0, 0.9))

    def init_render(self):
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.filepath = os.path.join(self.cfg.render.out, self.cfg.render.scene_image)
        self.scene.render.resolution_x = self.ppsee.def_x
        self.scene.render.resolution_y = self.ppsee.def_y

        self.event_display = EventDisplay("Events", self.ppsee.def_x, self.ppsee.def_y, 10_000)
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.video_writer = cv2.VideoWriter(os.path.join(self.cfg.render.out, self.cfg.render.video_file), fourcc, 20.0, (self.ppsee.def_x, self.ppsee.def_y))
        self.event_buffer = EventBuffer(0)


        with capture_blender_output():
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

    def render(self, step=0):
        dt = self.cfg.render.frame_delay

        self.ppsee.update_time(1/dt)
        self.ppsee.print_position()

        with capture_blender_output():
            bpy.ops.render.render(write_still=1)

        im = cv2.imread(os.path.join(self.cfg.render.out, self.cfg.render.scene_image))
        self.video_writer.write(im)

        if step == 0:
            self.ppsee.init_image(im)
        else:
            pk = self.ppsee.update(im, dt)
            self.event_display.update(pk, dt)
            self.event_buffer.increase_ev(pk)
            # bpy.data.objects['Light'].data.energy += 0.01
    
    def complete(self):
        self.video_writer.release()

        ts, x, y, p = self.event_buffer.export()

        self.logger.info(ts.shape)

        filename = os.path.join(self.cfg.render.out, self.cfg.render.event_file)
        output_file = DatFile(filename)
        output_file.write(ts, x, y, p, 'dvs', width=360, height=160)

        with capture_blender_output():
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.cfg.render.out, self.cfg.render.blender_file))

        event_video = EventVideo(self.cfg)
        event_video.create()