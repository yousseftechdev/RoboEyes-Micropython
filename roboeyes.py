import time
import random

# Constants (translated from the macros)
BGCOLOR = 0      # background and overlays
MAINCOLOR = 1    # drawings

# Mood types
DEFAULT = 0
TIRED   = 1
ANGRY   = 2
HAPPY   = 3

# On/off states
ON  = 1
OFF = 0

# Predefined positions (for left eye positioning; right eye follows)
N  = 1   # north, top center
NE = 2   # north-east, top right
E  = 3   # east, middle right
SE = 4   # south-east, bottom right
S  = 5   # south, bottom center
SW = 6   # south-west, bottom left
W  = 7   # west, middle left
NW = 8   # north-west, top left

class RoboEyes:
    def __init__(self, display, screen_width=128, screen_height=64, frame_rate=50):
        # Basic display properties and frame rate settings
        self.display = display
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.frame_interval = 1000 // frame_rate  # in milliseconds
        self.fps_timer = time.ticks_ms()
        
        # Mood and expression controls
        self.tired = False
        self.angry = False
        self.happy = False
        self.curious = False
        self.cyclops = False
        self.eyeL_open = False
        self.eyeR_open = False

        # Default geometries for both eyes and spacing
        self.eyeLwidth_default = 36
        self.eyeLheight_default = 36
        self.eyeLwidth_current = self.eyeLwidth_default
        self.eyeLheight_current = 1      # start with closed eye
        self.eyeLwidth_next = self.eyeLwidth_default
        self.eyeLheight_next = self.eyeLheight_default
        self.eyeLheight_offset = 0
        
        self.eyeLborder_radius_default = 8
        self.eyeLborder_radius_current = self.eyeLborder_radius_default
        self.eyeLborder_radius_next = self.eyeLborder_radius_default
        
        self.eyeRwidth_default = self.eyeLwidth_default
        self.eyeRheight_default = self.eyeLheight_default
        self.eyeRwidth_current = self.eyeRwidth_default
        self.eyeRheight_current = 1      # start with closed eye
        self.eyeRwidth_next = self.eyeRwidth_default
        self.eyeRheight_next = self.eyeRheight_default
        self.eyeRheight_offset = 0
        
        self.eyeRborder_radius_default = 8
        self.eyeRborder_radius_current = self.eyeRborder_radius_default
        self.eyeRborder_radius_next = self.eyeRborder_radius_default
        
        # Spacing between eyes
        self.space_between_default = 10
        self.space_between_current = self.space_between_default
        self.space_between_next = self.space_between_default
        
        # Position defaults (using left eye as reference)
        self.eyeLx_default = (self.screen_width - (self.eyeLwidth_default + self.space_between_default + self.eyeRwidth_default)) // 2
        self.eyeLy_default = (self.screen_height - self.eyeLheight_default) // 2
        self.eyeLx = self.eyeLx_default
        self.eyeLy = self.eyeLy_default
        self.eyeLx_next = self.eyeLx
        self.eyeLy_next = self.eyeLy
        
        # Right eye coordinates (relative to left)
        self.eyeRx_default = self.eyeLx + self.eyeLwidth_current + self.space_between_default
        self.eyeRy_default = self.eyeLy
        self.eyeRx = self.eyeRx_default
        self.eyeRy = self.eyeRy_default
        self.eyeRx_next = self.eyeRx
        self.eyeRy_next = self.eyeRy
        
        # Eyelid settings
        self.eyelids_height_max = self.eyeLheight_default // 2
        self.eyelids_tired_height = 0
        self.eyelids_tired_height_next = 0
        self.eyelids_angry_height = 0
        self.eyelids_angry_height_next = 0
        self.eyelids_happy_bottom_offset_max = (self.eyeLheight_default // 2) + 3
        self.eyelids_happy_bottom_offset = 0
        self.eyelids_happy_bottom_offset_next = 0
        
        # Animation flags and timers
        self.h_flicker = False
        self.h_flicker_alternate = False
        self.h_flicker_amplitude = 2
        
        self.v_flicker = False
        self.v_flicker_alternate = False
        self.v_flicker_amplitude = 10
        
        self.autoblinker = False
        self.blink_interval = 1  # in seconds
        self.blink_interval_variation = 4  # in seconds
        self.blink_timer = time.ticks_ms()
        
        self.idle = False
        self.idle_interval = 1  # in seconds
        self.idle_interval_variation = 3  # in seconds
        self.idle_animation_timer = time.ticks_ms()
        
        self.confused = False
        self.confused_animation_timer = 0
        self.confused_animation_duration = 500  # ms
        self.confused_toggle = True
        
        self.laugh = False
        self.laugh_animation_timer = 0
        self.laugh_animation_duration = 500  # ms
        self.laugh_toggle = True

    def begin(self, width, height, frame_rate):
        self.screen_width = width
        self.screen_height = height
        self.display.fill(BGCOLOR)
        self.display.show()
        self.eyeLheight_current = 1
        self.eyeRheight_current = 1
        self.set_framerate(frame_rate)

    def update(self):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.fps_timer) >= self.frame_interval:
            self.draw_eyes()
            self.fps_timer = current_time

    def set_framerate(self, fps):
        self.frame_interval = 1000 // fps

    def set_width(self, left_eye, right_eye):
        self.eyeLwidth_next = left_eye
        self.eyeRwidth_next = right_eye
        self.eyeLwidth_default = left_eye
        self.eyeRwidth_default = right_eye

    def set_height(self, left_eye, right_eye):
        self.eyeLheight_next = left_eye
        self.eyeRheight_next = right_eye
        self.eyeLheight_default = left_eye
        self.eyeRheight_default = right_eye

    def set_border_radius(self, left_eye, right_eye):
        self.eyeLborder_radius_next = left_eye
        self.eyeRborder_radius_next = right_eye
        self.eyeLborder_radius_default = left_eye
        self.eyeRborder_radius_default = right_eye

    def set_space_between(self, space):
        self.space_between_next = space
        self.space_between_default = space

    def set_mood(self, mood):
        if mood == TIRED:
            self.tired = True
            self.angry = False
            self.happy = False
        elif mood == ANGRY:
            self.tired = False
            self.angry = True
            self.happy = False
        elif mood == HAPPY:
            self.tired = False
            self.angry = False
            self.happy = True
        else:
            self.tired = self.angry = self.happy = False

    def set_position(self, position):
        if position == N:
            self.eyeLx_next = self.screen_width // 2
            self.eyeLy_next = 0
        elif position == NE:
            self.eyeLx_next = self.screen_width
            self.eyeLy_next = 0
        elif position == E:
            self.eyeLx_next = self.screen_width
            self.eyeLy_next = self.screen_height // 2
        elif position == SE:
            self.eyeLx_next = self.screen_width
            self.eyeLy_next = self.screen_height
        elif position == S:
            self.eyeLx_next = self.screen_width // 2
            self.eyeLy_next = self.screen_height
        elif position == SW:
            self.eyeLx_next = 0
            self.eyeLy_next = self.screen_height
        elif position == W:
            self.eyeLx_next = 0
            self.eyeLy_next = self.screen_height // 2
        elif position == NW:
            self.eyeLx_next = 0
            self.eyeLy_next = 0
        else:
            self.eyeLx_next = self.screen_width // 2
            self.eyeLy_next = self.screen_height // 2

    def set_autoblinker(self, active, interval=None, variation=None):
        self.autoblinker = active
        if interval is not None:
            self.blink_interval = interval
        if variation is not None:
            self.blink_interval_variation = variation

    def set_idle_mode(self, active, interval=None, variation=None):
        self.idle = active
        if interval is not None:
            self.idle_interval = interval
        if variation is not None:
            self.idle_interval_variation = variation

    def set_curiosity(self, curious_bit):
        self.curious = curious_bit

    def set_cyclops(self, cyclops_bit):
        self.cyclops = cyclops_bit

    def set_h_flicker(self, flicker_bit, amplitude=None):
        self.h_flicker = flicker_bit
        if amplitude is not None:
            self.h_flicker_amplitude = amplitude

    def set_v_flicker(self, flicker_bit, amplitude=None):
        self.v_flicker = flicker_bit
        if amplitude is not None:
            self.v_flicker_amplitude = amplitude

    def get_screen_constraint_x(self):
        return self.screen_width - self.eyeLwidth_current - self.space_between_current - self.eyeRwidth_current

    def get_screen_constraint_y(self):
        return self.screen_height - self.eyeLheight_default

    def close(self, left=True, right=True):
        if left:
            self.eyeLheight_next = 1
            self.eyeL_open = False
        if right:
            self.eyeRheight_next = 1
            self.eyeR_open = False

    def open(self, left=True, right=True):
        if left:
            self.eyeL_open = True
        if right:
            self.eyeR_open = True

    def blink(self, left=True, right=True):
        self.close(left, right)
        self.open(left, right)

    def anim_confused(self):
        self.confused = True

    def anim_laugh(self):
        self.laugh = True

    def draw_horizontal_line(self, x, y, length, color):
        self.display.fill_rect(x, y, length, 1, color)

    def fill_circle(self, x0, y0, r, color):
        x = 0
        y = r
        f = 1 - r
        dx = 1
        dy = -2 * r
        self.draw_horizontal_line(x0 - r, y0, 2 * r + 1, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            f += dx
            dx += 2
            self.draw_horizontal_line(x0 - x, y0 + y, 2 * x + 1, color)
            self.draw_horizontal_line(x0 - x, y0 - y, 2 * x + 1, color)
            self.draw_horizontal_line(x0 - y, y0 + x, 2 * y + 1, color)
            self.draw_horizontal_line(x0 - y, y0 - x, 2 * y + 1, color)

    def fill_round_rect(self, x, y, w, h, r, color):
        self.display.fill_rect(x + r, y, w - 2 * r, h, color)
        self.display.fill_rect(x, y + r, r, h - 2 * r, color)
        self.display.fill_rect(x + w - r, y + r, r, h - 2 * r, color)
        self.fill_circle(x + r, y + r, r, color)
        self.fill_circle(x + w - r - 1, y + r, r, color)
        self.fill_circle(x + r, y + h - r - 1, r, color)
        self.fill_circle(x + w - r - 1, y + h - r - 1, r, color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        if y0 > y1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        if y0 > y1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        if y1 == y2:
            self.fill_flat_bottom_triangle(x0, y0, x1, y1, x2, y2, color)
        elif y0 == y1:
            self.fill_flat_top_triangle(x0, y0, x1, y1, x2, y2, color)
        else:
            x3 = int(x0 + ((y1 - y0) / float(y2 - y0)) * (x2 - x0))
            y3 = y1
            self.fill_flat_bottom_triangle(x0, y0, x1, y1, x3, y3, color)
            self.fill_flat_top_triangle(x1, y1, x3, y3, x2, y2, color)

    def fill_flat_bottom_triangle(self, x0, y0, x1, y1, x2, y2, color):
        inv_slope1 = (x1 - x0) / float(y1 - y0) if (y1 - y0) != 0 else 0
        inv_slope2 = (x2 - x0) / float(y1 - y0) if (y1 - y0) != 0 else 0
        curx1 = x0
        curx2 = x0
        for scanline_y in range(y0, y1 + 1):
            start_x = int(min(curx1, curx2))
            end_x = int(max(curx1, curx2))
            self.display.fill_rect(start_x, scanline_y, end_x - start_x + 1, 1, color)
            curx1 += inv_slope1
            curx2 += inv_slope2

    def fill_flat_top_triangle(self, x0, y0, x1, y1, x2, y2, color):
        inv_slope1 = (x2 - x0) / float(y2 - y0) if (y2 - y0) != 0 else 0
        inv_slope2 = (x2 - x1) / float(y2 - y1) if (y2 - y1) != 0 else 0
        curx1 = x2
        curx2 = x2
        for scanline_y in range(y2, y0 - 1, -1):
            start_x = int(min(curx1, curx2))
            end_x = int(max(curx1, curx2))
            self.display.fill_rect(start_x, scanline_y, end_x - start_x + 1, 1, color)
            curx1 -= inv_slope1
            curx2 -= inv_slope2

    def draw_eyes(self):
        current_time = time.ticks_ms()
        
        if self.curious:
            if self.eyeLx_next <= 10:
                self.eyeLheight_offset = 8
            elif self.eyeLx_next >= (self.get_screen_constraint_x() - 10) and self.cyclops:
                self.eyeLheight_offset = 8
            else:
                self.eyeLheight_offset = 0
            if self.eyeRx_next >= self.screen_width - self.eyeRwidth_current - 10:
                self.eyeRheight_offset = 8
            else:
                self.eyeRheight_offset = 0
        else:
            self.eyeLheight_offset = 0
            self.eyeRheight_offset = 0

        self.eyeLheight_current = (self.eyeLheight_current + self.eyeLheight_next + self.eyeLheight_offset) // 2
        self.eyeLy += ((self.eyeLheight_default - self.eyeLheight_current) // 2)
        self.eyeLy -= self.eyeLheight_offset // 2

        self.eyeRheight_current = (self.eyeRheight_current + self.eyeRheight_next + self.eyeRheight_offset) // 2
        self.eyeRy += ((self.eyeRheight_default - self.eyeRheight_current) // 2)
        self.eyeRy -= self.eyeRheight_offset // 2

        if self.eyeL_open and self.eyeLheight_current <= 1 + self.eyeLheight_offset:
            self.eyeLheight_next = self.eyeLheight_default
        if self.eyeR_open and self.eyeRheight_current <= 1 + self.eyeRheight_offset:
            self.eyeRheight_next = self.eyeRheight_default

        self.eyeLwidth_current = (self.eyeLwidth_current + self.eyeLwidth_next) // 2
        self.eyeRwidth_current = (self.eyeRwidth_current + self.eyeRwidth_next) // 2
        self.space_between_current = (self.space_between_current + self.space_between_next) // 2
        self.eyeLx = (self.eyeLx + self.eyeLx_next) // 2
        self.eyeLy = (self.eyeLy + self.eyeLy_next) // 2
        self.eyeRx_next = self.eyeLx_next + self.eyeLwidth_current + self.space_between_current
        self.eyeRy_next = self.eyeLy_next
        self.eyeRx = (self.eyeRx + self.eyeRx_next) // 2
        self.eyeRy = (self.eyeRy + self.eyeRy_next) // 2
        self.eyeLborder_radius_current = (self.eyeLborder_radius_current + self.eyeLborder_radius_next) // 2
        self.eyeRborder_radius_current = (self.eyeRborder_radius_current + self.eyeRborder_radius_next) // 2

        if self.autoblinker:
            if time.ticks_diff(current_time, self.blink_timer) >= 0:
                self.blink()
                self.blink_timer = current_time + (self.blink_interval * 1000) + (random.randint(0, self.blink_interval_variation) * 1000)
        if self.laugh:
            if self.laugh_toggle:
                self.set_v_flicker(True, 5)
                self.laugh_animation_timer = current_time
                self.laugh_toggle = False
            elif time.ticks_diff(current_time, self.laugh_animation_timer) >= self.laugh_animation_duration:
                self.set_v_flicker(False, 0)
                self.laugh_toggle = True
                self.laugh = False
        if self.confused:
            if self.confused_toggle:
                self.set_h_flicker(True, 20)
                self.confused_animation_timer = current_time
                self.confused_toggle = False
            elif time.ticks_diff(current_time, self.confused_animation_timer) >= self.confused_animation_duration:
                self.set_h_flicker(False, 0)
                self.confused_toggle = True
                self.confused = False
        if self.idle:
            if time.ticks_diff(current_time, self.idle_animation_timer) >= 0:
                self.eyeLx_next = random.randint(0, self.get_screen_constraint_x())
                self.eyeLy_next = random.randint(0, self.get_screen_constraint_y())
                self.idle_animation_timer = current_time + (self.idle_interval * 1000) + (random.randint(0, self.idle_interval_variation) * 1000)
        if self.h_flicker:
            if self.h_flicker_alternate:
                self.eyeLx += self.h_flicker_amplitude
                self.eyeRx += self.h_flicker_amplitude
            else:
                self.eyeLx -= self.h_flicker_amplitude
                self.eyeRx -= self.h_flicker_amplitude
            self.h_flicker_alternate = not self.h_flicker_alternate
        if self.v_flicker:
            if self.v_flicker_alternate:
                self.eyeLy += self.v_flicker_amplitude
                self.eyeRy += self.v_flicker_amplitude
            else:
                self.eyeLy -= self.v_flicker_amplitude
                self.eyeRy -= self.v_flicker_amplitude
            self.v_flicker_alternate = not self.v_flicker_alternate
        if self.cyclops:
            self.eyeRwidth_current = 0
            self.eyeRheight_current = 0
            self.space_between_current = 0

        self.display.fill(BGCOLOR)

        # Use a threshold to force border radius to 0 until at least a quarter of the eye is open,
        # and also during a blink when the target height is 1.
        threshold = self.eyeLheight_default // 4
        eyeLradius = 0 if (self.eyeLheight_next <= 1 or self.eyeLheight_current < threshold) else self.eyeLborder_radius_current
        eyeRradius = 0 if (self.eyeRheight_next <= 1 or self.eyeRheight_current < threshold) else self.eyeRborder_radius_current

        self.fill_round_rect(self.eyeLx, self.eyeLy, self.eyeLwidth_current,
                             self.eyeLheight_current, eyeLradius, MAINCOLOR)
        if not self.cyclops:
            self.fill_round_rect(self.eyeRx, self.eyeRy, self.eyeRwidth_current,
                                 self.eyeRheight_current, eyeRradius, MAINCOLOR)

        if self.tired:
            self.eyelids_tired_height_next = self.eyeLheight_current // 2
            self.eyelids_angry_height_next = 0
        else:
            self.eyelids_tired_height_next = 0
        if self.angry:
            self.eyelids_angry_height_next = self.eyeLheight_current // 2
            self.eyelids_tired_height_next = 0
        else:
            self.eyelids_angry_height_next = 0
        if self.happy:
            self.eyelids_happy_bottom_offset_next = self.eyeLheight_current // 2
        else:
            self.eyelids_happy_bottom_offset_next = 0

        self.eyelids_happy_bottom_offset = (self.eyelids_happy_bottom_offset + self.eyelids_happy_bottom_offset_next) // 2
        self.eyelids_tired_height = (self.eyelids_tired_height + self.eyelids_tired_height_next) // 2
        if not self.cyclops:
            self.fill_triangle(self.eyeLx, self.eyeLy - 1,
                               self.eyeLx + self.eyeLwidth_current, self.eyeLy - 1,
                               self.eyeLx, self.eyeLy + self.eyelids_tired_height - 1, BGCOLOR)
            self.fill_triangle(self.eyeRx, self.eyeRy - 1,
                               self.eyeRx + self.eyeRwidth_current, self.eyeRy - 1,
                               self.eyeRx + self.eyeRwidth_current, self.eyeRy + self.eyelids_tired_height - 1, BGCOLOR)
        else:
            half_width = self.eyeLwidth_current // 2
            self.fill_triangle(self.eyeLx, self.eyeLy - 1,
                               self.eyeLx + half_width, self.eyeLy - 1,
                               self.eyeLx, self.eyeLy + self.eyelids_tired_height - 1, BGCOLOR)
            self.fill_triangle(self.eyeLx + half_width, self.eyeLy - 1,
                               self.eyeLx + self.eyeLwidth_current, self.eyeLy - 1,
                               self.eyeLx + self.eyeLwidth_current, self.eyeLy + self.eyelids_tired_height - 1, BGCOLOR)
        self.eyelids_angry_height = (self.eyelids_angry_height + self.eyelids_angry_height_next) // 2
        if not self.cyclops:
            self.fill_triangle(self.eyeLx, self.eyeLy - 1,
                               self.eyeLx + self.eyeLwidth_current, self.eyeLy - 1,
                               self.eyeLx + self.eyeLwidth_current, self.eyeLy + self.eyelids_angry_height - 1, BGCOLOR)
            self.fill_triangle(self.eyeRx, self.eyeRy - 1,
                               self.eyeRx + self.eyeRwidth_current, self.eyeRy - 1,
                               self.eyeRx, self.eyeRy + self.eyelids_angry_height - 1, BGCOLOR)
        else:
            half_width = self.eyeLwidth_current // 2
            self.fill_triangle(self.eyeLx, self.eyeLy - 1,
                               self.eyeLx + half_width, self.eyeLy - 1,
                               self.eyeLx + half_width, self.eyeLy + self.eyelids_angry_height - 1, BGCOLOR)
            self.fill_triangle(self.eyeLx + half_width, self.eyeLy - 1,
                               self.eyeLx + self.eyeLwidth_current, self.eyeLy - 1,
                               self.eyeLx + half_width, self.eyeLy + self.eyelids_angry_height - 1, BGCOLOR)
        self.fill_round_rect(self.eyeLx - 1,
                             (self.eyeLy + self.eyeLheight_current) - self.eyelids_happy_bottom_offset + 1,
                             self.eyeLwidth_current + 2, self.eyeLheight_default,
                             self.eyeLborder_radius_current, BGCOLOR)
        if not self.cyclops:
            self.fill_round_rect(self.eyeRx - 1,
                                 (self.eyeRy + self.eyeRheight_current) - self.eyelids_happy_bottom_offset + 1,
                                 self.eyeRwidth_current + 2, self.eyeRheight_default,
                                 self.eyeRborder_radius_current, BGCOLOR)
        self.display.show()