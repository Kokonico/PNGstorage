"""any file to PNG"""
import os
from PIL import Image, PngImagePlugin
import math
import numpy as np

def encode(key: int = 0):
    """main"""
    # read file
    file = input(f"Select File (current path: {os.getcwd()}): ")

    # get a file extension
    _, file_extension = os.path.splitext(file)

    # read file as bytes
    with open(file, 'rb') as f:
        byte_data = f.read()

    # Calculate the padding needed
    padding = len(byte_data) % 3

    # Add the padding to the byte data
    byte_data += b'\x00' * padding

    # Calculate total pixels and find width and height
    total_pixels = len(byte_data) // 3
    sqrt_pixels = math.ceil(math.sqrt(total_pixels))  # round up square root

    # offset pixel colors by key
    byte_data = bytes((byte + key) % 256 for byte in byte_data)

    # Calculate total pixels and find width and height
    total_pixels = len(byte_data) // 4  # each pixel is 4 bytes in RGBA
    sqrt_pixels = math.ceil(math.sqrt(total_pixels))  # round up square root

    # offset pixel colors by key
    byte_data = bytes((byte + key) % 256 for byte in byte_data)

    # Calculate the number of transparent pixels needed
    transparent_pixels = (sqrt_pixels * sqrt_pixels) - total_pixels

    # Add the transparent pixels to the byte data
    byte_data += b'\x00\x00\x00\x00' * transparent_pixels

    # Convert the bytes to an image
    image = Image.frombytes('RGBA', (sqrt_pixels, sqrt_pixels), byte_data)

    # Create the PNG object
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text('file_type', file_extension)

    # Save the new image
    image.save('output.png', pnginfo=pnginfo)

    print("Done!")


def decode(key: int = 0):
    # Open the image
    image = Image.open(input("Select Image: "))

    # Get the file type from image info
    try:
        file_type = image.text.get('file_type', '')
    except AttributeError:
        print("Unable to get file type from image info, you may need to manually add the file extension")
        file_type = ''

    # Convert the image back to bytes
    byte_data = np.array(image)

    # Remove the transparent pixels
    byte_data = byte_data[byte_data[..., 3] != 0]

    # Flatten the array and convert it to bytes
    byte_data = byte_data.flatten().tobytes()

    # offset pixel colors by key
    byte_data = bytes((byte - key) % 256 for byte in byte_data)

    # Write the bytes back to a file
    with open(f'original_file{file_type}', 'wb') as f:
        f.write(byte_data)


if __name__ == "__main__":
    while True:
        choice = input("1. Encode\n2. Decode\n3. Exit\nChoice: ")
        match choice:
            case '1':
                key = int(input("Enter Key (leave blank for 0): ") or 0)
                encode(key)
            case '2':
                key = int(input("Enter Key (leave blank for 0): ") or 0)
                decode(key)
            case '3':
                exit(0)
            case _:
                print("Invalid Choice")
