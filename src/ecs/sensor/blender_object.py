import bpy
import logging
import math
import numpy as np
from mathutils import Vector, Euler

class BlenderObject():
    def __init__(self, cfg, name, collection):
        self.cfg = cfg
        self.name = name
        self.collection = collection
        self.object_cfg = next(o for o in cfg.objects if o.name == name )
        self.logger = logging.getLogger()

        self.object = self.init_object()

    def delete_collection(self):
        collection = bpy.data.collections.get(self.collection)
        if collection:
            objects_to_delete = list(collection.objects)
            for obj in objects_to_delete:
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)

            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(collection)

    def init_object(self):
        # self.delete_collection()

        # Load collection from asset blend file
        with bpy.data.libraries.load(self.object_cfg.asset, link=False) as (data_from, data_to):
            if self.collection in data_from.collections:
                data_to.collections.append(self.collection)

        new_collection = data_to.collections[0]
        bpy.context.scene.collection.children.link(new_collection)

        # Select the parent item in the collection
        collection = bpy.data.collections.get(self.collection)
        if collection:
            parent_obj = None
            for obj in collection.objects:
                if obj.parent is None:
                    parent_obj = obj
                    break

        obj = parent_obj

        self.logger.debug(f'Select object {obj}')

        obj.location = Vector(self.object_cfg.position)
        obj.rotation_euler = Euler([math.radians(r) for r in self.object_cfg.rotation])

        return obj

    def update_position(self, step):
        position = np.array(self.object.location)
        velocity = np.array(self.object_cfg.velocity)

        delta_time = 1 / self.cfg.render.fps
        elapsed_time = step * delta_time
        new_position = position + velocity * elapsed_time
        self.object.location = new_position

        self.logger.debug(f"Updated Object Position: {new_position}")