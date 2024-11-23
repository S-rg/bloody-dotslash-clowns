import streamlit as st
from py3dbp import Packer, Bin, Item
from PIL import Image
import numpy as np
import utils.plotly_utils

# Now imports will work
from utils.plotly_utils import *
# Hold states of items and shelves
if "items" not in st.session_state:
    st.session_state["items"] = []
if "shelves" not in st.session_state:
    st.session_state["shelves"] = []

# TODO: Replace this function with OpenCV Object Detection and Measurement
# Function to calculate dimensions using a reference object
def calculate_dimensions(reference_dim, ref_size_px, obj_size_px):
    if not (len(reference_dim) == len(ref_size_px) == len(obj_size_px)):
        raise ValueError("All input lists must have the same length (width, length, height).")
    return [dim * obj_px / ref_px for dim, obj_px, ref_px in zip(reference_dim, obj_size_px, ref_size_px)]

# Define pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Visualization"])

if page == "Home":
    st.title("Upload Images and Configure Dimensions")

    # Upload item images
    st.header("Items")
    with st.expander("Upload Item Images"):
        top_views = st.file_uploader(
            "Upload Top View Images (Items)", type=["jpg", "png"], accept_multiple_files=True, key="top_item"
        )
        front_views = st.file_uploader(
            "Upload Front View Images (Items)", type=["jpg", "png"], accept_multiple_files=True, key="front_item"
        )

        if top_views and front_views:
            st.write("Uploaded Top View Images:")
            st.image(top_views, caption=["Top View" for _ in top_views], use_container_width=True)
            st.write("Uploaded Front View Images:")
            st.image(front_views, caption=["Front View" for _ in front_views], use_container_width=True)

            if len(top_views) != len(front_views):
                st.error("The number of top view and front view images must match.")
            else:
                for i in range(len(top_views)):
                    st.subheader(f"Item {i + 1}: Configure Dimensions")
                    item_name = st.text_input(f"Item {i + 1} Name", value=f"Item {i + 1}")
                    rotation = 0

                    # Reference object details for top view
                    st.subheader("Reference Object Details (Top View)")
                    ref_width = st.number_input(
                        f"Known Width of Reference Object (Item {i + 1})", value=5.5, step=0.1
                    )
                    ref_length = st.number_input(
                        f"Known Length of Reference Object (Item {i + 1})", value=5.5, step=0.1
                    )

                    # TODO: Get these from OpenCV
                    ref_size_px_top = 100
                    obj_width_px = 100
                    obj_length_px = 100

                    # Reference object details for front view
                    st.subheader("Reference Object Details (Front View)")
                    ref_height = st.number_input(
                        f"Known Height of Reference Object (Item {i + 1})", value=5.5, step=0.1,
                    )
                    ref_size_px_front = st.number_input(
                        f"Pixel Size of Reference Object in Front View (Item {i + 1})", value=100.0, step=1.0
                    )
                    st.divider()

                    obj_height_px = st.number_input(
                        f"Pixel Height of Object in Front View (Item {i + 1})", value=50.0, step=1.0
                    )

                    if st.button(f"Add Item {i + 1}"):
                        # Calculate dimensions
                        ref_dims = [ref_width, ref_length, ref_height]
                        ref_size_px = [ref_size_px_top, ref_size_px_top, ref_size_px_front]
                        obj_size_px = [obj_width_px, obj_length_px, obj_height_px]
                        dimensions = calculate_dimensions(ref_dims, ref_size_px, obj_size_px)

                        st.session_state["items"].append(
                            {"name": item_name, "rotation": rotation, "dimensions": dimensions}
                        )
                        st.success(f"Item '{item_name}' added with dimensions: {dimensions} and rotation {rotation}")

    # Upload shelf images
    st.header("Shelves")
    with st.expander("Upload Shelf Images"):
        top_views_shelf = st.file_uploader(
            "Upload Top View Images (Shelves)", type=["jpg", "png"], accept_multiple_files=True, key="top_shelf"
        )
        front_views_shelf = st.file_uploader(
            "Upload Front View Images (Shelves)", type=["jpg", "png"], accept_multiple_files=True, key="front_shelf"
        )

        if top_views_shelf and front_views_shelf:
            st.write("Uploaded Top View Images (Shelves):")
            st.image(top_views_shelf, caption=["Top View (Shelf)" for _ in top_views_shelf], use_container_width=True)
            st.write("Uploaded Front View Images (Shelves):")
            st.image(front_views_shelf, caption=["Front View (Shelf)" for _ in front_views_shelf], use_container_width=True)

            if len(top_views_shelf) != len(front_views_shelf):
                st.error("The number of top view and front view images for shelves must match.")
            else:
                for i in range(len(top_views_shelf)):
                    st.subheader(f"Shelf {i + 1}: Configure Dimensions")
                    rotation = 0

                    # Reference object details for top view
                    st.subheader("Reference Object Details (Top View - Shelf)")
                    ref_width_shelf = st.number_input(
                        f"Known Width of Reference Object (Shelf {i + 1})", value=25.0, step=0.1
                    )
                    ref_length_shelf = st.number_input(
                        f"Known Length of Reference Object (Shelf {i + 1})", value=15.0, step=0.1
                    )
                    ref_size_px_top_shelf = st.number_input(
                        f"Pixel Size of Reference Object in Top View (Shelf {i + 1})", value=100.0, step=1.0
                    )

                    shelf_width_px = st.number_input(
                        f"Pixel Width of Shelf in Top View (Shelf {i + 1})", value=50.0, step=1.0
                    )
                    shelf_length_px = st.number_input(
                        f"Pixel Length of Shelf in Top View (Shelf {i + 1})", value=50.0, step=1.0
                    )

                    # Reference object details for front view
                    st.subheader("Reference Object Details (Front View - Shelf)")
                    ref_height_shelf = st.number_input(
                        f"Known Height of Reference Object (Shelf {i + 1})", value=8.0, step=0.1
                    )
                    ref_size_px_front_shelf = st.number_input(
                        f"Pixel Size of Reference Object in Front View (Shelf {i + 1})", value=100.0, step=1.0
                    )

                    shelf_height_px = st.number_input(
                        f"Pixel Height of Shelf in Front View (Shelf {i + 1})", value=50.0, step=1.0
                    )

                    if st.button(f"Add Shelf {i + 1}"):
                        # Calculate dimensions
                        ref_dims_shelf = [ref_width_shelf, ref_length_shelf, ref_height_shelf]
                        ref_size_px_shelf = [
                            ref_size_px_top_shelf,
                            ref_size_px_top_shelf,
                            ref_size_px_front_shelf,
                        ]
                        shelf_size_px = [shelf_width_px, shelf_length_px, shelf_height_px]
                        dimensions_shelf = calculate_dimensions(ref_dims_shelf, ref_size_px_shelf, shelf_size_px)

                        st.session_state["shelves"].append(
                            {"rotation": rotation, "dimensions": dimensions_shelf}
                        )
                        st.success(f"Shelf added with dimensions: {dimensions_shelf} and rotation {rotation}")

    # Display current items and shelves
    st.write("Current Items:")
    for item in st.session_state["items"]:
        items = st.write(f"- {item['name']}: {item['dimensions']}")

    st.write("Current Shelves:")
    for shelf in st.session_state["shelves"]:
        shelves = st.write(f"- Shelf with dimensions {shelf['dimensions']}")

    # TODO: Implement deleting and updating the list functionality


elif page == "Visualization":
    st.title("Space Optimization Visualization")
    if not st.session_state["items"] or not st.session_state["shelves"]:
        st.warning("Please upload items and shelf dimensions first!")
    else:
        # Instantiate the packer
        packer = Packer()
        
        # Add the shelf as a bin
        shelf = st.session_state["shelves"][0]  # Assuming first shelf for now
        packer.add_bin(Bin('shelf', 
                          width=float(shelf['dimensions'][0]), 
                          height=float(shelf['dimensions'][1]), 
                          depth=float(shelf['dimensions'][2]), 
                          max_weight=10000)
        )
        
        # Add items to be packed
        for item in st.session_state["items"]:
            packer.add_item(Item(
                name=item['name'],
                width=float(item['dimensions'][0]),
                height=float(item['dimensions'][1]),
                depth=float(item['dimensions'][2]),
                weight=1
            ))

        packer.pack()
        fitted_items, bin_size = parse_packer_output(packer)

        # Visualize the packing
        colors = ["red", "blue", "green", "yellow", "orange", "purple", "cyan"]
        frames = create_packing_visualization(fitted_items, bin_size, colors)
        for fig in frames:
            st.plotly_chart(fig)

