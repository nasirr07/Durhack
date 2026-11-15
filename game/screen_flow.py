from enum import Enum

import pygame


class ScreenState(Enum):
    START = "start"
    GAMEPLAY = "gameplay"
    END = "end"


class ScreenController:
    def __init__(self):
        self.state = ScreenState.START
        self.victory = False
        self.selected_index = 0
        self.option_rects = ()

    @property
    def options(self):
        if self.state == ScreenState.END:
            return ("restart", "menu")
        return ("start", "quit")

    @property
    def gameplay_active(self):
        return self.state == ScreenState.GAMEPLAY

    def set_option_rects(self, rects):
        self.option_rects = tuple(rects)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index]
            elif event.key == pygame.K_ESCAPE:
                return "quit" if self.state == ScreenState.START else "menu"

        if event.type == pygame.MOUSEMOTION:
            self._select_from_mouse(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._select_from_mouse(event.pos)
            if index is not None:
                return self.options[index]

        return None

    def show_end_screen(self, victory):
        self.victory = victory
        self.state = ScreenState.END
        self.selected_index = 0
        self.option_rects = ()

    def show_start_screen(self):
        self.state = ScreenState.START
        self.selected_index = 0
        self.option_rects = ()

    def _select_from_mouse(self, position):
        for index, rect in enumerate(self.option_rects):
            if rect.collidepoint(position):
                self.selected_index = index
                return index
        return None
