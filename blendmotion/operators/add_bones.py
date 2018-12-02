import bpy
from mathutils import Euler

from blendmotion.logger import get_logger
from .util import error_and_log

import math

def make_armature(name, location):
    """
        name: str
    """
    bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=location)
    amt = bpy.context.object
    amt.name = name
    return amt

def calc_pos(o):
    """
        o: Object
    """
    return o.data.bones[0].head + o.matrix_world.translation

def make_bone(o, amt):
    """
        o: Object
        amt: Armature
    """
    get_logger().debug('make_bone: {}'.format(o.name))

    parent_name = o.parent.name if o.parent is not None else 'root'
    b = amt.data.edit_bones.new('{}_{}'.format(parent_name, o.name))
    if o.parent is not None:
        b.head = calc_pos(o.parent)
    b.tail = calc_pos(o)
    b['blendmotion_joint'] = parent_name

    return b

def attach_bones(parent, child):
    """
        parent: EditBone
        child: EditBone
    """
    child.parent = parent

def attach_mesh_bone(o, amt, bone):
    """
        o: Object
        amt: Armature
        bone: EditBone
    """
    # TODO: Take bone as Bone, not EditBone

    o.parent = amt
    o.parent_type = 'BONE'
    o.parent_bone = bone.name

def attach_mesh_armature(o, amt):
    """
        o: Object
        amt: Armature
    """
    o.parent = amt
    o.parent_type = 'OBJECT'

def make_tip(bone, amt):
    """
        bone: EditBone
        amt: Armature
    """
    # TODO: Take bone as Bone, not EditBone

    get_logger().debug('make_tip: {}'.format(bone.name))

    # make a bone which has the same shape with parent bone
    b = amt.data.edit_bones.new('tip_{}'.format(bone.name))
    b.head = bone.tail
    b.tail = b.head + bone.vector

    handle = amt.data.edit_bones.new('handle_{}'.format(bone.name))
    handle.head = b.tail
    v = b.vector.copy()
    v.rotate(Euler((0.0, - math.pi / 2, 0.0), 'XYZ'))
    handle.tail = handle.head + v

    return b, handle

def set_ik(bone_name, target_armature, target_bone_name):
    """
        bone: str
        target_armature: Armature
        target_bone_name: str
    """

    bone = target_armature.pose.bones[bone_name]
    ik = bone.constraints.new(type='IK')
    name = ik.name
    bone.constraints[name].target = target_armature
    bone.constraints[name].subtarget = target_bone_name

def limit_bone(bone_name, joint_name, amt):
    """
        bone_name: str
        joint_name: str
        amt: Armature
    """

    bone = amt.pose.bones[bone_name]
    joint = bpy.data.objects[joint_name]
    joint_type = joint.get('joint/type')

    limit_x = (0, 0)
    limit_y = (0, 0)
    limit_z = (0, 0)
    if joint_type is None or joint_type == 'fixed':
        pass
    elif joint_type == 'revolute':
        # Make sure the joint is phobos' joint
        assert len(joint.pose.bones) == 1
        joint_constraint = joint.pose.bones[0].constraints['Limit Rotation']

        # Make sure limit is only applied to Y axis
        assert joint_constraint.use_limit_x
        assert joint_constraint.use_limit_y
        assert joint_constraint.use_limit_z
        assert joint_constraint.min_x == 0 and joint_constraint.max_x == 0
        assert joint_constraint.min_z == 0 and joint_constraint.max_z == 0

        # So Y axis represents joint limits
        joint_limit = (joint_constraint.min_y, joint_constraint.max_y)

        bone_vector = bone.vector.copy()
        joint_vector = joint.pose.bones[0].vector
        diff = bone_vector.rotation_difference(joint_vector).to_euler('XYZ')
        x, y, z = tuple(int(i) for i in diff)
        if x != 0:
            limit_z = joint_limit
        elif y != 0:
            limit_x = joint_limit
        elif z != 0:
            limit_y = joint_limit
    elif joint_type == 'floating':
        limit_x = (-math.pi, math.pi)
        limit_y = (-math.pi, math.pi)
        limit_z = (-math.pi, math.pi)
    else:
        raise NotImplementedError('joint/type: {}'.format(joint_type))

    # IK Constraints
    bone.use_ik_limit_x = True
    bone.use_ik_limit_y = True
    bone.use_ik_limit_z = True
    bone.ik_min_x, bone.ik_max_x = limit_x
    bone.ik_min_y, bone.ik_max_y = limit_y
    bone.ik_min_z, bone.ik_max_z = limit_z

    # Bone Constraints
    # TODO: Enable bone constraints
    # Currently, this code causes broken form in Object mode and Pose mode
    # limit = bone.constraints.new(type='LIMIT_ROTATION')
    # limit.use_limit_x = True
    # limit.use_limit_y = True
    # limit.use_limit_z = True
    # limit.min_x, limit.max_x = limit_x
    # limit.min_y, limit.max_y = limit_y
    # limit.min_z, limit.max_z = limit_z

