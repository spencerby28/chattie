import os
from PIL import Image

# Get all PNG files in profile_images directory that match the profile pattern
profile_dir = './profile_images'
profile_images = [f for f in os.listdir(profile_dir) if f.startswith('profile_') and f.endswith('.png')]

# Convert each image to webp
for image_file in profile_images:
    # Open the PNG image
    img = Image.open(os.path.join(profile_dir, image_file))
    
    # Create webp filename by replacing .png extension
    webp_filename = image_file.rsplit('.', 1)[0] + '.webp'
    
    # Convert and save as webp in profile_images directory
    img.save(os.path.join(profile_dir, webp_filename), 'webp')
    
    print(f'Converted {image_file} to {webp_filename}')
