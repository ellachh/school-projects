#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import math
import os
from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col):
    '''
    Given an image and the coordinates of the pixel we are trying to access,
    Returns the value of the pixel at those coordinates.
    '''
    index = row*image['width']+col #create a new index
    return image["pixels"][index] #call index instead of [col,row]


def set_pixel(image, row, col, color):
    '''
    Given an image, the coordinates of the pixel we are trying to change,
    and the new value of the pixel, set the pixel to its new value.
    '''
    index = row*image['width']+col #create same index
    image["pixels"][index] = color #call index


def apply_per_pixel(image, func):
    '''
    Given an image and a function, apply the function to every pixel in the image.
    '''
    result = {
        "height": image["height"],
        "width": image["width"], #spelled width wrong
        "pixels": [0]*len(image['pixels']), #fill in pixel as blank list of zeroes, was blank before: 'pixels' = []
    }
    for row in range(image["height"]):
        for col in range(image["width"]): #flip row and col
            set_pixel(result, row, col, func(row,col)) #needed to be indented more
    return result


def inverted(image):
    return apply_per_pixel(image, lambda row,col: 255-get_pixel(image,row,col))
    # it's 255-color, not 256-color

# HELPER FUNCTIONS
def get_pixel_edge(image, row, col, edge):
    '''
    Modifies the get_pixel function to account for edge effects if 
    the pixel has row and col arguements that are out of the bounds
    for height and width.
    '''
    if row in range(image['height']) and col in range(image['width']):
        return get_pixel(image,row,col)
    if edge == 'zero':
        return 0
    if edge == 'extend':
        row = 0 if row<0 else (image['height'] - 1 if row >= image['height'] else row)
        col = 0 if col<0 else (image['width'] - 1 if col >= image['width'] else col)
    if edge == 'wrap':
        row = row%image['height']
        col = col%image['width']
    return get_pixel(image,row,col)


                                                                                                      
def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    A list of lists, where each list in the list represents a row. The index of the 
    outer list is the row index, and 
    the index of the inner list is the column index.
    """
    if boundary_behavior not in ['zero','extend','wrap']:
        return None
    unit = math.floor(len(kernel)/2)
    def apply_kernel(row,col):
        '''
        Given the row and column of each pixel, this function applies the kernel to each pixel in
        the list pixels and returns the new value of the pixel. This function is meant to be
        used in conjunction with apply_per_pixel.
        '''
        color = 0
        for r_index in range(len(kernel)):
            for c_index in range(len(kernel[r_index])):
                    #calling the pixels +- units around i and j, scaling them by the kernel,
                    #and adding this to the value of the new pixel at (i,j)
                color+=get_pixel_edge(image,row+r_index-unit,col+c_index-unit,boundary_behavior)*kernel[r_index][c_index]
        return color
        
    return apply_per_pixel(image,apply_kernel)

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i, pixel in enumerate(image['pixels']):
        image['pixels'][i] = max(0,min(round(pixel),255))
    return image




# FILTERS

def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    kernel = kernel_size*[[1/(kernel_size**2)]*kernel_size]
    return round_and_clip_image(correlate(image,kernel,'extend'))

def sharpened(image,kernel_size):
    '''
    Return a new image representing the result of sharpening the image after it's blurred.
    Equivalent to 2*(original image)-Blurred image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    '''
    blurred_image = blurred(image,kernel_size)
    new_pixels = []
    for i in range(len(image['pixels'])):
        new_pixels.append(2*image['pixels'][i]-blurred_image['pixels'][i])
    return round_and_clip_image({'height':image['height'],'width':image['width'],'pixels':new_pixels})

def edges(image):
    '''
    Returns a new image representing the result of emphasizing the edges.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    '''
    kernel1 = [[-1,-2,-1],
               [0,0,0],
               [1,2,1]]
    kernel2 = [[-1,0,1],
               [-2,0,2],
               [-1,0,1]]
    output1 = correlate(image,kernel1,'extend')
    output2 = correlate(image,kernel2,'extend')
    new_pixels = []
    for x,y in zip(output1['pixels'],output2['pixels']):
        new_pixels.append(round(math.sqrt(x**2+y**2)))
    return round_and_clip_image({'height':image['height'],'width':image['width'],'pixels':new_pixels})


# HELPER FUNCTIONS FOR DISPLAYING, LOADING, AND SAVING IMAGES

def print_greyscale_values(image):
    """
    Given a greyscale image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that pixel values that are floats will be rounded to the nearest int.
    """
    out = f"Greyscale image with {image['height']} rows"
    out += f" and {image['width']} columns:\n "
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        val = str(round(pixel))
        space_vals.append((col, val))
        space_sizes[col] = max(len(val), space_sizes.get(col, 2))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for (col, val) in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"]-1:
            out += "\n "
    print(out)


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}

def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # blue = load_greyscale_image('test_images/bluegill.png')
    # save_greyscale_image(inverted(blue),'inverted_blue_gill.png')
    # pigbird = load_greyscale_image('test_images/pigbird.png')
    kernel = 2*[[0]*13]+[[1]+[0]*12]+10*[[0]*13]
    # save_greyscale_image(correlate(pigbird,kernel,'zero'),'pigbird_zero.png')
    # save_greyscale_image(correlate(pigbird,kernel,'extend'),'pigbird_extend.png')
    # save_greyscale_image(correlate(pigbird,kernel,'wrap'),'pigbird_wrap.png')
    # cat = load_greyscale_image('test_images/cat.png')
    # save_greyscale_image(blurred(cat,13),'cat_blurred.png')
    # save_greyscale_image(blurred(cat,13),'blurred_zero.png')
    # save_greyscale_image(blurred(cat,13),'blurred_wrap.png')
    # python = load_greyscale_image('test_images/python.png')
    # save_greyscale_image(sharpened(python,11),'sharpened_python.png')
    construct = load_greyscale_image('test_images/construct.png')
    save_greyscale_image(edges(construct),'construct_edges.png')
