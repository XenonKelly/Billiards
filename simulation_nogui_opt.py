import os
import numpy as np
from numba import njit
import math
from distribution import plot_collision_distribution
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

@njit
def update_positions(x, y, vx, vy, r, width, height, dt):
    n = len(x)
    for i in range(n):
        x[i] += vx[i] * dt
        y[i] += vy[i] * dt
        if x[i] - r[i] < 0:
            x[i], vx[i] = r[i], -vx[i]
        elif x[i] + r[i] > width:
            x[i], vx[i] = width - r[i], -vx[i]
        if y[i] - r[i] < 0:
            y[i], vy[i] = r[i], -vy[i]
        elif y[i] + r[i] > height:
            y[i], vy[i] = height - r[i], -vy[i]

@njit
def update_collisions(x, y, vx, vy, r, collisions_by_particle):
    n = len(x)
    particle_collisions = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]; dy = y[j] - y[i]
            dist = math.hypot(dx, dy)
            min_dist = r[i] + r[j]
            if dist < min_dist and dist > 0:
                nx, ny = dx/dist, dy/dist
                tx, ty = -ny, nx
                v1n = vx[i]*nx + vy[i]*ny
                v2n = vx[j]*nx + vy[j]*ny
                v1t = vx[i]*tx + vy[i]*ty
                v2t = vx[j]*tx + vy[j]*ty
                vx[i] = v2n*nx + v1t*tx
                vy[i] = v2n*ny + v1t*ty
                vx[j] = v1n*nx + v2t*tx
                vy[j] = v1n*ny + v2t*ty
                overlap = min_dist - dist
                x[i] -= overlap * nx * 0.5
                y[i] -= overlap * ny * 0.5
                x[j] += overlap * nx * 0.5
                y[j] += overlap * ny * 0.5
                particle_collisions += 1
                collisions_by_particle[i] += 1
                collisions_by_particle[j] += 1
    return particle_collisions

@njit
def count_wall_collisions(x, y, r, width, height, collisions_by_particle):
    wall_collisions = 0
    n = len(x)
    for i in range(n):
        if x[i] - r[i] < 1 or x[i] + r[i] > width - 1 or y[i] - r[i] < 1 or y[i] + r[i] > height - 1:
            wall_collisions += 1
            collisions_by_particle[i] = 0
    return wall_collisions

@njit
def run_simulation_numba(x, y, vx, vy, r, width, height, dt, total_steps):
    n = len(x)
    collisions_by_particle = np.zeros(n, dtype=np.int64)
    collided_number = np.zeros(n + 1, dtype=np.int64)
    for step in range(1, total_steps + 1):
        update_positions(x, y, vx, vy, r, width, height, dt)
        update_collisions(x, y, vx, vy, r, collisions_by_particle)
        count_wall_collisions(x, y, r, width, height, collisions_by_particle)
        if step > 10000:
            collided_number[np.count_nonzero(collisions_by_particle)] += 1
    return collided_number

def main():

    width, height = 806, 607
    radius = 10.0
    speed_range = (1.0, 100)
    dt = 0.01
    total_steps = 1_000_000

    os.makedirs('experiments', exist_ok=True)

    for num_particles in range(1, 30):

        n = num_particles
        r_arr = np.full(n, radius, dtype=np.float64)
        x_arr = np.random.uniform(radius, width - radius, n)
        y_arr = np.random.uniform(radius, height - radius, n)
        speeds = np.random.uniform(speed_range[0], speed_range[1], n)
        angles = np.random.uniform(0, 2*np.pi, n)
        vx_arr = speeds * np.cos(angles)
        vy_arr = speeds * np.sin(angles)

        collided_number = run_simulation_numba(
            x_arr.copy(), y_arr.copy(),
            vx_arr.copy(), vy_arr.copy(),
            r_arr, width, height, dt, total_steps
        )

        plt.figure()
        plot_collision_distribution(collided_number)
        filename = f'experiments/1/{num_particles}b.png'
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f'Сохранено: {filename}')
        

if __name__ == '__main__':
    main()