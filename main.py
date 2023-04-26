import os
import csv
import time
from PIL import Image
import imagehash
import argparse

# Function to calculate similarity index between two images
def calculate_similarity_index(image1_path, image2_path):
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    hash1 = imagehash.phash(image1)
    hash2 = imagehash.phash(image2)
    return hash1 - hash2

# Function to get all image files in a directory and its subdirectories
def get_image_files(directory):
    image_files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
                image_files.append(os.path.join(dirpath, filename))
    return image_files

# Function to generate similarity groups and similarity index for images
def generate_similarity_groups(image_directory, similarity_threshold, output_csv, verbose=True, use_light_model=False, batch_size=1):
    """
    Generates similarity groups and similarity index for images in the given directory and saves the results to a CSV file.

    Args:
        image_directory (str): Directory containing the images.
        similarity_threshold (float): Similarity threshold between 0.00 and 1.00.
        output_csv (str): Output CSV filename.
        verbose (bool): Flag to control verbose output. Defaults to True.
        use_light_model (bool): Flag to use a lighter version of the imagehash algorithm. Defaults to False.
        batch_size (int): Batch size for processing images. Defaults to 1.

    Returns:
        None
    """

    if verbose:
        print("Generating similarity groups and similarity index...")

    image_files = get_image_files(image_directory)
    similarity_groups = {}
    image_count_per_folder = {}
    total_images = len(image_files)
    progress = 0
    start_time = time.time()

    for i in range(len(image_files)):
        similarity_group = None
        for j in range(i+1, len(image_files)):
            similarity_index = calculate_similarity_index(image_files[i], image_files[j])
            similarity_index /= 256  # Normalize similarity index to range [0, 1]
            if verbose:
                print(f"Similarity index between {image_files[i]} and {image_files[j]}: {similarity_index}")

            if similarity_index >= similarity_threshold:
                if similarity_group is None:
                    similarity_group = f'Similarity Group {len(similarity_groups) + 1}'
                if similarity_group not in similarity_groups:
                    similarity_groups[similarity_group] = []
                similarity_groups[similarity_group].append((os.path.basename(image_files[i]), similarity_index))
                similarity_groups[similarity_group].append((os.path.basename(image_files[j]), similarity_index))

        progress += 1
        elapsed_time = time.time() - start_time
        time_per_image = elapsed_time / progress if progress > 0 else 0
        estimated_total_time = time_per_image * total_images
        eta = estimated_total_time - elapsed_time
        if verbose:
            print(f"Progress: {progress}/{total_images}, Elapsed Time: {elapsed_time:.2f}s, ETA: {eta:.2f}s")   

    # Create a CSV file for writing
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Similarity Group', 'Image File', 'Similarity Index'])

        for similarity_group, images in similarity_groups.items():
            for image in images:
                writer.writerow([similarity_group, image[0], image[1]])
    
    if verbose:
        print(f"Similarity groups and similarity index written to {output_csv}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate similarity groups for images in a directory')
    parser.add_argument('image_directory', type=str, help='Directory containing the images')
    parser.add_argument('similarity_threshold', type=float, help='Similarity threshold between 0.00 and 1.00')
    parser.add_argument('output_csv', type=str, help='Output CSV filename')
    parser.add_argument('--verbose', action='store_true', help='Flag to control verbose output')
    parser.add_argument('--use_light_model', action='store_true', help='Flag to use a lighter version of the imagehash algorithm')
    parser.add_argument('--batch_size', type=int, default=1, help='Batch size for processing images')
    args = parser.parse_args()

    generate_similarity_groups(args.image_directory, args.similarity_threshold, args.output_csv, args.verbose, args.use_light_model, args.batch_size)
