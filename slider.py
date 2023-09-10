from setting import *
import pygame
pygame.init()

KNOB_COLOR = '#3b3b3b'
RAIL_COLOR = '#737373'
BORDER_COLOR = '#ffffff'

class Slider:
    def __init__(self, window, lower_bound, upper_bound, slider_center, rail_length, rail_height, knob_length, knob_height, border_size):
        self.window = window
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.slider_center = slider_center
        self.rail_length = rail_length
        self.rail_height = rail_height
        self.knob_length = knob_length
        self.knob_height = knob_height
        self.border_size = border_size

        self.rail = pygame.Rect(self.slider_center[0] - self.rail_length / 2, 
                                self.slider_center[1] - self.rail_height / 2, 
                                self.rail_length, 
                                self.rail_height)
        
        self.rail_bg = pygame.Rect(self.slider_center[0] - self.rail_length / 2 - self.border_size, 
                                   self.slider_center[1] - self.rail_height / 2 - self.border_size, 
                                   self.rail_length + 2 * self.border_size, 
                                   self.rail_height + 2 * self.border_size)
        
        self.knob = pygame.Rect(self.slider_center[0] - self.knob_length / 2, 
                                self.slider_center[1] - self.knob_height / 2, 
                                self.knob_length, 
                                self.knob_height)
        
        self.knob_bg = pygame.Rect(self.slider_center[0] - self.knob_length / 2 - self.border_size, 
                                   self.slider_center[1] - self.knob_height / 2 - self.border_size, 
                                   self.knob_length + 2 * self.border_size, 
                                   self.knob_height + 2 * self.border_size)
        
        self.dragging = False
        self.original_x = None

    def onKnob(self, mouse):
        if self.knob.collidepoint(mouse):
            self.original_x = mouse[0]
            return True
        return False
    
    def drag(self, mouse_x):
        displacement = mouse_x - self.original_x
        knobPos = self.knob.x + displacement
        if knobPos < self.rail.x:
            knobPos = self.rail.x
        elif knobPos > self.rail.x + self.rail.width - self.knob_length:
            knobPos = self.rail.x + self.rail.width - self.knob_length
        self.knob.update((knobPos, self.knob.y), (self.knob_length, self.knob_height))
        self.knob_bg.update((knobPos - self.border_size, self.knob.y - self.border_size), (self.knob_length + 2 * self.border_size, self.knob_height + 2 * self.border_size))
        self.original_x = self.knob.x + self.knob_length / 2

    def getValue(self): 
        return round((self.knob.centerx - self.rail.x - self.knob_length / 2) / (self.rail.width - self.knob.width) * (self.upper_bound - self.lower_bound)) + self.lower_bound

    def draw(self):
        pygame.draw.rect(self.window, BORDER_COLOR, self.rail_bg)
        pygame.draw.rect(self.window, RAIL_COLOR, self.rail)
        pygame.draw.rect(self.window, BORDER_COLOR, self.knob_bg)
        pygame.draw.rect(self.window, KNOB_COLOR, self.knob)