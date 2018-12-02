from blendmotion.logger import get_logger

class OperatorError(Exception):
    def report(self, opr):
        opr.report({'ERROR'}, str(self))

    def log(self):
        get_logger().error(self)
