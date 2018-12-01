import bpy

from blendmotion.logger import get_logger
from .util import error_and_log

def make_armature(name):
    """
        name: str
    """
    bpy.ops.object.add(type='ARMATURE', enter_editmode=True)
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

def attach_parent(parent, child):
    """
        parent: EditBone
        child: EditBone
    """
    child.parent = parent

def make_bones_recursive(o, amt):
    """
        o: Object
        amt: Armature
    """
    get_logger().debug('make_bone_recursive: {}'.format(o.name))

    parent_bone = make_bone(o, amt)
    for child in o.children:
        if child.type != 'ARMATURE':
            continue

        child_bone = make_bones_recursive(child, amt)
        attach_parent(parent_bone, child_bone)

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

        amt = make_armature("Main")
        make_bones_recursive(obj, amt)
        return {'FINISHED'}
