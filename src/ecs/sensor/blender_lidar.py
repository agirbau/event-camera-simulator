import os
import sys
import bpy
import cv2
import logging
import math
import numpy as np
from mathutils import Vector, Euler
from ecs.logger import capture_blender_output

class BlenderLiDAR():
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger()

        self.range_scanner = self.load_range_scanner()

        self.camera = self.init_camera()

    def load_range_scanner(self):
        bpy.ops.preferences.addon_enable(module="range_scanner")
        bpy.ops.wm.save_userpref()
        return sys.modules.get("range_scanner")

    def init_camera(self):
        if "LiDAR" in bpy.data.objects:
            bpy.data.objects['LiDAR'].select_set(True)
            bpy.ops.object.delete()

        cam_data = bpy.data.cameras.new("LiDAR")
        camera = bpy.data.objects.new("LiDAR", cam_data)
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

        self.logger.debug(f"Updated LiDAR Position: {new_position}")

    def collect_image(self, step):
        self.range_scanner.ui.user_interface.scan_rotating(
            bpy.context, 
            scannerObject=bpy.context.scene.objects["LiDAR"],

            xStepDegree=1,
            fovX=360.0,
            yStepDegree=1,
            fovY=30.0,
            rotationsPerSecond=20,

            reflectivityLower=0.0,
            distanceLower=0.0,
            reflectivityUpper=0.0,
            distanceUpper=100.0,
            maxReflectionDepth=10,
            
            enableAnimation=True,
            frameStart=step,
            frameEnd=step+1,
            frameStep=1,
            frameRate=24,

            addNoise=False,
            noiseType='gaussian',
            mu=0.0,
            sigma=0.01,
            noiseAbsoluteOffset=0.0,
            noiseRelativeOffset=0.0, 

            simulateRain=False,
            rainfallRate=0.0, 

            addMesh=True,

            exportLAS=False,
            exportHDF=False,
            exportCSV=True,
            exportPLY=False,
            exportSingleFrames=True,
            dataFilePath=self.cfg.render.out,
            # dataFilePath="/Users/felix/Projects/LINA/02_event-cameras/event-camera-simulator/out/leipzig",
            dataFileName="rs",
            
            debugLines=False,
            debugOutput=False,
            outputProgress=True,
            measureTime=False,
            singleRay=False,
            destinationObject=None,
            targetObject=None
        )  

    def complete(self):
        pass
