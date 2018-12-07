import bpy

from . import add_bones, export_animation, import_animation, mark_as_effector


def register():
    add_bones.register()
    export_animation.register()
    import_animation.register()
    mark_as_effector.register()

def unregister():
    add_bones.unregister()
    export_animation.unregister()
    import_animation.unregister()
    mark_as_effector.unregister()
