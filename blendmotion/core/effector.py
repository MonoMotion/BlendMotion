import bpy
from blendmotion.error import OperatorError

EFFECTOR_TYPES = ('rotation', 'location', 'none')

def mark_as_effector(object, weight=1.0):
    """
        obejct: Object(Mesh)
        weight: float
    """

    if object.type != 'MESH':
        raise OperatorError('Can\'t use {} as effector'.format(object.type))

    if weight < 0:
        raise OperatorError('Weight must be positive')

    object['blendmotion_effector'] = weight

def unmark_as_effector(object):
    """
        obejct: Object(Mesh)
    """

    if object.type != 'MESH':
        raise OperatorError('Can\'t use {} as effector'.format(object.type))

    del object['blendmotion_effector']

def register():
    effector_types_enum = [(t, t, t) for t in EFFECTOR_TYPES]
    bpy.types.Mesh.bm_rotation_effector = bpy.props.EnumProperty(items=effector_types_enum, default='none')
    bpy.types.Mesh.bm_rotation_effector_weight = bpy.props.FloatProperty(min=0.0, max=1.0, default=1.0)
    bpy.types.Mesh.bm_location_effector = bpy.props.EnumProperty(items=effector_types_enum, default='none')
    bpy.types.Mesh.bm_location_effector_weight = bpy.props.FloatProperty(min=0.0, max=1.0, default=1.0)

def unregister():
    pass
