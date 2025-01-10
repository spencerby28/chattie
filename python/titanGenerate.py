import boto3
import json
import base64
from typing import List
from dotenv import load_dotenv
import os
import random
import time

# Load environment variables from .env file
load_dotenv()

# List of objects that could make fun profile pictures
OBJECTS = [
    "smiling coffee cup",
    "cheerful pencil",
    "happy book",
    "grinning pizza slice",
    "joyful guitar",
    "smiling plant",
    "happy computer",
    "cheerful bicycle",
    "grinning backpack",
    "smiling camera",
    "happy paintbrush",
    "cheerful umbrella",
    "grinning clock",
    "smiling lamp",
    "happy teapot",
    "cheerful cookie",
    "grinning sandwich",
    "smiling phone",
    "happy calculator",
    "cheerful headphones"
]

def initialize_bedrock_client(region: str = None) -> boto3.client:
    """Initialize the Bedrock client."""
    if region is None:
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=region,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

def generate_images(
    prompt: str,
    num_images: int = 1,
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
    cfg_scale: int = 8,
    quality: str = "standard"
) -> List[bytes]:
    """
    Generate images using Amazon Titan Image Generator.
    
    Args:
        prompt (str): The text description of the image to generate
        num_images (int): Number of images to generate
        seed (int): Random seed for reproducibility
        width (int): Image width
        height (int): Image height
        cfg_scale (int): How closely the model follows the prompt
        quality (str): Image quality setting ("standard" or "premium")
        
    Returns:
        List[bytes]: List of generated images as bytes
    """
    client = initialize_bedrock_client()
    
    request_body = {
        "textToImageParams": {
            "text": prompt
        },
        "taskType": "TEXT_IMAGE",
        "imageGenerationConfig": {
            "cfgScale": cfg_scale,
            "seed": seed,
            "quality": quality,
            "width": width,
            "height": height,
            "numberOfImages": num_images
        }
    }
    
    # Convert the request body to JSON string
    body = json.dumps(request_body)
    
    # Make the API call
    response = client.invoke_model(
        modelId="amazon.titan-image-generator-v2:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )
    
    # Parse the response
    response_body = json.loads(response["body"].read())
    
    # Extract and decode the images
    images = []
    for image_data in response_body["images"]:
        image_bytes = base64.b64decode(image_data)
        images.append(image_bytes)
    
    return images

def generate_profile_prompt(object_name: str) -> str:
    """Generate a consistent prompt for profile pictures."""
    style_prompt = (
        f"A cute {object_name} character in a minimalist cartoon photorealistic style, "
        "centered like a profile picture, clean background, warm lighting, "
        "friendly expression, high quality digital art"
    )
    return style_prompt

def generate_batch_profiles(
    batch_size: int = 5,
    start_index: int = 0,
    seed_start: int = 1000
) -> None:
    """
    Generate a batch of profile pictures.
    
    Args:
        batch_size: Number of images to generate in this batch
        start_index: Starting index for file naming
        seed_start: Starting seed for consistent but varied generation
    """
    for i in range(batch_size):
        # Select a random object
        object_name = random.choice(OBJECTS)
        prompt = generate_profile_prompt(object_name)
        
        try:
            # Generate a single image with a specific seed
            generated_images = generate_images(
                prompt=prompt,
                num_images=1,
                seed=seed_start + i,
                width=1024,
                height=1024,
                cfg_scale=8,
                quality="standard"
            )
            
            # Save the generated image
            image_bytes = generated_images[0]
            filename = f"profile_{start_index + i:03d}_{object_name.replace(' ', '_')}.png"
            
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"Generated: {filename}")
            
            # Add a small delay to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error generating {object_name}: {str(e)}")
            time.sleep(5)  # Longer delay on error

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("profile_images", exist_ok=True)
    os.chdir("profile_images")
    
    # Generate 100 images in batches of 5
    total_images = 100
    batch_size = 5
    
    for batch in range(0, total_images, batch_size):
        print(f"\nGenerating batch {batch//batch_size + 1}/{total_images//batch_size}")
        generate_batch_profiles(
            batch_size=batch_size,
            start_index=batch,
            seed_start=1000 + batch
        )
        # Add a delay between batches
        time.sleep(5)