def make_bones_recursive(o, amt):
    """
        o: Object
        amt: Armature
    """
    get_logger().debug('make_bone_recursive: {}'.format(o.name))

    parent_bone = make_bone(o, amt)

    armature_children = [child for child in o.children if child.type == 'ARMATURE']
    mesh_children = [child for child in o.children if child.type == 'MESH']

    if len(armature_children) == 1:
        # Single bone
        child_bone = make_bones_recursive(armature_children[0], amt)
        attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_bone(child, amt, child_bone)
    elif len(armature_children) == 0:
        # The tip
        child_bone, handle_bone = make_tip(parent_bone, amt)
        attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_bone(child, amt, child_bone)

        # Mark a tip bone to use them later
        child_bone['blendmotion_joint'] = o.name
        child_bone['blendmotion_tip'] = handle_bone.name
    else:
        # Where bones are branching off
        for child in armature_children:
            child_bone = make_bones_recursive(child, amt)
            attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_armature(child, amt)

    return parent_bone

class AddBonesOperator(bpy.types.Operator):
    bl_idname = "mesh.addbmbones"
    bl_label  = "Kinematic Bones on Phobos model"
    bl_description = "Add kinematic bones on phobos model from selected mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        if obj.type != 'ARMATURE':
            return error_and_log(self, 'Armature object must be selected (currently selected: {})'.format(obj.type))

        model_name = obj.get('model/name')
        if model_name is None:
            return error_and_log(self, '"model/name" property not set. base link of phobos model must be selected.')

        bpy.ops.object.mode_set(mode='OBJECT')

        # collision meshes and intertia meshes are visible here
        bpy.context.scene.layers[:4] = [False, True, False, True]
        # Delete visible things (= collision and inertia)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # visual meshes and joints are visible
        bpy.context.scene.layers[:4] = [True, False, True, False]

        # Apply transforms
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.select_all(action='DESELECT')

        amt = make_armature(model_name, obj.matrix_world.translation)

        bpy.ops.object.mode_set(mode='EDIT')
        make_bones_recursive(obj, amt)

        # TODO: Do this in attach_mesh_bone
        bpy.ops.object.mode_set(mode='OBJECT')
        for o in amt.children:
            if o.type == 'MESH':
                o.matrix_world = o.matrix_parent_inverse

        bpy.ops.object.mode_set(mode='EDIT')

        bone_and_joints = [(name, b['blendmotion_joint']) for name, b in amt.data.bones.items() if 'blendmotion_joint' in b]
        tip_bones = [(name, b['blendmotion_tip']) for name, b in amt.data.bones.items() if 'blendmotion_tip' in b]

        bpy.ops.object.mode_set(mode='POSE')

        # Find tip bones and apply IK constraint on it
        for bone_name, handle_bone_name in tip_bones:
            set_ik(bone_name, amt, handle_bone_name)

        # Find joint bones and apply joint limits on it
        for bone_name, joint_name in bone_and_joints:
            limit_bone(bone_name, joint_name, amt)

        bpy.ops.object.mode_set(mode='OBJECT')

        # Joints are visible
        bpy.context.scene.layers[:5] = [True, False, False, False, False]
        # Delete joints
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # All layers are visible
        bpy.context.scene.layers[:5] = [True] * 5

        return {'FINISHED'}
