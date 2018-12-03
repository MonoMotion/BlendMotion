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

def export_animation(amt):
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end

    bpy.ops.object.mode_set(mode='POSE')
    for i in range(start, end + 1):
        bpy.context.scene.frame_set(i)
        get_logger().debug({name: extract_pose(b) for name, b in amt.pose.bones.items()})

    bpy.context.scene.frame_set(start)
