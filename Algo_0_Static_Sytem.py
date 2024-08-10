import random
import time
import threading
import pygame
import sys

# Constants
WIDTH, HEIGHT = 1400, 800
ROAD_WIDTH = 220  # Width of the roads
LINE_WIDTH = 2    # Width of the road lines
ROAD_COLOR = (50, 50, 50)  # Dark gray color for the road
LINE_COLOR = (255, 255, 255)  # White color for the lines
FONT_COLOR = (255, 255, 255)  # White color for the text

# Default values of signal timers
green_default = {0:10, 1:10, 2:10, 3:10}
red_default = 150
yellow_default = 5

signals = []
no_of_signals = 4
current_green = 0   # Indicates which signal is green currently
cycle = 0
next_green = (current_green+1)%no_of_signals   # Indicates which signal will turn green next
current_yellow = 0   # Indicates whether yellow signal is on or off 

speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5}  # average speeds of vehicles

# Coordinates of vehicles' start
#Traffic Generation Coordinates:
x_coordinates = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[600,626,659]}    
y_coordinates = {'right':[345,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicle_types = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
direction_numbers = {0:'right', 1:'down', 2:'left', 3:'up'}
vehicle_crossed = {'right': 0, 'down': 0, 'left': 0, 'up': 0}  # Vehicle counts for each direction that crossed
vehicle_generated = {'right': 0, 'down': 0, 'left': 0, 'up': 0} ## Vehicle counts for each direction that are in queue
vehicle_queue = {'right': 0, 'down': 0, 'left': 0, 'up': 0} ## Vehicle counts for each direction that are in queue

# Coordinates of signal image, timer, and vehicle count
signal_coordinates = [(530,230),(810,230),(810,570),(530,570)]
signal_timer_coordinates = [(530,210),(810,210),(810,550),(530,550)]

# Coordinates of stop lines
stop_lines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
#Offset for cars to stop
default_stop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stopping_gap = 15    # stopping gap
moving_gap = 15   # moving gap

pygame.init()
simulation = pygame.sprite.Group()

# Load signal images
green_signal = pygame.image.load('images/signals/green.png')
red_signal = pygame.image.load('images/signals/red.png')
yellow_signal = pygame.image.load('images/signals/yellow.png')

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signal_text = ""
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicle_class, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicle_class = vehicle_class
        self.speed = speeds[vehicle_class]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x_coordinates[direction][lane]
        self.y = y_coordinates[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicle_class + ".png"
        self.image = pygame.image.load(path)
        self.stop = default_stop[direction]
        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0:
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stopping_gap
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stopping_gap
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stopping_gap
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stopping_gap

        # Adjust starting and stopping coordinates
        if direction == 'right':
            temp = self.image.get_rect().width + stopping_gap
            x_coordinates[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stopping_gap
            x_coordinates[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stopping_gap
            y_coordinates[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stopping_gap
            y_coordinates[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        crossed_line = False
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stop_lines[self.direction]:
                self.crossed = 1
                crossed_line = True
            if self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (current_green == 0 and current_yellow == 0):
                if self.index == 0 or self.x + self.image.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - moving_gap):
                    self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stop_lines[self.direction]:
                self.crossed = 1
                crossed_line = True
            if self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (current_green == 1 and current_yellow == 0):
                if self.index == 0 or self.y + self.image.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - moving_gap):
                    self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stop_lines[self.direction]:
                self.crossed = 1
                crossed_line = True
            if self.x >= self.stop or self.crossed == 1 or (current_green == 2 and current_yellow == 0):
                if self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + moving_gap):
                    self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stop_lines[self.direction]:
                self.crossed = 1
                crossed_line = True
            if self.y >= self.stop or self.crossed == 1 or (current_green == 3 and current_yellow == 0):
                if self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + moving_gap):
                    self.y -= self.speed
        
        if crossed_line:
            vehicle_crossed[self.direction] += 1

# Function to display vehicle counts
def display_vehicle_crossed(screen, font):
    x_offsets = {'right': 100, 'down': 350, 'left': 900, 'up': 1150}  # Example positions
    y_offset = 50
    for direction in vehicle_crossed:
        text = f"{direction.title()} Crossed: {vehicle_crossed[direction]}"
        text_surface = font.render(text, True, (255, 255, 255))  # White color
        screen.blit(text_surface, (x_offsets[direction], y_offset))

# Initialization and signal handling
def initialize():
    ts1 = TrafficSignal(red_default, yellow_default, green_default[0])
    signals.append(ts1)
    ts2 = TrafficSignal(red_default, yellow_default, green_default[1])
    signals.append(ts2)
    ts3 = TrafficSignal(red_default, yellow_default, green_default[2])
    signals.append(ts3)
    ts4 = TrafficSignal(red_default, yellow_default, green_default[3])
    signals.append(ts4)
    repeat()

def repeat():
    global current_green, current_yellow, next_green, cycle
    while signals[current_green].green > 0:
        update_values()
        time.sleep(1)
    current_yellow = 1
    for i in range(0, 3):
        for vehicle in vehicles[direction_numbers[current_green]][i]:
            vehicle.stop = default_stop[direction_numbers[current_green]]
    while signals[current_green].yellow > 0:
        update_values()
        time.sleep(1)
    current_yellow = 0

    signals[current_green].green = green_default[current_green]
    signals[current_green].yellow = yellow_default
    signals[current_green].red = red_default
       
    if current_green == 3:  # Check if the current green signal was 'up' (3)
        cycle += 1  # Increment the cycle count after completing a full cycle
    
    current_green = next_green
    next_green = (current_green + 1) % no_of_signals
    signals[next_green].red = signals[current_green].yellow + signals[current_green].green
    repeat()

def update_values():
    for i in range(no_of_signals):
        if i == current_green:
            if current_yellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generate_vehicles():
    while True:
        vehicle_type = random.randint(0, 3)
        lane_number = random.randint(0, 2)
        direction_number = random.randint(0, 3)
        Vehicle(lane_number, vehicle_types[vehicle_type], direction_number, direction_numbers[direction_number])
        vehicle_generated[direction_numbers[direction_number]] += 1  # Increment vehicle count when a new vehicle is created
        time.sleep(random.randint(1, 3))

def display_vehicle_counts(screen, font):
    x_offsets = {'right': 100, 'down': 350, 'left': 900, 'up': 1150}  # Example positions
    y_offset = 100
    y_offset_2 = 150
    for direction in vehicle_generated:
        total_generated = vehicle_generated[direction]
        total_crossed = vehicle_crossed[direction]
        total_queue = vehicle_generated[direction] - vehicle_crossed[direction]
        text = f"{direction.title()} Generated: {total_generated}"
        text_2 = f"{direction.title()} Queue: {total_queue}"
        text_surface = font.render(text, True, (255, 255, 255))  # White color
        text_surface_2 = font.render(text_2, True, (255, 255, 255))  # White color
        screen.blit(text_surface, (x_offsets[direction], y_offset))
        screen.blit(text_surface_2, (x_offsets[direction], y_offset_2))

def display_traffic_light_timers(screen, font):
    # Display the remaining green time for each signal
    for i in range(no_of_signals):
        # Only display green time if the light is green and not yellow
        if i == current_green and current_yellow == 0:
            green_time_text = font.render(f"GT: {signals[i].green}s", True, FONT_COLOR)
            screen.blit(green_time_text, (signal_timer_coordinates[i][0], signal_timer_coordinates[i][1]))


# Main execution loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    thread1 = threading.Thread(target=initialize)
    thread1.daemon = True
    thread1.start()

    thread2 = threading.Thread(target=generate_vehicles)
    thread2.daemon = True
    thread2.start()

    fps_font = pygame.font.Font(None, 24)  # Font for FPS display
    time_font = pygame.font.Font(None, 24)  # Font for time display
    start_time = time.time()  # Record the start time of the simulation

    while True:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Fill background with green
        screen.fill((0, 128, 0))


        # Draw roads
        # Horizontal road
        pygame.draw.rect(screen, ROAD_COLOR, (0, HEIGHT // 2 - ROAD_WIDTH // 2 + 35, WIDTH, ROAD_WIDTH ))
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT // 2 + 35), (WIDTH, HEIGHT // 2 + 35), LINE_WIDTH)
        
        # Vertical road
        pygame.draw.rect(screen, ROAD_COLOR, (WIDTH // 2 - ROAD_WIDTH // 2 - 5, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.line(screen, LINE_COLOR, (WIDTH // 2 - 5, 0), (WIDTH // 2 - 5, HEIGHT), LINE_WIDTH)

        # Display signals and vehicle counts
        for i in range(no_of_signals):
            if i == current_green:
                screen.blit(green_signal, signal_coordinates[i])
            else:
                screen.blit(red_signal, signal_coordinates[i])
        
        # Display vehicle counts and other information
        display_vehicle_counts(screen, font)
        display_vehicle_crossed(screen, font)

        # Update vehicles
        for vehicle in simulation:
            vehicle.render(screen)
            vehicle.move()
        

        # Display timers for green lights
        display_traffic_light_timers(screen, time_font)

        # FPS display
        fps_text = fps_font.render(f"FPS: {int(clock.get_fps())}", True, FONT_COLOR)
        screen.blit(fps_text, (10, HEIGHT - 50))  # Adjusted position

        # Time display (Elapsed time since simulation started)
        elapsed_time = time.time() - start_time
        time_text = time_font.render(f"Time: {int(elapsed_time)}s", True, FONT_COLOR)
        screen.blit(time_text, (10, HEIGHT - 100))  # Adjusted position

        # Display cycle count
        cycle_text = time_font.render(f"Cycle Count: {cycle}", True, FONT_COLOR)
        screen.blit(cycle_text, (WIDTH - 200, HEIGHT - 100))  # Adjust position as needed


        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()

