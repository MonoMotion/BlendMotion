import bpy

from blendmotion.logger import get_logger
from blendmotion.error import OperatorError

import math
import json

def dictzip(d1, d2):
    for k, v in d1:
        yield k, (v, d2[k])

LOOP_TYPES = ('wrap', 'none')

def extract_pose(bone):
    """
        bone: PoseBone
    """

    euler = bone.matrix.to_euler('XYZ')

    if sum(1 for e in euler if not math.isclose(e, 0, abs_tol=1e-5)) != 1:
        get_logger().warning('joint "{}" has out-of-bound position {}'.format(bone.name, tuple(euler)))

    return max(euler, key=abs)

def get_frame_at(index, amt):
    """
        index: int
        amt: Object(Armature)
    """

    bpy.context.scene.frame_set(index)
    positions = {name: extract_pose(b) for name, b in amt.pose.bones.items() if 'blendmotion_joint' in b}
    timepoint = index * (1 / bpy.context.scene.render.fps)
    return timepoint, positions


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
                'position': p
            }
            for t, p in frames
        ]
    }

    with open(path, 'w') as f:
        json.dump(output_data, f, indent=2)

def import_animation(amt, path):
    with open(path) as f:
        data = json.load(f)

    if amt.name != data['model']:
        raise OperatorError('Model name mismatch: {} and {}'.format(amt.name, data['model']))

    for frame in data['frames']:
        timepoint = data['timepoint']
        positions = data['position']

        bpy.context.scene.frame_set(int(timepoint * bpy.context.scene.render.fps))

        for _, (bone, pos) in dictzip(positions, amt.pose.bones):
            if 'blendmotion_joint' not in bone:
                continue

            assert 'blendmotion_axis' in bone

            axis = bone['blendmotion_axis']
            if axis == 'x':
                euler = (pos, 0, 0)
            elif axis == 'y':
                euler = (0, pos, 0)
            elif axis == 'z':
                euler = (0, 0, pos)

            bone.rotation_quaternion = Euler(euler, 'XYZ').to_quaternion()
