import time
import machine

# The roboeyes library uses the ssd1306 library to control the display, so don't use any other driver.
from ssd1306 import SSD1306_I2C
from roboeyes import RoboEyes

# Change the pin numbers to fit your controller's i2c bus.
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

# Assuming you have no other i2c devices connectes on the same .bus
oledAddr = i2c.scan()[0]

# Create an I2C oled display object.
display = SSD1306_I2C(128, 64, i2c, addr=oledAddr)

# Create a RoboEyes object with the display.
eyes = RoboEyes(display)
# Initialize the RoboEyes object with the display dimensions and frame rate.
eyes.begin(128, 64, 50)

# Set the idle mode with a 1-3 second interval.
eyes.set_idle_mode(True, 1, 3)
# Set the autoblinker with a 1-4 second interval.
eyes.set_autoblinker(True, 1, 4)

while True:
    # Update the display at the specified frame rate.
    eyes.update()