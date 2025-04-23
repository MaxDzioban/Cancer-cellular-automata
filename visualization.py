"""visualize process of tumor growth"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap
from cells import Cell
from grid import Grid

def initialize_tumor(grid, center_x, center_y, initial_radius=3):
    """Initialize tumor cells in a circular pattern at the center."""
    for i in range(grid.rows):
        for j in range(grid.cols):
            # Calculate distance from center
            distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            # Create cells within the initial radius
            if distance <= initial_radius:
                cell = Cell((i, j))
                grid.add_cell(cell)

def update(frame_num, grid, img):
    """Update function for animation."""
    # Make actions for all cells
    grid.make_action()
    
    # Update the grid visualization
    grid_array = grid.grid.astype(int)
    img.set_array(grid_array)
    
    # Add a title with the current frame and cell count
    plt.title(f"Tumor Growth Simulation - Step: {frame_num}, Cells: {grid.num_cells}")
    
    return [img]

def visualize_tumor_growth(grid_size=50, num_frames=100, fps=10):
    """Create and display animation of tumor growth."""
    # Set cell behavior rates
    Cell.set_rates(apoptosis=0.01, proliferation=0.3, migration=0.2)
    
    # Initialize grid
    grid = Grid(grid_size, grid_size)
    center = grid_size // 2
    initialize_tumor(grid, center, center)
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = ListedColormap(['white', 'red'])
    img = ax.imshow(grid.grid.astype(int), cmap=cmap, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Tumor Growth Simulation - Step: 0, Cells: {}".format(grid.num_cells))
    
    # Create the animation
    anim = animation.FuncAnimation(
        fig, update, frames=num_frames, fargs=(grid, img),
        interval=1000//fps, blit=True
    )
    
    # Display or save the animation
    plt.tight_layout()
    
    # To save as MP4 file (requires ffmpeg):
    # anim.save('tumor_growth.mp4', fps=fps, extra_args=['-vcodec', 'libx264'])
    anim.save('tumor_growth.gif', writer='pillow', fps=fps)
    # plt.show()
    
    return anim

if __name__ == "__main__":
    # Run the visualization with default parameters
    visualize_tumor_growth(grid_size=50, num_frames=30, fps=15)