from machine import Pin, SoftI2C as I2C, PWM, Timer
import machine
import ssd1306
from font import Font
import time
from time import sleep_ms, ticks_ms
import random
import network
import ntptime
import utime

#init screen connection
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=4000000) 
display = ssd1306.SSD1306_I2C(128, 64, i2c)  # display object
f=Font(display)

#connect to buzzer
buzzer_pin = Pin(23, Pin.OUT)
buzzer_pwm = PWM(buzzer_pin)
buzzer_pwm.duty(0)

def buzz(duration_ms, frequency):
    buzzer_pwm.freq(frequency)  # Set the PWM frequency
    buzzer_pwm.duty(512)        # Set the PWM duty cycle (50% for a beep)
    sleep_ms(duration_ms)
    buzzer_pwm.duty(0)

#button listener
button = Pin(4, Pin.IN, Pin.PULL_UP)

MODE_WELCOME 	= 'welcome'
MODE_COUNTDOWN 	= 'countdown'
MODE_GAME		= 'game'
MODE_RESULTS	= 'results'

GAME_TIME_MS 	= 5000
GAME_TITLE 		= 'Click Frenzy'

#init variables
mode = MODE_WELCOME
last_button_status = 0
last_event = ticks_ms()
show_message = True
countdown = 3
my_font=Font(display)
total_clicks = 0

def check_button_pressed():
    global last_button_status
    button_pressed = not button.value()
    
    if button_pressed:
        if last_button_status == 0:
            last_button_status = 1
            buzz(10, 800)
            return True
        return False
        
    last_button_status = 0
    return False
        
def draw_welcome_message():
    global MODE_COUNTDOWN, mode, last_event, show_message, countdown, my_font
    my_font.text(GAME_TITLE, 10, 0, 16)
    
    now = ticks_ms()
    if now - last_event > 1000:
        last_event = now
        show_message = not show_message
    
    if show_message:
        my_font.text('Click to start', 5, 30, 1)
    if check_button_pressed():
        mode = MODE_COUNTDOWN
        countdown = 3
        last_event = now
        
def draw_countdown():
    global my_font, countdown, last_event, mode, GAME_TIME_MS, total_clicks
    my_font.text(GAME_TITLE, 10, 0, 16)
    my_font.text('Get ready!', 15, 20, 16)
    
    now = ticks_ms()
    if now - last_event > 1000:
        last_event = now
        countdown -= 1
    
    #prepare for next step
    if countdown == 0:
        mode = MODE_GAME
        last_event = now
        countdown = GAME_TIME_MS
        total_clicks = 0
    else:
        my_font.text(str(countdown), 50, 35, 32)

def draw_game():
    global my_font, total_clicks, countdown, last_event, mode
    
    now = ticks_ms()
    
    countdown -= (now-last_event)
    
    if countdown <= 0:
        mode = MODE_RESULTS
        countdown = 3
        return
    
    if check_button_pressed():
        total_clicks += 1
    
    my_font.text('Time left: ' + str(countdown/1000.0), 0, 0, 1)
    my_font.text('Clicks:', 20, 20, 1)
    my_font.text(str(total_clicks), 50, 35, 32)
    
    last_event = ticks_ms()

def draw_results():
    global my_font, total_clicks, countdown, mode, last_event
    
    now = ticks_ms()
    if now - last_event <= 5000:
        my_font.text("Game over!", 20, 0, 1)
        my_font.text("Your score:", 10, 15, 16)
        my_font.text(str(total_clicks), 50, 35, 32)
    else:
        my_font.text('Retry?', 20, 20, 32)
        if check_button_pressed():
            countdown = 3
            mode = MODE_COUNTDOWN
            

while True:
    # clear the screen
    display.fill(0)
    
    if mode == MODE_WELCOME:
        draw_welcome_message()
    elif mode == MODE_COUNTDOWN:
        draw_countdown()
    elif mode == MODE_GAME:
        draw_game()
    elif mode == MODE_RESULTS:
        draw_results()
    
    display.show()
    
    