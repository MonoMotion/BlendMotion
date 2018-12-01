import bpy

from .operators import AddBonesOperator

bl_info = {
    "name": "blendmotion",
    "author": "coord.e <me@coord-e.com>",
    "version": (0, 1),
    "blender": (2, 7, 9),
    "location": "somewhere",
    "description": "convert animation to robot motion",
    "warning": "You may need phobos plugin to be installed on your system",
    "wiki_url": "https://github.com/DeepL2/blendmotion/wiki",
    "tracker_url": "https://github.com/DeepL2/blendmotion/issues",
    "category": "Development",
}

def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(AddBonesOperator.bl_idname)

def register():
    bpy.utils.register_class(AddBonesOperator)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(AddBonesOperator)
