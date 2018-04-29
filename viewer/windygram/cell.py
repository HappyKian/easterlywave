
class Cell:

    def __init__(self, x=0, y=0, width=0.125, height=0.125, span=1):
        self.x = x
        self.y = y
        self.height = height
        self.width = width * span
        self.span = span
        self.text = None
        self.bgcolor = None
        self.alpha = 1

    def set_text(self, text):
        self.text = text

    def set_bgcolor(self, color):
        self.bgcolor = color

    def set_alpha(self, alpha):
        self.alpha = alpha

    def set_theta(self, theta):
        self.theta = theta

    def set_code(self, code):
        self.code = code

    def set_time(self, time):
        self.time = time

    def copy(self):
        new = Cell()
        new.__dict__ = self.__dict__.copy()
        return new

class CellRow:

    def __init__(self, x=0, y=0, height=0, width=0, name=None):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.name = name
        self.cells = []
        self.cellx = x

    def add_cell(self, cell):
        cell.x = self.cellx
        cell.y = self.y
        cell.height = self.height
        cell.width = self.width * cell.span
        self.cellx += cell.width
        self.cells.append(cell)
