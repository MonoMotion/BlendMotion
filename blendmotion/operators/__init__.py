import bpy

from .add_bones import AddBonesOperator, SelectAndAddBonesOperator

def menu_func(self, context):
    self.layout.separator()
    o1 = self.layout.operator(AddBonesOperator.bl_idname, icon='GROUP_BONE', text=AddBonesOperator.bl_label)
    o1.with_ik = False
    o2 = self.layout.operator(AddBonesOperator.bl_idname, icon='CONSTRAINT_BONE', text=AddBonesOperator.bl_label + " (with IK)")
    o2.with_ik = True

def register():
    bpy.types.INFO_MT_armature_add.append(menu_func)
    bpy.utils.register_class(SelectAndAddBonesOperator)
    bpy.utils.register_class(AddBonesOperator)

def unregister():
    bpy.types.INFO_MT_armature_add.remove(menu_func)
    bpy.utils.unregister_class(SelectAndAddBonesOperator)
    bpy.utils.unregister_class(AddBonesOperator)
