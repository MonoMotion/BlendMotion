import bpy

from blendmotion.logger import get_logger
from blendmotion.error import OperatorError

import math
import json

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

    frames = (get_frame_at(i, amt) for i in range(start, end+1))

    output_data = {
        'model': amt.name,
        'loop': loop_type,
        'frames': [
            {
                'timepoint': t,
                'position': p
            }
            for t, p in frames
        ]
    }

    with open(path, 'w') as f:
        json.dump(output_data, f, indent=2)
