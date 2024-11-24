from scipy.spatial import distance as dist
from imutils import perspective
import numpy as np
import imutils
import cv2
from PIL import Image

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def normalize_dimensions(object_dims, reference_dims):
    """
    Normalize object dimensions based on the reference object's dimensions.

    Args:
        object_dims (tuple): Dimensions of the object.
        reference_dims (tuple): Dimensions of the reference object.

    Returns:
        tuple: Normalized dimensions.
    """
    return tuple(dim / reference_dims[0] for dim in object_dims)

def get_3d_dimensions(top_dims, front_dims):
    """
    Match dimensions from top-down and front views to calculate 3D dimensions.

    Args:
        top_dims (tuple): Dimensions from the top-down view.
        front_dims (tuple): Dimensions from the front view.

    Returns:
        tuple: Calculated 3D dimensions.
    """
    for t_dim in top_dims:
        for f_dim in front_dims:
            if abs(top_dims[0] - f_dim) < 0.2 * t_dim:  # Allowable tolerance
                return tuple(sorted([top_dims[0], top_dims[1], front_dims[0] if f_dim == front_dims[1] else front_dims[1]]))
    return None

def get_real_dimensions(reference_img_dims, object_dims, input_dims):
    """
    Calculate real-world dimensions using normalized dimensions.

    Args:
        reference_img_dims (tuple): Dimensions of the reference object in pixels.
        object_dims (tuple): Dimensions of the measured object in pixels.
        input_dims (tuple): Real-world dimensions of the reference object.

    Returns:
        tuple: Real-world dimensions of the object.
    """
    scale_factors = [input_dims[i] / reference_img_dims[i] for i in range(3)]
    return tuple(scale_factors[i] * object_dims[i] for i in range(3))

def get_dims(image):
    """
    Extract dimensions of the two largest objects in the image.

    Args:
        image (numpy.ndarray): Input image.

    Returns:
        list: List of tuples containing dimensions and centroid x-coordinate.
    """
    dims = []
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grey, (25, 25), 0)
    illumination_corrected = cv2.divide(grey, blurred, scale=255)
    illumination_corrected = cv2.GaussianBlur(illumination_corrected, (7, 7), 0)

    edged = cv2.Canny(illumination_corrected, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:2]

    for c in cnts:
        box = cv2.minAreaRect(c)
        box = cv2.boxPoints(box) if imutils.is_cv3() else cv2.boxPoints(box)
        box = perspective.order_points(box)

        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"] if M["m00"] != 0 else 0)
        dims.append((dA, dB, cX))

        # Draw the bounding box on the original image
        cv2.drawContours(image, [box.astype("int")], -1, (0, 255, 0), 2)

        # Optional: Annotate dimensions
        cv2.putText(
            image,
            f"{dA:.1f}px",
            (int(tl[0]), int(tl[1] - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
        cv2.putText(
            image,
            f"{dB:.1f}px",
            (int(tr[0] + 10), int(tr[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        # Show the image with bounding boxes
        Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).show()


    dims.sort(key=lambda x: x[2])  # Sort by x-coordinate of the centroid
    return dims

def get_objects(im_td, im_side):
    """
    Calculate 3D dimensions of objects using top-down and side view images.

    Args:
        im_td (numpy.ndarray): Top-down view image.
        im_side (numpy.ndarray): Side view image.

    Returns:
        tuple: Dimensions of the reference and the measured object.
    """
    td_dims = get_dims(im_td)
    side_dims = get_dims(im_side)

    reference_td = td_dims[1]  # Rightmost object in top-down view
    object_td = td_dims[0]

    reference_side = side_dims[1]  # Rightmost object in side view
    object_side = side_dims[0]

    reference_dims = get_3d_dimensions(reference_td[:2], reference_side[:2])
    object_dims = get_3d_dimensions(object_td[:2], object_side[:2])

    return reference_dims, object_dims

if __name__ == "__main__":
    image_top = cv2.imread("/Users/suraj/Downloads/bloody-dotslash-clowns/assets/megaminx_top.jpeg")
    image_front = cv2.imread("/Users/suraj/Downloads/bloody-dotslash-clowns/assets/megaminx_front.jpeg")

    ref, obj = get_objects(image_top, image_front)
    print(f"Reference dims (normalized): {ref}")
    print(f"Object dims (normalized): {obj}")

    real_reference_dims = (5.5, 5.5, 5.5)  # Example real-world reference dimensions
    real_obj_dims = get_real_dimensions(ref, obj, real_reference_dims)

    print(f"Reference dims (real-world): {real_reference_dims} cm")
    print(f"Object dims (real-world): {real_obj_dims} cm")
