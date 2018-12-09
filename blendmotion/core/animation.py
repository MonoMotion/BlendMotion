import bpy
from mathutils import Euler

from blendmotion.logger import get_logger
from blendmotion.error import OperatorError
from blendmotion.core.effector import is_effector

import math
import json

def dictzip(d1, d2):
    for k, v in d1.items():
        yield k, (v, d2[k])

LOOP_TYPES = ('wrap', 'none')

def extract_bone_pose(bone):
    """
        bone: PoseBone
    """

    assert bone.rotation_mode == 'AXIS_ANGLE'
    return bone.rotation_axis_angle[0]

def get_decomposed_pose(obj):
    """
        obj: Object
    """

    local = obj.matrix_local.decompose()
    world = obj.matrix_world.decompose()
    return local, world


def extract_effector_pose(mesh):
    """
        mesh: Object(Mesh)
    """

    # Effector types stored in properties
    loc_effector = mesh.data.bm_location_effector
    rot_effector = mesh.data.bm_rotation_effector

    weight_loc = mesh.data.bm_location_effector_weight
    weight_rot = mesh.data.bm_rotation_effector_weight

    (local_loc, local_rot, _), (world_loc, world_rot, _) = get_decomposed_pose(mesh)

    def select_space(effector_type, world, local):
        # Select world or local value depends on effector type
        if effector_type == 'world':
            return world
        elif effector_type == 'local':
            return local
        elif effector_type == 'none':
            return None

    def compose_data(effector_type, world, local, weight):
        # Create data from effector type and values
        value = select_space(effector_type, world, local)
        if value is None:
            return None
        return { 'space': effector_type, 'weight': weight, 'value': list(value) }

    # Here, if effector_type is none, the value is set to None
    poses = {
        'location': compose_data(loc_effector, world_loc, local_loc, weight_loc),
        'rotation': compose_data(rot_effector, world_rot, local_rot, weight_rot),
    }

    # Let's filter out None
    return {k: v for k, v in poses.items() if v != None}

def get_frame_at(index, amt):
    """
        index: int
        amt: Object(Armature)
    """

    bpy.context.scene.frame_set(index)
    positions = {name: extract_bone_pose(b) for name, b in amt.pose.bones.items()}
    effectors = {obj.name: extract_effector_pose(obj) for obj in amt.children if is_effector(obj)}
    timepoint = index * (1 / bpy.context.scene.render.fps)
    return timepoint, positions, effectors


def export_animation(amt, path, loop_type='wrap'):
    if amt.type != 'ARMATURE':
        raise OperatorError('Armature object must be selected (selected: {})'.format(amt.type))

    assert loop_type in LOOP_TYPES

    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end

    bpy.ops.object.mode_set(mode='POSE')

    frames = [get_frame_at(i, amt) for i in range(start, end+1)]
    first_ts, _, _ = frames[0]

    output_data = {
        'model': amt.name,
        'loop': loop_type,
        'frames': [
            {
                'timepoint': t - first_ts,
                'position': p,
                'effector': e
            }
            for t, p, e in frames
        ]
    }

    with open(path, 'w') as f:
        json.dump(output_data, f, indent=2)

def timepoint_to_frame_index(timepoint):
    """
        timepoint: float
    """
    return int(timepoint * bpy.context.scene.render.fps)

def import_animation(amt, path):
    with open(path) as f:
        data = json.load(f)

    if amt.name != data['model']:
        raise OperatorError('Model name mismatch: {} and {}'.format(amt.name, data['model']))

    frames = data['frames']
    bpy.context.scene.frame_start = timepoint_to_frame_index(frames[0]['timepoint'])
    bpy.context.scene.frame_end = timepoint_to_frame_index(frames[-1]['timepoint'])

    for frame in frames:
        timepoint = frame['timepoint']
        positions = frame['position']
        effectors = frame['effector']

        bpy.context.scene.frame_set(timepoint_to_frame_index(timepoint))

        for _, (pos, bone) in dictzip(positions, amt.pose.bones):
            if 'blendmotion_joint' not in bone:
                continue

            assert bone.rotation_mode == 'AXIS_ANGLE'
            bone.rotation_axis_angle[0] = pos

            bone.keyframe_insert(data_path='rotation_axis_angle')

        for link_name, data in effectors.items():
            obj = next(c for c in amt.children if c.name == link_name)
            assert obj.type == 'MESH'

            def extract_data(data):
                return data['space'], data['weight']

            if 'rotation' in data:
                effector_type, weight = extract_data(data['rotation'])
                obj.data.bm_rotation_effector = effector_type
                obj.data.bm_rotation_effector_weight = weight

            if 'location' in data:
                effector_type, weight = extract_data(data['location'])
                obj.data.bm_location_effector = effector_type
                obj.data.bm_location_effector_weight = weight

def register():
    pass

def unregister():
    pass
