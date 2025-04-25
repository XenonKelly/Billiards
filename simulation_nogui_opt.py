import numpy as np
import csv
from numba import njit
import math

@njit
def update_positions(x, y, vx, vy, r, width, height, dt):
    n = len(x)
    for i in range(n):

        x[i] += vx[i] * dt
        y[i] += vy[i] * dt

        if x[i] - r[i] < 0:
            x[i] = r[i]
            vx[i] = -vx[i]
        elif x[i] + r[i] > width:
            x[i] = width - r[i]
            vx[i] = -vx[i]
        if y[i] - r[i] < 0:
            y[i] = r[i]
            vy[i] = -vy[i]
        elif y[i] + r[i] > height:
            y[i] = height - r[i]
            vy[i] = -vy[i]

@njit
def update_collisions(x, y, vx, vy, r, collisions_by_particle):
    n = len(x)
    particle_collisions = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            dy = y[j] - y[i]
            dist = math.sqrt(dx*dx + dy*dy)
            min_dist = r[i] + r[j]
            if dist < min_dist:
                if dist == 0:
                    continue  
                nx = dx / dist
                ny = dy / dist
                tx = -ny
                ty = nx
                v1n = vx[i]*nx + vy[i]*ny
                v2n = vx[j]*nx + vy[j]*ny
                v1t = vx[i]*tx + vy[i]*ty
                v2t = vx[j]*tx + vy[j]*ty

                vx[i] = v2n * nx + v1t * tx
                vy[i] = v2n * ny + v1t * ty
                vx[j] = v1n * nx + v2t * tx
                vy[j] = v1n * ny + v2t * ty

                overlap = min_dist - dist
                x[i] -= overlap * nx / 2.0
                y[i] -= overlap * ny / 2.0
                x[j] += overlap * nx / 2.0
                y[j] += overlap * ny / 2.0

                particle_collisions += 1
                collisions_by_particle[i] += 1
                collisions_by_particle[j] += 1
    return particle_collisions

@njit
def count_wall_collisions(x, y, r, width, height, collisions_by_particle):
    wall_collisions = 0
    n = len(x)
    for i in range(n):
        if (x[i] - r[i] < 1 or x[i] + r[i] > width - 1 or
            y[i] - r[i] < 1 or y[i] + r[i] > height - 1):
            wall_collisions += 1
            collisions_by_particle[i] = 0
    return wall_collisions

@njit
def run_simulation_numba(x, y, vx, vy, r, width, height, dt, total_steps, output_interval):
    stats_steps = total_steps // output_interval
    stats = np.empty((stats_steps, 5), dtype=np.float64)  
    stats_index = 0
    particle_collisions = 0
    wall_collisions = 0
    collisions_by_particle = np.zeros(num_particles, dtype=np.int64)
    collided_number = np.zeros(num_particles + 1, dtype=np.int64)

    for step in range(1, total_steps + 1):
        update_positions(x, y, vx, vy, r, width, height, dt)
        particle_collisions += update_collisions(x, y, vx, vy, r, collisions_by_particle)
        wall_collisions += count_wall_collisions(x, y, r, width, height, collisions_by_particle)
        if(step > 10000):
            collided_number[np.count_nonzero(collisions_by_particle)] += 1
        # if step % output_interval == 0:
        #     current_time = step * dt
        #     total = particle_collisions + wall_collisions
        #     ratio = (particle_collisions / total * 100) if total > 0 else 0.0
        #     stats[stats_index, 0] = current_time
        #     stats[stats_index, 1] = particle_collisions
        #     stats[stats_index, 2] = wall_collisions
        #     stats[stats_index, 3] = total
        #     stats[stats_index, 4] = ratio
        #     stats_index += 1
    print(collided_number)
    return stats

print("Running...")

width = 800
height = 600
num_particles = 10
radius = 20
mass = 1.0   
speed_range = [50, 100]
dt = 0.01
total_steps = 100000
output_interval = 1000

n = num_particles
r_arr = np.full(n, radius, dtype=np.float64)
x_arr = np.random.uniform(radius, width - radius, n)
y_arr = np.random.uniform(radius, height - radius, n)
speeds = np.random.uniform(speed_range[0], speed_range[1], n)
angles = np.random.uniform(0, 2*np.pi, n)
vx_arr = speeds * np.cos(angles)
vy_arr = speeds * np.sin(angles)

stats = run_simulation_numba(x_arr, y_arr, vx_arr, vy_arr, r_arr,
                                width, height, dt, total_steps, output_interval)

# output_file = "simulation_stats.csv"
# with open(output_file, "w", newline="") as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(["Time (s)", "Particle Collisions", "Wall Collisions", "Total Collisions", "Collision Ratio (%)"])
#     for row in stats:
#         writer.writerow(row)

# print("Simulation complete. Statistics written to", output_file)