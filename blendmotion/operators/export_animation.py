import bpy
from blendmotion.core import export_animation

class ExportAnimationOperator(bpy.types.Operator):
    bl_idname = "bm.export_animation"
    bl_label = "Export animation"

    def execute(self, context):
        export_animation()
        return {'FINISHED'}

