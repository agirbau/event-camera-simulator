import bpy

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Find existing image texture node (assume first one found)
    tex_node = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)
    if not tex_node:
        print(f"Skipping material '{mat.name}' (no image texture found).")
        continue

    # Clear existing nodes EXCEPT the texture node
    for node in nodes:
        if node != tex_node:
            nodes.remove(node)

    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Metallic'].default_value = 0.0

    # Add Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)

    # Reconnect nodes
    links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    print(f"Updated material: {mat.name}")
