import bpy
from blendmotion.core import export_animation
from blendmotion.core.export_animation import LOOP_TYPES
from blendmotion.error import error_and_log

class ExportAnimationProps(bpy.types.PropertyGroup):
    loop_type = bpy.props.EnumProperty(name='Loop Type', description='Whether the animation is looped', items=[(t, t, t) for t in LOOP_TYPES])

class ExportAnimationPanel(bpy.types.Panel):
    bl_idname = 'bm.panel.export_animation'
    bl_label = 'BlendMotion Animation Export'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'


    def draw(self, context):
        props = context.scene.export_animation_props
        self.layout.prop(props, 'loop_type')
        opr = self.layout.operator(ExportAnimationOperator.bl_idname)
        opr.loop_type = props.loop_type

class ExportAnimationOperator(bpy.types.Operator):
    bl_idname = "bm.export_animation"
    bl_label = "Export Animation"

    filepath = bpy.props.StringProperty(name='file_path', subtype='FILE_PATH')
    loop_type = bpy.props.EnumProperty(name='loop_type', items=[(t, t, t) for t in LOOP_TYPES])

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            export_animation(obj, self.filepath, self.loop_type)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
