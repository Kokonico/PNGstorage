"""any file to PNG"""
import os
from PIL import Image, PngImagePlugin
import math
from pytextbin import *

textbin = pytextbin.Textbin()


def encode():

    """main"""
    # read file

    file = input(f"Select File (current path: {os.getcwd()}): ")
    # get a file extension
    _, file_extension = os.path.splitext(file)

    # read file as bytes

    try:
        with open(file, 'rb') as f:
            original_data = f.read()
    except FileNotFoundError:
        # Ask the user to select an existing file
        print("The file doesn't exist in this current location.")
        encode()
        return  # Added return to prevent further execution

    # Calculate the padding needed
    original_bytes = len(original_data)
    padding_bytes = (int(math.pow(math.isqrt(original_bytes) + 1, 2) - original_bytes)+1) * 3

    # pad the byte data
    byte_data = original_data + b'\x00' * padding_bytes

    # Calculate total pixels and find width and height
    total_pixels = len(byte_data) // 3

    width = height = math.isqrt(total_pixels)

    # Convert the bytes to an image
    image = Image.frombytes('RGB', (width, height), byte_data)

    # Create a PngInfo object and add a file type to it
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text('original_bytes', str(original_bytes))
    pnginfo.add_text('file_type', file_extension)

    # Save the new image
    image.save('output.png', pnginfo=pnginfo)

    # Integrity check: decode the encoded image and compare with original data
    decoded_data = image.tobytes()[:original_bytes]
    print("Verifying Integrity...")
    if original_data != decoded_data:
        print("Integrity check failed!")
        advanced_scan = input("Do you want to perform an advanced error scan? (y/n): ")
        if advanced_scan.lower() == 'y':
            error_count = 0
            for i, (original_byte, decoded_byte) in enumerate(zip(original_data, decoded_data)):
                if original_byte != decoded_byte:
                    print(f"[ERROR]: Difference at byte {i}: original {original_byte}, decoded {decoded_byte}")
                    error_count += 1
            if error_count == 0:
                print("No byte differences found.")
            else:
                print(f"{error_count} byte differences found.")
            error_count = 0
            if len(original_data) != len(decoded_data):
                print(f"[ERROR]: Length mismatch: original {len(original_data)}, decoded {len(decoded_data)}")
                print(f"Length mismatch {len(original_data) - len(decoded_data)} characters long")
            else:
                print("Lengths match.")

        else:
            print("advanced integrity check skipped.")


def decode():
    # Open the image
    try:
        image = Image.open(input("Select Image: "))
    except IOError:
        print("Error: Selected file is not an image.")
        return

    # Get the file type from image info
    try:
        file_type = image.text.get('file_type', '')
    except AttributeError:
        print("Unable to get file type from image info, you may need to manually add the file extension")
        file_type = ''

    try:
        original_bytes = int(image.text.get('original_bytes', '0'))
    except AttributeError:
        print("Unable to get original bytes from image info, the image cannot be decoded.")
        return

    # Convert the image back to bytes
    byte_data = image.tobytes()[:original_bytes]

    if len(byte_data) != original_bytes:
        print("Warning: The decoded data length does not match the original data length, decoding/encoding may have "
              "failed.")

    # Write the bytes back to a file
    with open(f'original_file{file_type}', 'wb') as f:
        f.write(byte_data)

    print("Done!")

#function to generate the encryption key
def generate_key(phrase):
    
    phrase = {"keyword": phrase}

    generated_key = textbin.json_to_base64(phrase)
    with open("key", "w") as f:
        key = f.write(generated_key)

    print("Generated Encryption key successfully\n")

def decode_key(phrase):
    with open("key", "r") as f:
        data = f.read()
        decoded_key = textbin.base64_to_json(data)

    return decoded_key

if __name__ == "__main__":
    while True:
        choice = input("1. Encode\n2. Decode\n3. Exit\nChoice: ")
        match choice:
            case '1':

                #generate encryption key
                try:
                    key_phrase = input("Enter a key Phrase: ")
                    generate_key(key_phrase)
                except ValueError:
                    print("Enter a key phrase value")
                
                encode()
            case '2':

                try:
                    phrase = input("Enter the key Phrase: ")    
                except ValueError:
                    print("Enter a key phrase value")

                decoded_key = decode_key(phrase)
                if decoded_key["keyword"] == phrase:
                    decode()
                else:
                    print("Wrong phrase. Try again")

            case '3':
                exit(0)
            case _:
                print("Invalid Choice")
