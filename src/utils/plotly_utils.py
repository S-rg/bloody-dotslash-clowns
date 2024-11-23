import plotly.graph_objects as go
from decimal import Decimal
from typing import List, Tuple, Dict, Union

def create_cuboid(x: Union[float, Decimal], 
                 y: Union[float, Decimal], 
                 z: Union[float, Decimal],
                 dx: Union[float, Decimal], 
                 dy: Union[float, Decimal], 
                 dz: Union[float, Decimal], 
                 color: str) -> go.Mesh3d:
    """
    Create a 3D cuboid mesh using triangular faces.
    
    Args:
        x, y, z: Coordinates of the starting corner
        dx, dy, dz: Dimensions in x, y, z directions
        color: Color of the cuboid
    
    Returns:
        plotly.graph_objects.Mesh3d object
    """
    vertices = [
        [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z],
        [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]
    ]

    faces = [
        [0, 1, 2], [0, 2, 3],  # Bottom face
        [4, 5, 6], [4, 6, 7],  # Top face
        [0, 1, 5], [0, 5, 4],  # Front face
        [1, 2, 6], [1, 6, 5],  # Right face
        [2, 3, 7], [2, 7, 6],  # Back face
        [3, 0, 4], [3, 4, 7]   # Left face
    ]

    x_coords, y_coords, z_coords = zip(*vertices)
    
    return go.Mesh3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        i=[face[0] for face in faces],
        j=[face[1] for face in faces],
        k=[face[2] for face in faces],
        color=color,
        opacity=0.7
    )

def apply_rotation(size: Tuple[float, float, float], rotation: int) -> Tuple[float, float, float]:
    """
    Apply rotation to item dimensions.
    
    Args:
        size: Original dimensions (width, height, depth)
        rotation: Rotation type (0-5)
    
    Returns:
        Rotated dimensions
    """
    if rotation == 1:  # Rotate Height and Width
        return (size[1], size[0], size[2])
    elif rotation == 2:  # Rotate Height and Depth
        return (size[0], size[2], size[1])
    elif rotation == 3:  # Rotate Depth and Height
        return (size[2], size[0], size[1])
    elif rotation == 4:  # Rotate Depth and Width
        return (size[2], size[1], size[0])
    elif rotation == 5:  # Rotate Width and Depth
        return (size[1], size[2], size[0])
    return size

def create_packing_visualization(fitted_items: List[Dict], 
                               bin_size: Tuple[float, float, float],
                               colors: List[str]) -> List[go.Figure]:
    """
    Create sequential visualization frames for bin packing.
    
    Args:
        fitted_items: List of dictionaries containing item information
        bin_size: Dimensions of the container (width, height, depth)
        colors: List of colors for items
    
    Returns:
        List of plotly figures representing packing steps
    """
    frames = []
    for step, item in enumerate(fitted_items):
        fig = go.Figure()
        
        # Draw container
        fig.add_trace(create_cuboid(0, 0, 0, *bin_size, "lightgray"))
        
        # Add items up to current step
        for i in range(step + 1):
            pos = fitted_items[i]["position"]
            size = apply_rotation(fitted_items[i]["size"], fitted_items[i]["rotation"])
            
            fig.add_trace(create_cuboid(
                *map(Decimal, pos),
                *map(Decimal, size),
                colors[i]
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[0, bin_size[0]], title="Width"),
                yaxis=dict(range=[0, bin_size[1]], title="Height"),
                zaxis=dict(range=[0, bin_size[2]], title="Depth"),
            ),
            title=f"Step {step + 1}: Packing {item['name']}"
        )
        
        frames.append(fig)
    
    return frames


def parse_packer_output(packer) -> Tuple[List[Dict], Tuple[float, float, float]]:
    """
    Parse the bin packing data directly from a Packer object.
    
    Args:
        packer: Packer object containing bins with packed items
        
    Returns:
        Tuple containing:
            - List[Dict]: List of fitted items, each with keys:
                - name: str
                - size: Tuple[float, float, float]
                - position: Tuple[float, float, float]
                - rotation: int
            - Tuple[float, float, float]: Bin dimensions (width, height, depth)
    
    Example:
        packer = Packer()
        packer.add_bin(Bin('large-box', 8.0, 12.0, 5.5, 70.0))
        packer.add_item(Item('Item 1', 4, 2, 2, 1))
        packer.pack()
        fitted_items, bin_size = parse_packer_output(packer)
    """
    # Get the first bin (assuming single bin packing)
    bin = packer.bins[0]
    bin_size = (float(bin.width), float(bin.height), float(bin.depth))
    
    # Parse fitted items
    fitted_items = [
        {
            "name": item.name,
            "size": (float(item.width), float(item.height), float(item.depth)),
            "position": (float(item.position[0]), float(item.position[1]), float(item.position[2])),
            "rotation": int(item.rotation_type)
        }
        for item in bin.items
    ]
    
    return fitted_items, bin_size


if __name__ == "__main__":
    fitted_items = [
        {"name": "Item 1", "size": (4, 2, 2), "position": (0, 0, 0), "rotation": 0},
        {"name": "Item 2", "size": (4, 2, 2), "position": (4, 0, 0), "rotation": 0},
        {"name": "Item 3", "size": (4, 2, 2), "position": (0, 2, 0), "rotation": 0},
        {"name": "Item 4", "size": (8, 4, 2), "position": (4, 2, 0), "rotation": 1},
        {"name": "Item 5", "size": (8, 4, 2), "position": (0, 0, 2), "rotation": 0},
        {"name": "Item 6", "size": (8, 4, 2), "position": (0, 4, 2), "rotation": 0},
        {"name": "Item 7", "size": (8, 4, 2), "position": (0, 8, 2), "rotation": 0}
    ]
    bin_size = (8, 12, 5.5)
    colors = ["red", "blue", "green", "yellow", "orange", "purple", "cyan"]
    
    # Generate and display frames
    frames = create_packing_visualization(fitted_items, bin_size, colors)
    for fig in frames:
        fig.show()

