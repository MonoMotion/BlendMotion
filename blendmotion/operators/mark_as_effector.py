import bpy
from blendmotion.core.effector import mark_as_effector, unmark_as_effector
from blendmotion.error import OperatorError, error_and_log

class MarkAsEffectorOperator(bpy.types.Operator):
    bl_idname = "bm.mark_as_effector"
    bl_label = "Mark as an effector"

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            mark_as_effector(obj)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

class UnmarkAsEffectorOperator(bpy.types.Operator):
    bl_idname = "bm.unmark_as_effector"
    bl_label = "Delete the mark of an effector"

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            unmark_as_effector(obj)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    bpy.utils.register_class(MarkAsEffectorOperator)
    bpy.utils.register_class(UnmarkAsEffectorOperator)

def unregister():
    bpy.utils.unregister_class(UnmarkAsEffectorOperator)
    bpy.utils.unregister_class(MarkAsEffectorOperator)
