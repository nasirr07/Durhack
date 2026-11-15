import os
import unittest

import pygame

from screen_flow import ScreenController, ScreenState
from ui import PALETTE, PixelUI


class ScreenFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    @staticmethod
    def create_ui(size):
        assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets")
        )
        return PixelUI(size, assets_dir)

    def test_keyboard_navigation_and_start_action(self):
        controller = ScreenController()

        controller.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        )
        self.assertEqual(controller.selected_index, 1)

        controller.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        )
        action = controller.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        )
        self.assertEqual(action, "start")

    def test_end_screen_uses_restart_and_menu_actions(self):
        controller = ScreenController()
        controller.show_end_screen(victory=True)

        self.assertEqual(controller.state, ScreenState.END)
        self.assertEqual(controller.options, ("restart", "menu"))

        action = controller.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        )
        self.assertEqual(action, "restart")

    def test_mouse_selects_and_activates_end_screen_option(self):
        controller = ScreenController()
        controller.show_end_screen(victory=False)
        controller.set_option_rects(
            (pygame.Rect(0, 0, 40, 20), pygame.Rect(50, 0, 40, 20))
        )

        controller.handle_event(
            pygame.event.Event(pygame.MOUSEMOTION, pos=(60, 10))
        )
        action = controller.handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                button=1,
                pos=(60, 10),
            )
        )

        self.assertEqual(controller.selected_index, 1)
        self.assertEqual(action, "menu")

    def test_start_and_end_options_stack_vertically_at_responsive_width(self):
        ui = self.create_ui((800, 600))
        buttons = ui._button_rects(240)

        self.assertEqual(buttons[0].centerx, buttons[1].centerx)
        self.assertGreater(buttons[1].top, buttons[0].bottom)

        wide_ui = self.create_ui((1920, 1080))
        wide_buttons = wide_ui._button_rects(400)
        for button in wide_buttons:
            self.assertGreaterEqual(button.left, 0)
            self.assertLessEqual(button.right, 1920)

    def test_selected_marker_has_reserved_space_left_of_button_text(self):
        ui = self.create_ui((800, 600))
        button = ui._button_rects(240)[0]
        marker = ui._selection_marker_rect(button)
        text = ui._button_text_rect(button, "Return to menu")

        self.assertLess(marker.right, text.left)
        self.assertEqual(text.center, button.center)
        self.assertLessEqual(button.height, 36 * ui.scale)

    def test_start_render_restores_dimming_and_individual_option_boxes(self):
        ui = self.create_ui((800, 600))
        screen = pygame.Surface((800, 600))
        background = pygame.Surface((800, 460))
        floor = pygame.Surface((800, 140))
        background.fill((180, 180, 180))
        floor.fill((180, 180, 180))

        buttons = ui.draw_start(screen, background, floor, 0)

        self.assertNotEqual(screen.get_at((0, 0))[:3], (180, 180, 180))
        self.assertEqual(
            screen.get_at(buttons[0].center)[:3],
            PALETTE["panel_light"],
        )


if __name__ == "__main__":
    unittest.main()
