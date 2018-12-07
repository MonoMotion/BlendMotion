import bpy
from mathutils import Euler

from blendmotion.logger import get_logger
from blendmotion.error import OperatorError

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

    euler = bone.rotation_quaternion.to_euler('XYZ')
    axis = bone['blendmotion_axis']

    if sum(1 for e in euler if not math.isclose(e, 0, abs_tol=1e-5)) > 1:
        get_logger().warning('joint "{}" has out-of-bound position {}'.format(bone.name, tuple(euler)))

    if axis == 'x':
        return euler.x
    elif axis == 'y':
        return euler.y
    elif axis == 'z':
        return euler.z

def extract_effector_pose(mesh):
    """
        mesh: Object(Mesh)
    """

    assert 'blendmotion_effector' in mesh

    location = mesh.location
    rotation = mesh.rotation_quaternion

    return { 'location': location, 'rotation': rotation }

def get_frame_at(index, amt):
    """
        index: int
        amt: Object(Armature)
    """

    bpy.context.scene.frame_set(index)
    positions = {name: extract_bone_pose(b) for name, b in amt.pose.bones.items() if 'blendmotion_axis' in b}
    effectors = {name: extract_effector_pose(mesh) for name, mesh in amt.children.items() if 'blendmotion_effector' in mesh}
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
    first_ts, _ = frames[0]

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

        bpy.context.scene.frame_set(timepoint_to_frame_index(timepoint))

        for _, (pos, bone) in dictzip(positions, amt.pose.bones):
            if 'blendmotion_joint' not in bone:
                continue

            if 'blendmotion_axis' not in bone:
                get_logger().warning('no axis available for {}, skipping'.format(bone.name))
                continue

            axis = bone['blendmotion_axis']
            if axis == 'x':
                euler = (pos, 0, 0)
            elif axis == 'y':
                euler = (0, pos, 0)
            elif axis == 'z':
                euler = (0, 0, pos)

            bone.rotation_quaternion = Euler(euler, 'XYZ').to_quaternion()
            bone.keyframe_insert(data_path='rotation_quaternion')
