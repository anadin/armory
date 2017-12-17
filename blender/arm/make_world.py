import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import arm.write_probes as write_probes
import arm.assets as assets
import arm.utils
import arm.node_utils as node_utils
import arm.log as log
import arm.make_state as state

def build():
    worlds = []
    for scene in bpy.data.scenes:
        if scene.arm_export and scene.world != None and scene.world not in worlds:
            worlds.append(scene.world)
            build_node_tree(scene.world)

def build_node_tree(world):
    wname = arm.utils.safestr(world.name)
    wrd = bpy.data.worlds['Arm']
    wrd.world_defs = ''
    rpdat = arm.utils.get_rp()
    
    # Traverse world node tree
    parsed = False
    if world.node_tree != None:
        output_node = node_utils.get_node_by_type(world.node_tree, 'OUTPUT_WORLD')
        if output_node != None:
            parse_world_output(world, output_node)
            parsed = True
    if parsed == False:
        solid_mat = rpdat.arm_material_model == 'Solid'
        if wrd.arm_irradiance and not solid_mat:
            wrd.world_defs += '_Irr'
        c = world.horizon_color
        world.arm_envtex_color = [c[0], c[1], c[2], 1.0]
        world.arm_envtex_strength = 1.0
    
    # Clear to color if no texture or sky is provided
    if '_EnvSky' not in wrd.world_defs and '_EnvTex' not in wrd.world_defs:
        if '_EnvImg' not in wrd.world_defs:
            wrd.world_defs += '_EnvCol'
        # Irradiance json file name
        world.arm_envtex_name = wname
        world.arm_envtex_irr_name = wname
        write_probes.write_color_irradiance(wname, world.arm_envtex_color)

    # film_transparent
    if bpy.context.scene != None and bpy.context.scene.cycles != None and bpy.context.scene.cycles.film_transparent:
        wrd.world_defs += '_EnvTransp'
        wrd.world_defs += '_EnvCol'

    # Clouds enabled
    if rpdat.arm_clouds:
        wrd.world_defs += '_EnvClouds'

    # Screen-space ray-traced shadows
    if rpdat.arm_ssrs:
        wrd.world_defs += '_SSRS'

    if wrd.arm_two_sided_area_lamp:
        wrd.world_defs += '_TwoSidedAreaLamp'

    # Store contexts
    if rpdat.rp_hdr == False:
        wrd.world_defs += '_LDR'

    # Alternative models
    if rpdat.arm_diffuse_model == 'OrenNayar':
        wrd.world_defs += '_OrenNayar'

    # TODO: Lamp texture test..
    if wrd.arm_lamp_texture != '':
        wrd.world_defs += '_LampColTex'

    if wrd.arm_lamp_ies_texture != '':
        wrd.world_defs += '_LampIES'
        assets.add_embedded_data('iestexture.png')

    if wrd.arm_lamp_clouds_texture != '':
        wrd.world_defs += '_LampClouds'
        assets.add_embedded_data('cloudstexture.png')

    voxelgi = False
    voxelao = False
    if rpdat.rp_renderer == 'Deferred':
        assets.add_khafile_def('arm_deferred')
    # Shadows
    if rpdat.rp_shadowmap_cascades != '1':
        wrd.world_defs += '_CSM'
        assets.add_khafile_def('arm_csm')
    if rpdat.rp_shadowmap == 'Off':
        wrd.world_defs += '_NoShadows'
        assets.add_khafile_def('arm_no_shadows')
    # GI
    has_voxels = state.in_viewport == False or bpy.app.version >= (2, 80, 1)
    if has_voxels:
        if rpdat.rp_gi == 'Voxel GI':
            voxelgi = True
        elif rpdat.rp_gi == 'Voxel AO':
            voxelao = True
    # SS
    # if rpdat.rp_dfrs:
    #     wrd.world_defs += '_DFRS'
    #     assets.add_khafile_def('arm_sdf')
    # if rpdat.rp_dfao:
    #     wrd.world_defs += '_DFAO'
    #     assets.add_khafile_def('arm_sdf')
    # if rpdat.rp_dfgi:
    #     wrd.world_defs += '_DFGI'
    #     assets.add_khafile_def('arm_sdf')
    #     wrd.world_defs += '_Rad' # Always do radiance for gi
    #     wrd.world_defs += '_Irr'
    if rpdat.rp_ssgi == 'RTGI' or rpdat.rp_ssgi == 'RTAO':
        if rpdat.rp_ssgi == 'RTGI':
            wrd.world_defs += '_RTGI'
        if wrd.arm_ssgi_rays == '9':
            wrd.world_defs += '_SSGICone9'
    if rpdat.rp_autoexposure:
        wrd.world_defs += '_AutoExposure'

    if voxelgi or voxelao:
        assets.add_khafile_def('arm_voxelgi')
        if rpdat.arm_voxelgi_revoxelize:
            assets.add_khafile_def('arm_voxelgi_revox')
            if rpdat.arm_voxelgi_camera:
                wrd.world_defs += '_VoxelGICam'
        wrd.world_defs += '_Rad' # Always do radiance for voxels
        wrd.world_defs += '_Irr'

    if voxelgi:
        wrd.world_defs += '_VoxelGI'
        if wrd.arm_voxelgi_diff_cones == '5':
            wrd.world_defs += '_VoxelGICone5'
        if rpdat.arm_voxelgi_shadows:
            wrd.world_defs += '_VoxelGIDirect'
            wrd.world_defs += '_VoxelGIShadow'
        if rpdat.arm_voxelgi_refraction:
            wrd.world_defs += '_VoxelGIDirect'
            wrd.world_defs += '_VoxelGIRefract'
        if rpdat.arm_voxelgi_emission:
            wrd.world_defs += '_VoxelGIEmission'
    elif voxelao:
        wrd.world_defs += '_VoxelAO'
        if wrd.arm_voxelgi_ao_cones == '9':
            wrd.world_defs += '_VoxelAOCone9'

    if arm.utils.get_gapi().startswith('direct3d'): # Flip Y axis in drawQuad command
        wrd.world_defs += '_InvY'

    # Area lamps
    for lamp in bpy.data.lamps:
        if lamp.type == 'AREA':
            wrd.world_defs += '_LTC'
            assets.add_khafile_def('arm_ltc')
            break

