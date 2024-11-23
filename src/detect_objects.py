from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2
from PIL import Image

def midpoint(ptA, ptB):
    """
    Calculates the midpoint between two 2D points.

    Args:
    ptA/ptB (tuple[2]): 2D coordinates
    """
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def get_3_dim_from_dims(dim1, dim2, tolerance=100):
    """
    Finds the real world 3D dimensions of the object, based on 2D dimensions taken from top-down view and side view

    Args:
        dim1 (tuple): A tuple of two dimensions (e.g., height and width) for the first object.
        dim2 (tuple): A tuple of two dimensions for the second object.
        tolerance (int): The allowable difference between matching dimensions.

    Returns:
        tuple: A tuple of three dimensions if a match is found; otherwise, None.
    """
    for d1 in dim1:
        for d2 in dim2:
            if abs(d1 - d2) <= tolerance:
                return (dim1[0], dim1[1], dim2[0] if d2 == dim2[1] else dim2[1])
    return None



def get_dims(image):
    """
    Finds the 2 largest objects in an image and gets its dimensions

    Args:
        image (numpy.ndarray): Input image (BGR format)

    Returns:
        list of 2 tuples containing:
            - dA (float): Height of the object in image
            - dB (float): Width of the object in image
            - cX (int): x-coordinate of the centroid of the object in the image
    """
    dims = []

    #removing noise
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grey, (25, 25), 0)
    illumination_corrected = cv2.divide(grey, blurred, scale=255)
    illumination_corrected = cv2.GaussianBlur(illumination_corrected, (7, 7), 0)
    denoised = cv2.bilateralFilter(illumination_corrected, d=9, sigmaColor=75, sigmaSpace=75)
    #Image.fromarray(denoised).show()

    #edge detection
    edged = cv2.Canny(denoised, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)
    #Image.fromarray(edged).show()

    #obtaining contours from edges
    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)


    for c in cnts[:2]:
        # compute the rotated bounding box of the contour
        orig = image.copy()
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")

        #Order the points
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

        #compute midpoints
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        #find the centroid
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0

        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
            (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
            (255, 0, 255), 2)

        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        dims.append((dA, dB, cX))

        # draw the object sizes on the image
        # cv2.putText(orig, "{:.1f}in".format(dimA),
        #     (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
        #     0.65, (255, 255, 255), 2)
        # cv2.putText(orig, "{:.1f}in".format(dimB),
        #     (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
        #     0.65, (255, 255, 255), 2)
        Image.fromarray(orig).show()
        
    return dims


def get_objects(im_td, im_side):
    """
    Computes the 3D dimensions of an object, and a known reference object using top down and side view images

    Args:
        im_td (numpy.ndarray): Top-down view image
        im_side (numpy.ndarray): Side view image

    Returns:
        Tuple containing two 3d dimensions:
            - reference_dim (tuple): The dimensions of the reference object
            - object_dim (tuple): The dimensions of the second object
    """

    td_dims = get_dims(im_td)
    side_dims = get_dims(im_side)

    #ensures only 2 objects
    assert len(td_dims) != 2 or len(side_dims != 2)
    
    #identify the reference object
    left_td_dim = td_dims[0] if td_dims[0][2] < td_dims[1][2] else td_dims[1]
    left_side_dim = side_dims[0] if side_dims[0][2] < side_dims[1][2] else side_dims[1]
    reference_dim = get_3_dim_from_dims(left_td_dim, left_side_dim)

    #identify the packing object
    right_td_dim = td_dims[0] if left_td_dim is td_dims[1] else td_dims[1]
    right_side_dim = side_dims[0] if left_side_dim is side_dims[1] else side_dims[1]
    object_dim = get_3_dim_from_dims(right_td_dim, right_side_dim)

    return (reference_dim, object_dim)