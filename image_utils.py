import os
import shutil
import argparse
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


def is_image_empty(image_path):
    """Check if the image is empty (all pixels are zero)."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return True
    return not image.any()

def clean_and_rename_images(directory):
    """Delete empty images and rename remaining images in the specified directory."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    def extract_number(filename):
        """Extract number from filename, handling various formats."""
        # Try to find any number in the filename
        numbers = re.findall(r'\d+', filename)
        if numbers:
            # Return the last number found as an integer
            return int(numbers[-1])
        return 0

    # Get list of image files in the directory with proper numeric sorting
    image_files = [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg'))]
    image_files.sort(key=extract_number)

    # Delete empty images
    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        if is_image_empty(image_path):
            os.remove(image_path)
            print(f"Deleted empty image: {image_file}")

    # Get list of remaining image files with proper numeric sorting
    remaining_image_files = [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg'))]
    remaining_image_files.sort(key=extract_number)

    # Calculate required number of digits for the new filenames
    num_digits = len(str(len(remaining_image_files)))
    format_string = f"%0{max(4, num_digits)}d"  # Use at least 4 digits, more if needed

    # Rename remaining images
    for idx, image_file in enumerate(remaining_image_files):
        end = 'png' if image_file.endswith('png') else 'jpg'
        new_name = f"{format_string}.{end}" % idx
        old_path = os.path.join(directory, image_file)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {image_file} to {new_name}")

    print(f"Total images processed: {len(remaining_image_files)}")

def convert_image(image_path):
    """Convert a single PNG image to JPG format."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return None, image_path
    jpg_image_path = image_path.replace('.png', '.jpg')
    cv2.imwrite(jpg_image_path, image)
    return jpg_image_path, image_path

def convert_png_to_jpg(directory):
    """Convert all PNG images in the specified directory to JPG format."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    image_files = sorted([f for f in os.listdir(directory) if f.endswith('.png')])
    image_paths = [os.path.join(directory, image_file) for image_file in image_files]

    results = []
    with ThreadPoolExecutor() as executor:
        future_to_path = {executor.submit(convert_image, image_path): image_path for image_path in image_paths}
        for future in as_completed(future_to_path):
            jpg_image_path, original_image_path = future.result()
            results.append((jpg_image_path, original_image_path))

    # Remove original PNG files after conversion
    for jpg_image_path, original_image_path in results:
        if original_image_path:
            os.remove(original_image_path)

    print(f"Converted {len(image_files)} PNG images to JPG format")

def downsample_images(directory, fraction):
    """Reduces the number of images in the directory by keeping 1/fraction of them.
       Remaining images are renamed to have consecutive numbers, supporting up to 10,000 images.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    # Get list of image files in the directory, sorted to maintain order
    image_files = sorted([f for f in os.listdir(directory) if f.endswith('.jpg')])

    orig_num = len(image_files)
    print(f"Original number of images: {orig_num}")

    # Create a list of images to keep based on the fraction
    images_to_keep = [image_files[i] for i in range(orig_num) if i % fraction == 0]

    # Delete all images that are not in the images_to_keep list
    for image_file in image_files:
        if image_file not in images_to_keep:
            os.remove(os.path.join(directory, image_file))

    #clean_and_rename_images(directory)

    print(f"Remaining images after downsampling: {len(images_to_keep)}")

def split_batches(directory, num_batches):
    """ Split the images in the directory into num_batches.
        The split is done by creating subdirectories with the batch number.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return
    
    # Get list of image files in the directory
    image_files = sorted([f for f in os.listdir(directory) if f.endswith('.jpg')])
    num_images = len(image_files)
    images_per_batch = num_images // num_batches

    # Create subdirectories for the batches
    for i in range(num_batches):
        batch_directory = os.path.join(directory, f"batch_{i}")
        os.makedirs(batch_directory, exist_ok=True)
        print(f"Created batch directory: {batch_directory}")

    # Move images to the batch directories

    for i, image_file in enumerate(image_files):
        batch_idx = i // images_per_batch
        if batch_idx == num_batches:
            batch_idx -= 1
        batch_directory = os.path.join(directory, f"batch_{batch_idx}")
        image_path = os.path.join(directory, image_file)
        new_path = os.path.join(batch_directory, image_file)
        os.rename(image_path, new_path)

    print(f"Moved images to {num_batches} batch directories")
    print("Number of images per batch:", images_per_batch)

def join_batches(directory):
    """ Join the images from batch subdirectories back into the main directory.
        The batch subdirectories are then removed.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    # Get list of batch subdirectories
    batch_dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and d.startswith('batch_')]

    for batch_dir in batch_dirs:
        batch_directory = os.path.join(directory, batch_dir)
        
        # Get list of image files in the batch directory
        image_files = [f for f in os.listdir(batch_directory) if f.endswith('.jpg')]
        
        # Move images to the main directory
        for image_file in image_files:
            image_path = os.path.join(batch_directory, image_file)
            new_path = os.path.join(directory, image_file)
            os.rename(image_path, new_path)
        
        # Remove the batch directory
        shutil.rmtree(batch_directory)
        print(f"Removed batch directory: {batch_directory}")

    print("Joined all batch directories into the main directory")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some images.")
    parser.add_argument('-f', '--function', type=str, required=True, help='Function to execute')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    current_directory = os.getcwd()
    frames_directory = os.path.join(current_directory, "videos/20241022_RAITE/20241022_RAITE_laser4_drones")

    if args.function == 'clean_and_rename_images':
        clean_and_rename_images(frames_directory)
    elif args.function == 'convert_png_to_jpg':
        convert_png_to_jpg(frames_directory)
    elif args.function == 'downsample_images':
        downsample_images(frames_directory, 3)
    elif args.function == 'split_batches':
        split_batches(frames_directory, 3)
    elif args.function == 'join_batches':
        join_batches(frames_directory)
    else:
        print(f"Unknown function: {args.function}")