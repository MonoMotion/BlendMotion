import bpy
from blendmotion.core import export_animation
from blendmotion.error import error_and_log

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
    bl_label = "Export Animation"

    filepath = bpy.props.StringProperty(name='file_path', subtype='FILE_PATH')

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            export_animation(obj, self.filepath)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
