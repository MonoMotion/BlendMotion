import bpy

from blendmotion.core import add_bones
from blendmotion.error import OperatorError, error_and_log

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

        try:
            add_bones(obj)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}
