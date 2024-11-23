import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Rotation Type Definitions
class RotationType:
    RT_WHD = 0
    RT_HWD = 1
    RT_HDW = 2
    RT_DHW = 3
    RT_DWH = 4
    RT_WDH = 5

    ALL = [RT_WHD, RT_HWD, RT_HDW, RT_DHW, RT_DWH, RT_WDH]

# Function to apply rotation to dimensions
def apply_rotation(size, rotation):
    width, height, depth = size
    if rotation == RotationType.RT_WHD:
        return [width, height, depth]
    elif rotation == RotationType.RT_HWD:
        return [height, width, depth]
    elif rotation == RotationType.RT_HDW:
        return [height, depth, width]
    elif rotation == RotationType.RT_DHW:
        return [depth, height, width]
    elif rotation == RotationType.RT_DWH:
        return [depth, width, height]
    elif rotation == RotationType.RT_WDH:
        return [width, depth, height]

# Dimensions of the large box
box_dimensions = [8.0, 12.0, 5.5]

# Fitted items (position [x, y, z], size [width, height, depth], rotation)
fitted_items = [
    {"name": "powder 1", "pos": [0, 0, 0], "size": [3.937, 1.968, 1.968], "rotation": RotationType.RT_WHD},
    {"name": "powder 2", "pos": [3.937, 0, 0], "size": [3.937, 1.968, 1.968], "rotation": RotationType.RT_WHD},
    {"name": "powder 3", "pos": [0, 1.968, 0], "size": [3.937, 1.968, 1.968], "rotation": RotationType.RT_WHD},
    {"name": "powder 4", "pos": [3.937, 1.968, 0], "size": [7.874, 3.937, 1.968], "rotation": RotationType.RT_HWD},
    {"name": "powder 5", "pos": [0, 0, 1.968], "size": [7.874, 3.937, 1.968], "rotation": RotationType.RT_WHD},
    {"name": "powder 6", "pos": [0, 3.937, 1.968], "size": [7.874, 3.937, 1.968], "rotation": RotationType.RT_WHD},
    {"name": "powder 7", "pos": [0, 7.874, 1.968], "size": [7.874, 3.937, 1.968], "rotation": RotationType.RT_WHD},
]

# Function to draw a cuboid
def draw_cuboid(ax, position, size, rotation, color, alpha=0.6, label=None):
    size = apply_rotation(size, rotation)  # Apply rotation to the dimensions
    x, y, z = position
    dx, dy, dz = size
    vertices = [
        [x, y, z],
        [x + dx, y, z],
        [x + dx, y + dy, z],
        [x, y + dy, z],
        [x, y, z + dz],
        [x + dx, y, z + dz],
        [x + dx, y + dy, z + dz],
        [x, y + dy, z + dz],
    ]
    faces = [
        [vertices[j] for j in [0, 1, 5, 4]],
        [vertices[j] for j in [1, 2, 6, 5]],
        [vertices[j] for j in [2, 3, 7, 6]],
        [vertices[j] for j in [3, 0, 4, 7]],
        [vertices[j] for j in [0, 1, 2, 3]],
        [vertices[j] for j in [4, 5, 6, 7]],
    ]
    poly3d = Poly3DCollection(faces, alpha=alpha, edgecolor="black")
    poly3d.set_facecolor(color)
    ax.add_collection3d(poly3d)
    if label:
        ax.text(x + dx / 2, y + dy / 2, z + dz / 2, label, color="black")

# Create the plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

# Draw the large box
draw_cuboid(ax, [0, 0, 0], box_dimensions, RotationType.RT_WHD, color="lightblue", alpha=0.1, label="Container")

# Draw fitted items
colors = plt.cm.tab20.colors
for i, item in enumerate(fitted_items):
    draw_cuboid(ax, item["pos"], item["size"], item["rotation"], color=colors[i % len(colors)], label=item["name"])

# Set labels and limits
ax.set_xlabel("Width")
ax.set_ylabel("Height")
ax.set_zlabel("Depth")
ax.set_xlim(0, box_dimensions[0])
ax.set_ylim(0, box_dimensions[1])
ax.set_zlim(0, box_dimensions[2])
ax.set_title("3D Bin Packing Visualization with Rotations")
ax.legend()

# Show plot
plt.show()
