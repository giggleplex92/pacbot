from pygame._freetype import Font, init as init_font
from vector import Vector
from constants import *

init_font()


class Text(object):
    """
    This class represents text on the screen. It can have various properties, but the
    font will remain consistent across all instances.
    """

    def __init__(self, text, color, x, y, size, time=None, text_id=None, visible=True):
        self.font = None
        self.id = text_id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setup_font("PressStart2P-Regular.ttf")
        self.create_label()

    def setup_font(self, font_path):
        self.font = Font(font_path, self.size)

    def create_label(self):
        self.label, _ = self.font.render(self.text, self.color)

    def set_text(self, new_text):
        self.text = str(new_text)
        self.create_label()

    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen):
        if self.visible:
            x, y = self.position.as_tuple()
            screen.blit(self.label, (x, y))


class TextGroup(object):
    def __init__(self):
        self.nextid = 10
        self.all_text = {}
        self.setup_text()
        self.show_text(READYTXT)

    def add_text(self, text, color, x, y, size, time=None, text_id=None):
        self.nextid += 1
        self.all_text[self.nextid] = Text(text, color, x, y, size, time=time, text_id=text_id)
        return self.nextid

    def remove_text(self, text_id):
        self.all_text.pop(text_id)

    def setup_text(self):
        size = TILEHEIGHT
        self.all_text[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.all_text[HIGHSCORETXT] = Text("0".zfill(8), WHITE, 11 * TILEWIDTH, TILEHEIGHT, size)
        self.all_text[LEVELTXT] = Text(str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, size)
        self.all_text[READYTXT] = Text("READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.all_text[PAUSETXT] = Text("PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.all_text[GAMEOVERTXT] = Text("GAME OVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)

        self.add_text("SCORE", WHITE, 0, 0, size)
        self.add_text("HIGH SCORE", WHITE, 9 * TILEWIDTH, 0, size)
        self.add_text("LEVEL", WHITE, 23 * TILEWIDTH, 0, size)

    def update(self, dt):
        for text_key in list(self.all_text.keys()):
            self.all_text[text_key].update(dt)
            if self.all_text[text_key].destroy:
                self.remove_text(text_key)

    def show_text(self, text_id):
        self.hide_text()
        self.all_text[text_id].visible = True

    def hide_text(self):
        self.all_text[READYTXT].visible = False
        self.all_text[PAUSETXT].visible = False
        self.all_text[GAMEOVERTXT].visible = False

    def update_score(self, score):
        self.update_text(SCORETXT, str(score).zfill(8))

    def update_high_score(self, score):
        self.update_text(HIGHSCORETXT, str(score).zfill(8))

    def update_level(self, level):
        self.update_text(LEVELTXT, str(level + 1).zfill(3))

    def update_text(self, text_id, value):
        if text_id in self.all_text.keys():
            self.all_text[text_id].set_text(value)

    def render(self, screen):
        for text_key in list(self.all_text.keys()):
            self.all_text[text_key].render(screen)