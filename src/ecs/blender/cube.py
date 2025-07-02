import os
import bpy

class Cube():
    def __init__(self, cfg, name):
        self.cfg = cfg
        self.name = name
        self.obj = self._create_object()

    def _create_object(self):
        if self.name in bpy.data.objects:
            raise f"Object {self.name} already exists!"

        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.name = self.name
        return 
    
    def _create_texture(self):
        matname = "CheeseMapping"
        texname = "texCheeseMapping"

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

        self.obj.data.materials.append(material)

    def set_location(self, location):
        self.obj.location = location
