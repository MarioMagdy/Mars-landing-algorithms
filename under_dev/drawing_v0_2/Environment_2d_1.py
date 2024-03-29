import pygame
import math
import numpy as np

slower= 200000

# Constants
MARS_GRAVITY = -3.71  # m/s^2
AIR_RESISTANCE_COEFF = 0.05  # (adjustable for different air densities) UNUSED
LEFT_DRAG_COEFF = 0.01  # (adjustable for spacecraft design)  UNUSED
LD_C = 10 # (adjustable)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCALE = 10  # meters per pixel (adjust for visual representation)

# TODO: Get the accurate velocities
# User input (replace with prompts and error handling)
initial_altitude = 5000.0  # meters
initial_horizontal_velocity = 0.0  # m/s (positive to the right)

initial_vertical_velocity = -50000.0  # m/s (negative for downward)
max_thrust = 10.0  # m/s^2
spacecraft_mass = 500 #
fuel_mass = 100.0  # kg
fuel_consumption_rate = 1.0  # kg/s per unit of thrust (adjustable for engine efficiency)


# Simulation variables
x_position = 600  # meters
y_position = initial_altitude  # meters (matches initial altitude)
x_velocity = initial_horizontal_velocity
y_velocity = initial_vertical_velocity
fuel_remaining = fuel_mass
thrust_x = 0.0  # m/s^2 (horizontal thrust)
thrust_y = 0.0  # m/s^2 (vertical thrust)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (133, 40, 20)  # For crash landing
YELLOW = (255, 255, 0)  # For successful landing


# Global variables for thruster power levels (0 to 100%)
left_vertical_thruster_power = 0.0
right_vertical_thruster_power = 0.0
up_horizontal_thruster_power = 0.0
down_horizontal_thruster_power = 0.0


# New global variable for spacecraft orientation (in degrees)
spacecraft_orientation = 0.0



def apply_thrust(dt):
    global x_velocity, y_velocity, fuel_remaining, spacecraft_orientation
    global left_vertical_thruster_power, right_vertical_thruster_power
    global up_horizontal_thruster_power, down_horizontal_thruster_power
    global x_velocity, y_velocity, fuel_remaining, thrust_x, thrust_y, spacecraft_orientation, right_thruster_power, left_thruster_power
    # Limit thrust based on fuel availability
    if fuel_remaining > 0:
        # Calculate the actual thrust force based on the power level (0 to 100%) and max thrust capability
        left_vertical_force = (left_vertical_thruster_power / 100.0) * max_thrust
        right_vertical_force = (right_vertical_thruster_power / 100.0) * max_thrust
        up_horizontal_force = (up_horizontal_thruster_power / 100.0) * max_thrust
        down_horizontal_force = (down_horizontal_thruster_power / 100.0) * max_thrust
        
        # The net horizontal thrust is the difference between the left and right vertical thruster forces
        net_horizontal_thrust = right_vertical_force - left_vertical_force
        
        # The net vertical thrust is the difference between the up and down horizontal thruster forces
        net_vertical_thrust = up_horizontal_force - down_horizontal_force
        
        # Update velocities based on the net thrust forces
        x_velocity += net_horizontal_thrust * dt
        y_velocity += (net_vertical_thrust + MARS_GRAVITY) * dt  # Including gravity in the vertical velocity update
        
        # Update the spacecraft's orientation based on the difference in thrust between opposing thrusters
        # The rotation rate could be adjusted by a constant to simulate the spacecraft's moment of inertia
        horizontal_rotation_rate = (left_vertical_force - right_vertical_force) * dt * 0.05
        vertical_rotation_rate = (down_horizontal_force - up_horizontal_force) * dt * 0.05
        
        # Update the spacecraft orientation
        spacecraft_orientation += horizontal_rotation_rate + vertical_rotation_rate
        
        # Fuel consumption is based on the total thrust exerted by all thrusters
        total_thrust = left_vertical_force + right_vertical_force + up_horizontal_force + down_horizontal_force
        fuel_remaining -= total_thrust * dt / fuel_consumption_rate
            
        # Update velocities based on the net thrust forces
        x_velocity += net_horizontal_thrust * dt
        y_velocity += (net_vertical_thrust + MARS_GRAVITY) * dt  # Including gravity in the vertical velocity update
    else:
        thrust_x = 0.0
        thrust_y = 0.0



