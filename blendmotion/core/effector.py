import bpy

def set_effector(object, weight=1.0):
    """
        obejct: Object(Mesh)
        weight: float
    """

    if object.type != 'MESH':
        raise OperatorError('Can\'t use {} as effector'.format(object.type))

    if weight < 0:
        raise OperatorError('Weight must be positive')

    object['blendmotion_effector'] = weight

