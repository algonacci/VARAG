import os
from typing import Optional, List, Union
from PIL import Image
from openai import OpenAI
from varag.vlms import BaseVLM

class MistralVLM(BaseVLM):
    DEFAULT_BASE_URL = "https://api.mistral.ai/v1"
    DEFAULT_MODEL = "pixtral-12b-2409"
    DEFAULT_MAX_IMAGES = 5

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_images: int = DEFAULT_MAX_IMAGES
    ):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.model = model
        self.max_images = max_images
        self.client = self._initialize_client()

    def _initialize_client(self) -> OpenAI:
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _prepare_image_content(self, image: Union[str, Image.Image]) -> dict:
        if isinstance(image, str):
            # If image is a file path, open it
            image = Image.open(image)
        encoded_image = self._encode_image(image)
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{encoded_image}"
            }
        }

    def response(self, 
                 query: str,
                 images: Union[str, Image.Image, List[Union[str, Image.Image]]], 
                 max_tokens: Optional[int] = 300) -> str:
        if isinstance(images, (str, Image.Image)):
            images = [images]
        
        # Limit the number of images
        images = images[:self.max_images]
        
        content = [{"type": "text", "text": query}]
        content.extend(self._prepare_image_content(img) for img in images)

        completion_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": max_tokens
        }

        response = self.client.chat.completions.create(**completion_params)
        return response.choices[0].message.content

    def __call__(self, image: Union[str, Image.Image], query: str) -> str:
        """
        Implement the __call__ method to satisfy the BaseVLM abstract class requirement.
        This method provides a simpler interface for single-image queries.
        """
        return self.response(query, image)