import pygame
import pygame_gui
import numpy as np
import random
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-gui', action='store_true', help='Run simulation without GUI')
args = parser.parse_args()


class Particle:
    def __init__(self, x, y, radius, mass, speed_range, id):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.speed = random.uniform(speed_range[0], speed_range[1])
        self.angle = random.uniform(0, 2 * np.pi)
        self.vx = self.speed * np.cos(self.angle)
        self.vy = self.speed * np.sin(self.angle)
        self.id = id

    def update(self, dt, width, height):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        if self.x + self.radius > width:
            self.x = width - self.radius
            self.vx *= -1
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
        if self.y + self.radius > height:
            self.y = height - self.radius
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

def collide_particles(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dist = np.sqrt(dx**2 + dy**2)
    min_dist = p1.radius + p2.radius

    if dist < min_dist: 
        if dist == 0:
            return False  

        nx, ny = dx / dist, dy / dist  

        tx, ty = -ny, nx  
        v1n = p1.vx * nx + p1.vy * ny 
        v2n = p2.vx * nx + p2.vy * ny

        v1t = p1.vx * tx + p1.vy * ty  
        v2t = p2.vx * tx + p2.vy * ty

        p1.vx = v2n * nx + v1t * tx
        p1.vy = v2n * ny + v1t * ty
        p2.vx = v1n * nx + v2t * tx
        p2.vy = v1n * ny + v2t * ty

        overlap = min_dist - dist
        p1.x -= overlap * nx / 2
        p1.y -= overlap * ny / 2
        p2.x += overlap * nx / 2
        p2.y += overlap * ny / 2

        return True
    return False

def create_particles(num_particles, radius, mass, speed_range, width, height):
    particles = []
    for i in range(num_particles):
        x = random.uniform(radius, width - radius)
        y = random.uniform(radius, height - radius)
        new_particle = Particle(x, y, radius, mass, speed_range, id=i)

        overlap = False
        for p in particles:
            dx = new_particle.x - p.x
            dy = new_particle.y - p.y
            dist = np.sqrt(dx**2 + dy**2)
            if dist < new_particle.radius + p.radius:
                overlap = True
                break

        if not overlap:
            particles.append(new_particle)
    return particles


def main(no_gui=False):
    heating_iterations = 2000
    counter_heating = 0

    width = 800
    height = 600
    num_particles = 10
    radius = 10
    mass = 1
    speed_range = [300, 350]
    aspect_ratio = 1.33

    if no_gui:
        print("Running in headless (no-GUI) mode...")

        particles = create_particles(num_particles, radius, mass, speed_range, width, height)
        sim_time = 100000  # общее число шагов времени
        dt = 0.01  # шаг по времени
        particle_collisions = 0
        wall_collisions = 0

        output_file = "simulation_stats.csv"
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time (s)", "Particle Collisions", "Wall Collisions", "Total Collisions", "Collision Ratio (%)"])

            for step in range(1, sim_time + 1):
                for p in particles:
                    p.update(dt, width, height)

                for i in range(len(particles)):
                    for j in range(i + 1, len(particles)):
                        if collide_particles(particles[i], particles[j]):
                            particle_collisions += 1

                for p in particles:
                    if (p.x - p.radius < 1 or p.x + p.radius > width - 1 or
                        p.y - p.radius < 1 or p.y + p.radius > height - 1):
                        wall_collisions += 1

                if step % 100 == 0:
                    current_time = step * dt
                    total_collisions = particle_collisions + wall_collisions
                    ratio = (particle_collisions / total_collisions * 100) if total_collisions > 0 else 0
                    writer.writerow([f"{current_time:.2f}", particle_collisions, wall_collisions, total_collisions, f"{ratio:.2f}"])

        print("Simulation complete.")
        return

    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Molecular Gas Simulation")

    manager = pygame_gui.UIManager((width, height))

    num_particles_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10), (150, 20)),
                                                    text="Number of Particles:", manager=manager)
    num_particles_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170, 10), (50, 20)),
                                                              manager=manager)
    num_particles_entry.set_text(str(num_particles))

    radius_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 40), (100, 20)),
                                            text="Radius:", manager=manager)
    radius_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120, 40), (50, 20)),
                                                      manager=manager)
    radius_entry.set_text(str(radius))

    mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 70), (100, 20)),
                                          text="Mass:", manager=manager)
    mass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120, 70), (50, 20)),
                                                    manager=manager)
    mass_entry.set_text(str(mass))

    speed_range_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 100), (150, 20)),
                                                 text="Speed Range (min,max):", manager=manager)
    speed_range_min_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170, 100), (50, 20)),
                                                                manager=manager)
    speed_range_min_entry.set_text(str(speed_range[0]))
    speed_range_max_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((230, 100), (50, 20)),
                                                                manager=manager)
    speed_range_max_entry.set_text(str(speed_range[1]))

    aspect_ratio_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 130), (150, 20)),
                                                 text="Aspect Ratio:", manager=manager)
    aspect_ratio_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170, 130), (50, 20)),
                                                              manager=manager)
    aspect_ratio_entry.set_text(str(aspect_ratio))

    update_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 160), (150, 30)),
                                                 text="Update Parameters", manager=manager)

    collision_count_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 200), (200, 20)),
                                                        text="Particle Collisions: 0", manager=manager)
    wall_collision_count_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 230), (200, 20)),
                                                             text="Wall Collisions: 0", manager=manager)

    particles = create_particles(num_particles, radius, mass, speed_range, width, height)
    particle_collisions = 0
    wall_collisions = 0
    collisions_by_particle = np.zeros(num_particles)
    collided_number = np.zeros(num_particles + 1)

    clock = pygame.time.Clock()
    running = True

    while running:
        counter_heating += 1
        time_delta = clock.tick(60) / 1000.0
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == update_button:
                        try:
                            heating_iterations = 2000
                            counter_heating = 0
                            num_particles = int(num_particles_entry.get_text())
                            radius = float(radius_entry.get_text())
                            mass = float(mass_entry.get_text())
                            speed_range = [float(speed_range_min_entry.get_text()), float(speed_range_max_entry.get_text())]
                            aspect_ratio = float(aspect_ratio_entry.get_text())

                            width = 800  
                            height = int(width / aspect_ratio)
                            screen = pygame.display.set_mode((width, height))

                            particles = create_particles(num_particles, radius, mass, speed_range, width, height)
                            particle_collisions = 0
                            wall_collisions = 0
                            collisions_by_particle = np.zeros(num_particles)
                            collided_number = np.zeros(num_particles)
                        except ValueError:
                            print("Invalid input. Please enter numbers.")

            manager.process_events(event)

        for i, p1 in enumerate(particles):
            p1.update(time_delta, width, height)
            p1.draw(screen)

        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):
                if collide_particles(particles[i], particles[j]):
                    particle_collisions += 1
                    collisions_by_particle[i] += 1
                    collisions_by_particle[j] += 1

        for p in particles:
            if (p.x - p.radius < 1 or p.x + p.radius > width - 1 or
                p.y - p.radius < 1 or p.y + p.radius > height - 1):
                wall_collisions += 1
                collisions_by_particle[p.id] = 0

        collision_count_label.set_text(f"Particle Collisions: {particle_collisions}")
        wall_collision_count_label.set_text(f"Wall Collisions: {wall_collisions}")

        if counter_heating <= heating_iterations:
            time_delta *= 5  
            
        if counter_heating > heating_iterations:
            collided_number[np.count_nonzero(collisions_by_particle)] += 1
            print(collided_number, counter_heating, sep=",")
        else:
            pass 

        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main(no_gui=args.no_gui)