def parse_world_output(world, node):
    if node.inputs[0].is_linked:
        surface_node = node_utils.find_node_by_link(world.node_tree, node, node.inputs[0])
        parse_surface(world, surface_node)
    
def parse_surface(world, node):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    solid_mat = rpdat.arm_material_model == 'Solid'
    
    # Extract environment strength
    if node.type == 'BACKGROUND':
        
        # Append irradiance define
        if wrd.arm_irradiance and not solid_mat:
            wrd.world_defs += '_Irr'

        world.arm_envtex_color = node.inputs[0].default_value
        world.arm_envtex_strength = node.inputs[1].default_value

        # Strength
        if node.inputs[0].is_linked:
            color_node = node_utils.find_node_by_link(world.node_tree, node, node.inputs[0])
            parse_color(world, color_node)

def parse_color(world, node):       
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'

    # Env map included
    if node.type == 'TEX_ENVIRONMENT' and node.image != None:

        image = node.image
        filepath = image.filepath
        
        if image.packed_file == None and not os.path.isfile(arm.utils.asset_path(filepath)):
            log.warn(world.name + ' - unable to open ' + image.filepath)
            return

        # Reference image name
        tex_file = arm.utils.extract_filename(image.filepath)
        base = tex_file.rsplit('.', 1)
        ext = base[1].lower()

        if ext == 'hdr':
            target_format = 'HDR'
        else:
            target_format = 'JPEG'
        do_convert = ext != 'hdr' and ext != 'jpg'
        if do_convert:
            if ext == 'exr':
                tex_file = base[0] + '.hdr'
                target_format = 'HDR'
            else:
                tex_file = base[0] + '.jpg'
                target_format = 'JPEG'

        if image.packed_file != None:
            # Extract packed data
            unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + tex_file
            filepath = unpack_filepath

            if do_convert:
                if not os.path.isfile(unpack_filepath):
                    arm.utils.write_image(image, unpack_filepath, file_format=target_format)

            elif os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            
            assets.add(unpack_filepath)
        else:
            if do_convert:
                converted_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked/' + tex_file
                filepath = converted_path
                # TODO: delete cache when file changes
                if not os.path.isfile(converted_path):
                    arm.utils.write_image(image, converted_path, file_format=target_format)
                assets.add(converted_path)
            else:
                # Link image path to assets
                assets.add(arm.utils.asset_path(image.filepath))

        # Generate prefiltered envmaps
        world.arm_envtex_name = tex_file
        world.arm_envtex_irr_name = tex_file.rsplit('.', 1)[0]
        disable_hdr = target_format == 'JPEG'
        
        mip_count = world.arm_envtex_num_mips
        mip_count = write_probes.write_probes(filepath, disable_hdr, mip_count, arm_radiance=wrd.arm_radiance)
        
        world.arm_envtex_num_mips = mip_count
        
        # Append envtex define
        wrd.world_defs += '_EnvTex'
        # Append LDR define
        if disable_hdr:
            wrd.world_defs += '_EnvLDR'
        # Append radiance define
        if wrd.arm_irradiance and wrd.arm_radiance and not mobile_mat:
            wrd.world_defs += '_Rad'

    # Static image background
    elif node.type == 'TEX_IMAGE':        
        image = node.image
        filepath = image.filepath

        if image.packed_file != None:
            # Extract packed data
            filepath = arm.utils.build_dir() + '/compiled/Assets/unpacked'
            unpack_path = arm.utils.get_fp() + filepath
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + image.name
            if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            assets.add(unpack_filepath)
        else:
            # Link image path to assets
            assets.add(arm.utils.asset_path(image.filepath))

        # Reference image name
        tex_file = arm.utils.extract_filename(image.filepath)
        world.arm_envtex_name = tex_file

    # Append sky define
    elif node.type == 'TEX_SKY':
        # Match to cycles
        world.arm_envtex_strength *= 0.1
        
        wrd.world_defs += '_EnvSky'
        assets.add_khafile_def('arm_hosek')
                
        world.arm_envtex_sun_direction = [node.sun_direction[0], node.sun_direction[1], node.sun_direction[2]]
        world.arm_envtex_turbidity = node.turbidity
        world.arm_envtex_ground_albedo = node.ground_albedo
        
        # Irradiance json file name
        wname = arm.utils.safestr(world.name)
        world.arm_envtex_irr_name = wname
        write_probes.write_sky_irradiance(wname)

        # Radiance
        if wrd.arm_radiance_sky and wrd.arm_radiance and wrd.arm_irradiance and not mobile_mat:
            wrd.world_defs += '_Rad'
            hosek_path = 'armory/Assets/hosek/'
            sdk_path = arm.utils.get_sdk_path()
            # Use fake maps for now
            assets.add(sdk_path + hosek_path + 'hosek_radiance.hdr')
            for i in range(0, 8):
                assets.add(sdk_path + hosek_path + 'hosek_radiance_' + str(i) + '.hdr')
            
            world.arm_envtex_name = 'hosek'
            world.arm_envtex_num_mips = 8
