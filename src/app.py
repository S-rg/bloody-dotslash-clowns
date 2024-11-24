import cv2
import numpy as np
from PIL import Image

import streamlit as st
from py3dbp import Packer, Bin, Item

from utils.plotly_utils import *
import detect_objects as dobj
from object_labeling import label_image



# Hold states of items and shelves
if "items" not in st.session_state:
    st.session_state["items"] = []
if "shelves" not in st.session_state:
    st.session_state["shelves"] = []


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

                    # Convert the uploaded file to an OpenCV image
                    top_file_bytes = np.asarray(bytearray(top_views[i].read()), dtype=np.uint8)
                    image_top = cv2.imdecode(top_file_bytes, cv2.IMREAD_COLOR)
                    front_file_bytes = np.asarray(bytearray(front_views[i].read()), dtype=np.uint8)
                    image_front = cv2.imdecode(front_file_bytes, cv2.IMREAD_COLOR)
                    
                    # Crop the image to the object and label it
                    cropped_image = dobj.crop_to_object(image_top)
                    item_name_val = label_image(cropped_image)

                    item_name = st.text_input(f"Item {i + 1} Name", value=item_name_val)
                    rotation = 1

                    # Reference object details for top view
                    st.subheader("Reference Object Details (Top View)")
                    ref_width = st.number_input(
                        f"Known Width of Reference Object (Item {i + 1})", value=5.5, step=0.1
                    )
                    ref_length = st.number_input(
                        f"Known Length of Reference Object (Item {i + 1})", value=5.5, step=0.1
                    )

                    st.divider()

                    # Reference object details for front view
                    st.subheader("Reference Object Details (Front View)")
                    ref_height = st.number_input(
                        f"Known Height of Reference Object (Item {i + 1})", value=5.5, step=0.1,
                    )

                   
                    
                    ref_real = [ref_height, ref_width, ref_length]
                    ref_px, obj_px = dobj.get_objects(image_top, image_front)
                    obj_real = dobj.get_real_dimensions(ref_px, obj_px, ref_real)

                    # Simply display the opencv computed values:
                    st.write(f"Reference dims (pixels): {ref_px}")
                    st.write(f"Reference dims (real-world): {ref_real} cm")
                    st.write(f"Object dims (pixels): {obj_px}")
                    st.write(f"Object dims (real-world): {obj_real} cm")


                    if st.button(f"Add Item {i + 1}"):
                        st.session_state["items"].append(
                            {"name": item_name, "rotation": rotation, "dimensions": obj_real}
                        )
                        st.success(f"Item '{item_name}' added with dimensions: {obj_real} and rotation {rotation}")

    # Upload shelf images
    #TODO: Add shelf detection and dimension calculation
    st.header("Shelves")

    # Add a checklist for default sizes or custom
    shelf_type = st.radio(
        "Select Shelf Type:",
        ["Small", "Medium", "Large", "Custom"],
        index=3,  # Default to "Custom"
    )

    if shelf_type != "Custom":
        # Predefined dimensions based on the selected size
        dimensions_shelf = {
            "Small": [10.0, 15.0, 10.0],
            "Medium": [30.0, 25.0, 10.0],
            "Large": [50.0, 40.0, 20.0],
        }[shelf_type]
        rotation = 0  # Default rotation for predefined shelves
        if st.button("Add Predefined Shelf"):
            st.session_state["shelves"].append({"rotation": rotation, "dimensions": dimensions_shelf})
            st.success(f"Predefined shelf added with dimensions: {dimensions_shelf} and rotation {rotation}")
    else:
        # Custom shelf configuration
        st.subheader("Upload Shelf Images")

        # File uploaders
        col1, col2 = st.columns(2)
        with col1:
            top_views_shelf = st.file_uploader(
                "Upload Top View Images (Shelves)", type=["jpg", "png"], accept_multiple_files=True, key="top_shelf"
            )
        with col2:
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
                # Separate section for each shelf
                for i in range(len(top_views_shelf)):
                    st.markdown(f"### Shelf {i + 1}: Configure Dimensions")
                    rotation = 0

                    col1, col2 = st.columns(2)

                    # Top view reference object details
                    with col1:
                        st.markdown("**Reference Object Details (Top View)**")
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

                    # Front view reference object details
                    with col2:
                        st.markdown("**Reference Object Details (Front View)**")
                        ref_height_shelf = st.number_input(
                            f"Known Height of Reference Object (Shelf {i + 1})", value=8.0, step=0.1
                        )
                        ref_size_px_front_shelf = st.number_input(
                            f"Pixel Size of Reference Object in Front View (Shelf {i + 1})", value=100.0, step=1.0
                        )

                        shelf_height_px = st.number_input(
                            f"Pixel Height of Shelf in Front View (Shelf {i + 1})", value=50.0, step=1.0
                        )

                    if st.button(f"Add Shelf {i + 1}", key=f"add_shelf_{i}"):
                        # Calculate dimensions
                        ref_dims_shelf = [ref_width_shelf, ref_length_shelf, ref_height_shelf]
                        ref_size_px_shelf = [
                            ref_size_px_top_shelf,
                            ref_size_px_top_shelf,
                            ref_size_px_front_shelf,
                        ]
                        shelf_size_px = [shelf_width_px, shelf_length_px, shelf_height_px]
                        dimensions_shelf = [
                            (dim * obj_px / ref_px)
                            for dim, obj_px, ref_px in zip(ref_dims_shelf, shelf_size_px, ref_size_px_shelf)
                        ]

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


elif page == "Visualization":
    st.title("Space Optimization Visualization")
    if not st.session_state["items"] or not st.session_state["shelves"]:
        st.warning("Please upload items and shelf dimensions first!")
    else:
        # Instantiate the packer
        packer = Packer()
        
        for shelf in st.session_state["shelves"]:
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