def draw_speed_text(screen, x, y, x_velocity, y_velocity, font_size=16, font_color=WHITE):
    """
    Draws text displaying the spacecraft's x and y-axis velocities below it.

    Args:
        screen: The Pygame display surface.
        x: The x-coordinate of the spacecraft's center.
        y: The y-coordinate of the spacecraft's center.
        x_velocity: The spacecraft's x-axis velocity (m/s).
        y_velocity: The spacecraft's y-axis velocity (m/s).
        font_size: The size of the font used to display the text (default: 16).
        font_color: The color of the text (default: BLACK).
    """
    font = pygame.font.SysFont(None, font_size)

    # Format the text with one decimal place for velocity
    x_velocity_text = f"X-Velocity: {x_velocity:.1f} m/s"
    y_velocity_text = f"Y-Velocity: {y_velocity:.1f} m/s"

    # Render the text surfaces
    x_text_surface = font.render(x_velocity_text, True, font_color)
    y_text_surface = font.render(y_velocity_text, True, font_color)

    # Get the text surface dimensions for positioning
    x_text_width, x_text_height = x_text_surface.get_size()
    y_text_width, y_text_height = y_text_surface.get_size()

    # Place the text surfaces below the spacecraft with some offset
    x_text_x = x - x_text_width // 2  # Center the text horizontally below the spacecraft
    y_text_y = y + x_text_height + 20  # Position the text slightly below the spacecraft

    # Blit the text surfaces onto the screen
    screen.blit(x_text_surface, (x_text_x, y_text_y))
    screen.blit(y_text_surface, (x_text_x, y_text_y + y_text_height))




# Ensure max_thrust is accessible


def handle_thrust_controls(keys_pressed):
    """
    Checks for keyboard clicks and updates thrust based on user input.

    Args:
        keys_pressed: A dictionary containing the state of all pressed keys (True for pressed, False for not pressed).

    Returns:
        A tuple containing the horizontal and vertical thrust values (m/s^2).
    """
    global max_thrust

    horizontal_thrust = 0.0
    vertical_thrust = 0.0

    # Adjust these key codes based on your desired controls
    if keys_pressed[pygame.K_LEFT]:  # Left arrow key
        horizontal_thrust = -max_thrust  # Negative for left thrust

    if keys_pressed[pygame.K_RIGHT]:  # Right arrow key
        horizontal_thrust = max_thrust

    if keys_pressed[pygame.K_UP]:  # Up arrow key
        vertical_thrust = max_thrust

    return horizontal_thrust, vertical_thrust







def update_orientation(dt, thrust_x):
    global spacecraft_orientation
    # Adjust the orientation based on the horizontal thrust
    # The multiplier can be adjusted to represent the sensitivity of the spacecraft's rotation
    orientation_change = thrust_x * dt * 0.1  # This is an arbitrary value for rotation sensitivity
    spacecraft_orientation += orientation_change



def draw_spacecraft(screen, x, y, angle):
    """
    Draws a rotated triangle representing the spacecraft.

    Args:
        screen: The Pygame display surface.
        x: The x-coordinate of the spacecraft's center.
        y: The y-coordinate of the spacecraft's center.
        angle: The angle to rotate the spacecraft (in degrees).
    """
    # Define the original spacecraft points
    points = [(x, y), (x - 10, y + 20), (x + 10, y + 20)]
    
    # Rotate each point around the spacecraft's center
    rotated_points = []
    for point in points:
        rotated_point = rotate_point(x, y, point[0], point[1], math.radians(angle))
        rotated_points.append(rotated_point)
    
    pygame.draw.polygon(screen, WHITE, rotated_points)

def rotate_point(cx, cy, x, y, angle):
    """
    Rotates a point around a given center point.

    Args:
        cx: The x-coordinate of the center point.
        cy: The y-coordinate of the center point.
        x: The x-coordinate of the point to rotate.
        y: The y-coordinate of the point to rotate.
        angle: The angle of rotation (in radians).

    Returns:
        A tuple representing the new x and y coordinates after rotation.
    """
    sin_angle = math.sin(angle)
    cos_angle = math.cos(angle)
    
    # Translate point to origin
    x -= cx
    y -= cy
    
    # Rotate point
    x_new = x * cos_angle - y * sin_angle
    y_new = x * sin_angle + y * cos_angle
    
    # Translate point back
    x_new += cx
    y_new += cy
    
    return x_new, y_new


