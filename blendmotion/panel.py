import bpy
from blendmotion.core.animation import LOOP_TYPES
from blendmotion.operators.export_animation import ExportAnimationOperator
from blendmotion.operators.import_animation import ImportAnimationOperator

class ExportAnimationProps(bpy.types.PropertyGroup):
    loop_type = bpy.props.EnumProperty(name='Loop Type', description='Whether the animation is looped', items=[(t, t, t) for t in LOOP_TYPES])

class ExportAnimationPanel(bpy.types.Panel):
    bl_idname = 'bm.panel.export_animation'
    bl_label = 'Export'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BlendMotion"


    def draw(self, context):
        props = context.scene.export_animation_props

        self.layout.prop(props, 'loop_type')
        self.layout.operator(ExportAnimationOperator.bl_idname, icon='EXPORT').loop_type = props.loop_type

class ImportAnimationPanel(bpy.types.Panel):
    bl_idname = 'bm.panel.import_animation'
    bl_label = 'Import'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BlendMotion"


    def draw(self, context):
        self.layout.operator(ImportAnimationOperator.bl_idname, icon='IMPORT')

def register():
    bpy.utils.register_class(ExportAnimationPanel)
    bpy.utils.register_class(ImportAnimationPanel)
    bpy.utils.register_class(ExportAnimationProps)
    bpy.types.Scene.export_animation_props = bpy.props.PointerProperty(type=ExportAnimationProps)

def unregister():
    bpy.utils.unregister_class(ExportAnimationProps)
    bpy.utils.unregister_class(ImportAnimationPanel)
    bpy.utils.unregister_class(ExportAnimationPanel)
