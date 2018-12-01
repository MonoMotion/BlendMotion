from blendmotion.logger import get_logger

def error_and_log(opr, message):
    get_logger().error(message)
    opr.report({'ERROR'}, message)
    return {'CANCELLED'}