def apply_air_resistance_v2(dt, density=0.02):  # Density is in kg/m^3 (adjustable)
    """
    Calculates and applies air resistance force to each component of the spacecraft's velocity.

    Args:
        dt: Timestep (seconds).
        v: The spacecraft's velocity as a NumPy array (m/s). Can be 1D (scalar) or 3D (vector).
        density: The air density (kg/m^3). Defaults to 0.02 (approximate Martian surface density).
    """
    # Reference speed of sound in Martian atmosphere (adjustable)
    speed_of_sound = 240  # m/s

    # Separate x and y components of velocity
    global x_velocity, y_velocity 


    # Calculate individual air resistance forces for x and y components
    if abs(x_velocity) > 0:  # Apply air resistance only for positive x-velocity (assuming right is positive)
        drag_coefficient_x = calculate_drag_coefficient(x_velocity / speed_of_sound) * LD_C # Adjust based on Mach number for x-direction
        air_resistance_force_x = -0.5 * density * drag_coefficient_x * np.pi * (x_velocity**2)
        x_velocity +=(abs(x_velocity)/x_velocity) * air_resistance_force_x * dt / mass  # Apply force as acceleration and update x-velocity
    
    if abs(y_velocity) > 0:  # Apply air resistance only for positive y-velocity (assuming up is positive)
        drag_coefficient_y = calculate_drag_coefficient(y_velocity / speed_of_sound)* LD_C  # Adjust based on Mach number for y-direction
        air_resistance_force_y = -0.5 * density * drag_coefficient_y * np.pi * (y_velocity**2)
        y_velocity += (abs(y_velocity)/y_velocity) * air_resistance_force_y * dt / mass  # Apply force as acceleration and update y-velocity

    return np.array([x_velocity, y_velocity])  # Return the updated velocity components


def calculate_drag_coefficient(mach_number):  # Replace with your implementation for calculating drag coefficient based on Mach number
    """
    This function is a placeholder. You should replace it with your actual implementation 
    to calculate the drag coefficient based on the Mach number.
    """
    # This is a simplified example, consider using lookup tables or more detailed models
    if mach_number <= 1:
        return 1.0  # Drag coefficient for subsonic speeds
    else:
        return 0.5  # Simplified drag coefficient for supersonic speeds (adjust based on data)




def apply_gravity(dt):
    global y_velocity
    y_velocity += MARS_GRAVITY * dt



def update_position(dt):
    global x_position, y_position
    x_position += x_velocity * dt
    y_position += y_velocity * dt


def draw_environment(screen):
    """
    Draws the Martian surface on the Pygame screen.

    You can customize this function to create a more visually appealing environment.
    Here are some suggestions:
        - Use an image for the Martian surface.
        - Draw a polygon with a gradient to represent the Martian terrain.
        - Add craters, rocks, and other Martian features (optional).
    """
    screen.fill(BLACK)  # Fill the background with black
    pygame.draw.rect(screen, RED, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))



# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mars Landing Simulation")
clock = pygame.time.Clock()

# Simulation loop
running = True
landed = False
crashed = False
# input()



while running:
    mass = spacecraft_mass + fuel_mass
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Add events for thrust control (e.g., keyboard presses)
        # You can replace `desired_thrust_x` and `desired_thrust_y` in `apply_thrust`
        # based on user input or control logic here

    keys_pressed = pygame.key.get_pressed()


    dt = clock.tick(60) / slower  # Time step in seconds
    # print(dt)
    # print(spacecraft_x, y_position)

    apply_gravity(dt)
    apply_air_resistance_v2(dt)

    # Example usage in the main loop
    keys_pressed = pygame.key.get_pressed()
    horizontal_thrust, vertical_thrust = handle_thrust_controls(keys_pressed)
    x_velocity += horizontal_thrust * dt
    y_velocity += vertical_thrust * dt

    apply_thrust(dt)
    update_position(dt)

    # Draw environment and spacecraft
    draw_environment(screen)
    spacecraft_x = int(x_position / SCALE)  # Convert x-position to screen coordinates
    spacecraft_y = SCREEN_HEIGHT - int(y_position / SCALE)  # Y-axis flipped for visual representation
    
    draw_spacecraft(screen, spacecraft_x, spacecraft_y,spacecraft_orientation)

    # Draw speed text on top of the spacecraft
    draw_speed_text(screen, spacecraft_x, spacecraft_y, x_velocity, y_velocity)


    # Check for landing or crash
    if y_position <= 500:  # Adjust based on landing area height
        if abs(y_velocity) < 20.0:  # Tolerable landing speed
            landed = True
            color = YELLOW
        else:
            crashed = True
            color = RED

    # Update display color based on landing/crash status
    if landed or crashed:
        screen.fill(color)  # Change background color

    # Display landing/crash message
    if landed:
        font = pygame.font.SysFont(None, 36)
        text = font.render("Successful Landing!", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    elif crashed:
        font = pygame.font.SysFont(None, 36)
        text = font.render("Crash Landing!", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)

    pygame.display.flip()  # Update the display

    # Exit the loop after landing or crash
    if landed or crashed:
        pygame.time.wait(3000)  # Wait for 3 seconds before quitting
        running = False

pygame.quit()

