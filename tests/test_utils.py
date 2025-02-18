from src.utils import debug_message, download_pack_images
from PIL import Image
import pytest
from config import DEBUG

def test_debug_message():
    assert DEBUG
    debug_message('Hello, this is a debug test')

@pytest.mark.asyncio
async def test_download_pack_images(pack_for_testing):
    """Test async image downloading for a pack."""
    # Fake image URLs (replace with real ones in actual tests)
    image_urls = [card.images.small for card in pack_for_testing]

    # Run the async image download function
    image_data_list = await download_pack_images(image_urls)

    # Check all images downloaded successfully
    assert len(image_data_list) == 10  # Expecting 10 images
    assert all(img_data is not None for img_data in image_data_list), "Some images failed to download"

    # Check if images are valid
    for img_data in image_data_list:
        image = Image.open(img_data)  # Open image in memory
        assert image is not None, "Failed to open image"
        assert isinstance(image, Image.Image), "Image is not a valid PIL image"
        image.show()
