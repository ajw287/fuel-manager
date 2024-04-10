#from : https://stackoverflow.com/questions/38551168/radio-button-in-pygame#38625795
import pygame
pygame.font.init()

class Checkbox:
    """ Simple Checkbox class"""
    #TODO: FIXME: Not working yet - should be used to set the level of symmetry...
    def __init__(self, surface, x, y, idnum, color=(230, 230, 230), caption="test", outline_color=(0, 0, 0), check_color=(0, 0, 0), font_size=22,\
        font_color=(0, 0, 0), text_offset=(28, 1), font='Ariel Black', isChecked=False):
        self.surface = surface
        self.x = x
        self.y = y
        self.color = color
        self.caption = caption
        self.oc = outline_color
        self.cc = check_color
        self.fs = font_size
        self.fc = font_color
        self.to = text_offset
        self.font = font
        self.caption = caption

        #identification for removal and reorginazation
        self.idnum = idnum

        # checkbox object
        #self.font = pygame.font.SysFont(self.ft, self.fs)
        #self.font_surf = self.font.render(self.caption, True, self.fc)
        self.text = self.font.render(self.caption, 1, self.fc)
        self.rect = self.text.get_rect()
        self.surface.blit(self.text, self.text.get_rect(bottomleft = self.rect.topleft))

        w, h = self.font.size(self.caption)
        self.checkbox_obj = pygame.Rect(self.x + w + 24, self.y + 4, 12, 12)
        self.checkbox_outline = self.checkbox_obj.copy()
        # variables to test the different states of the checkbox
        self.checked = isChecked

    def _draw_button_text(self):
        self.text = self.font.render(self.caption, 1, (0, 5, 20))
        self.rect = self.text.get_rect()
        self.surface.blit(self.text, self.text.get_rect(bottomleft = self.rect.topleft))

        w, h = self.font.size(self.caption)
        self.font_pos = (self.x, self.y + 12 / 2 - h / 2 + self.to[1])
        self.surface.blit(self.text, self.text.get_rect(bottomleft = self.rect.topleft))
        #self.surface.blit(self.font_surf, self.font_pos)

    def render_checkbox(self):
        self._draw_button_text()
        if self.checked:
            pygame.draw.rect(self.surface, self.color, self.checkbox_obj)
            pygame.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
            w, h = self.font.size(self.caption)
            pygame.draw.circle(self.surface, self.cc, (self.x + w + 30, self.y + 10), 4)
        elif not self.checked:
            pygame.draw.rect(self.surface, self.color, self.checkbox_obj)
            pygame.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)

    def _update(self, event_object):
        x, y = pygame.mouse.get_pos()
        px, py, w, h = self.checkbox_obj
        if px < x < px + w and py < y < py + w:
            if self.checked:
                self.checked = False
            else:
                self.checked = True
            return True
        else:
            return False

    def update_checkbox(self, event_object):
        if event_object.type == pygame.MOUSEBUTTONDOWN:
            self.click = True
            return self._update(event_object)
