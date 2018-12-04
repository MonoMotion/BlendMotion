import bpy
from blendmotion.logger import get_logger
import math

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


def export_animation(amt):
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end

    bpy.ops.object.mode_set(mode='POSE')

    frames = (get_frame_at(i, amt) for i in range(start, end+1))

    output_data = {
        'model': amt.name,
        'loop': 'wrap',
        'frames': [
            {
                'timepoint': t,
                'position': p
            }
            for t, p in frames
        ]
    }

    get_logger().debug(output_data)
