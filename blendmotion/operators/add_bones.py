import bpy

from blendmotion.logger import get_logger
from .util import error_and_log

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

    b = amt.data.edit_bones.new('{}_{}'.format(o.parent.name if o.parent is not None else 'root', o.name))
    if o.parent is not None:
        b.head = calc_pos(o.parent)
    b.tail = calc_pos(o)

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
        child_bone = make_bones_recursive(armature_children[0], amt)
        attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_bone(child, amt, child_bone)
    else:
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

        amt = make_armature("Main", obj.matrix_world.translation)
        make_bones_recursive(obj, amt)

        # TODO: Do this in attach_mesh_bone
        bpy.ops.object.mode_set(mode='OBJECT')
        for o in amt.children:
            if o.type == 'MESH':
                o.matrix_world = o.matrix_parent_inverse

        return {'FINISHED'}
