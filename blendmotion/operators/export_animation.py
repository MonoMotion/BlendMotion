import bpy
from blendmotion.core import export_animation

class ExportAnimationPanel(bpy.types.Panel):
    bl_idname = 'bm.panel.export_animation'
    bl_label = 'BlendMotion Animation Export'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        self.layout.operator(ExportAnimationOperator.bl_idname)

class ExportAnimationOperator(bpy.types.Operator):
    bl_idname = "bm.export_animation"
    bl_label = "Export animation"

    def execute(self, context):
        obj = context.selected_objects[0]
        export_animation(obj)
        return {'FINISHED'}

