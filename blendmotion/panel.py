import bpy
from blendmotion.core.animation import LOOP_TYPES
from blendmotion.operators.export_animation import ExportAnimationOperator
from blendmotion.operators.import_animation import ImportAnimationOperator

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

        row_export = self.layout.row()
        box = row_export.box()
        box.prop(props, 'loop_type')
        box.operator(ExportAnimationOperator.bl_idname, icon='EXPORT').loop_type = props.loop_type

        row_import = self.layout.row()
        box = row_import.box()
        box.operator(ImportAnimationOperator.bl_idname, icon='IMPORT')

def register():
    bpy.utils.register_class(ExportAnimationPanel)
    bpy.utils.register_class(ExportAnimationProps)
    bpy.types.Scene.export_animation_props = bpy.props.PointerProperty(type=ExportAnimationProps)

def unregister():
    bpy.utils.unregister_class(ExportAnimationProps)
    bpy.utils.unregister_class(ExportAnimationPanel)
