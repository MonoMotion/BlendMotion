import bpy
from blendmotion.error import OperatorError

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
