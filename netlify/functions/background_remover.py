"""
Core background removal engine for BlusWipe.
Provides high-quality AI-powered background removal capabilities.
"""

import os
import logging
from typing import Union, Optional, Tuple
import numpy as np
from PIL import Image, ImageEnhance
import cv2
import torch
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Delay import of rembg to avoid numba JIT compilation at startup
_rembg_imported = False
_remove_func = None
_new_session_func = None

def _import_rembg():
    """Lazy import of rembg to avoid startup delays."""
    global _rembg_imported, _remove_func, _new_session_func
    if not _rembg_imported:
        logger.info("Importing rembg module...")
        try:
            from rembg import remove, new_session
            _remove_func = remove
            _new_session_func = new_session
            _rembg_imported = True
            logger.info("rembg imported successfully")
        except Exception as e:
            logger.error(f"Failed to import rembg: {e}")
            raise
    return _remove_func, _new_session_func


class BackgroundRemover:
    """
    Main class for background removal operations.
    Supports multiple AI models and processing options.
    """
    
    def __init__(self, model_name: str = "u2net", use_gpu: bool = None):
        """
        Initialize the background remover.
        
        Args:
            model_name: Name of the model to use ('u2net', 'u2netp', 'silueta', etc.)
            use_gpu: Whether to use GPU acceleration (auto-detect if None)
        """
        self.model_name = model_name
        self.use_gpu = use_gpu if use_gpu is not None else torch.cuda.is_available()
        self.session = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model session."""
        try:
            logger.info(f"Initializing model: {self.model_name}")
            remove_func, new_session_func = _import_rembg()
            self.session = new_session_func(self.model_name)
            logger.info("Model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            # Fallback to default model
            try:
                self.model_name = "u2net"
                remove_func, new_session_func = _import_rembg()
                self.session = new_session_func(self.model_name)
            except Exception as e2:
                logger.error(f"Failed to initialize fallback model: {e2}")
                raise
    
    def remove_background(self, 
                         input_image: Union[str, Image.Image, np.ndarray],
                         output_format: str = "PNG") -> Image.Image:
        """
        Remove background from an image.
        
        Args:
            input_image: Input image (file path, PIL Image, or numpy array)
            output_format: Output format ('PNG', 'JPEG', etc.)
            
        Returns:
            PIL Image with background removed
        """
        try:
            # Convert input to PIL Image
            if isinstance(input_image, str):
                image = Image.open(input_image)
            elif isinstance(input_image, np.ndarray):
                image = Image.fromarray(input_image)
            elif isinstance(input_image, Image.Image):
                image = input_image
            else:
                raise ValueError("Unsupported input image type")
            
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Remove background using rembg
            logger.info("Processing image for background removal...")
            remove_func, _ = _import_rembg()
            output = remove_func(image, session=self.session)
            
            logger.info("Background removal completed successfully")
            return output
            
        except Exception as e:
            logger.error(f"Error during background removal: {e}")
            raise
    
    def remove_background_with_mask(self, 
                                   input_image: Union[str, Image.Image, np.ndarray]) -> Tuple[Image.Image, Image.Image]:
        """
        Remove background and return both the result and the mask.
        
        Args:
            input_image: Input image
            
        Returns:
            Tuple of (result_image, mask_image)
        """
        try:
            # Convert input to PIL Image
            if isinstance(input_image, str):
                image = Image.open(input_image)
            elif isinstance(input_image, np.ndarray):
                image = Image.fromarray(input_image)
            elif isinstance(input_image, Image.Image):
                image = input_image
            else:
                raise ValueError("Unsupported input image type")
            
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Remove background
            remove_func, _ = _import_rembg()
            output = remove_func(image, session=self.session)
            
            # Extract mask from alpha channel
            if output.mode == 'RGBA':
                mask = output.split()[-1]  # Alpha channel
            else:
                # Create a simple mask if no alpha channel
                mask = Image.new('L', output.size, 255)
            
            return output, mask
            
        except Exception as e:
            logger.error(f"Error during background removal with mask: {e}")
            raise
    
    def enhance_edges(self, image: Image.Image, strength: float = 1.0) -> Image.Image:
        """
        Enhance edges in the processed image for better quality.
        
        Args:
            image: Input image
            strength: Enhancement strength (0.0 to 2.0)
            
        Returns:
            Enhanced image
        """
        try:
            enhancer = ImageEnhance.Sharpness(image)
            return enhancer.enhance(strength)
        except Exception as e:
            logger.error(f"Error during edge enhancement: {e}")
            return image
    
    def add_background(self, 
                      foreground: Image.Image, 
                      background: Union[Image.Image, str, tuple]) -> Image.Image:
        """
        Add a new background to the processed image.
        
        Args:
            foreground: Foreground image with transparent background
            background: Background image, file path, or color tuple
            
        Returns:
            Combined image
        """
        try:
            if isinstance(background, str):
                # File path
                bg_image = Image.open(background)
            elif isinstance(background, tuple):
                # Color tuple (R, G, B)
                bg_image = Image.new('RGB', foreground.size, background)
            elif isinstance(background, Image.Image):
                bg_image = background
            else:
                raise ValueError("Unsupported background type")
            
            # Resize background to match foreground
            bg_image = bg_image.resize(foreground.size, Image.Resampling.LANCZOS)
            
            # Ensure background is RGB
            if bg_image.mode != 'RGB':
                bg_image = bg_image.convert('RGB')
            
            # Composite images
            if foreground.mode == 'RGBA':
                result = Image.alpha_composite(bg_image.convert('RGBA'), foreground)
                return result.convert('RGB')
            else:
                return foreground
                
        except Exception as e:
            logger.error(f"Error during background addition: {e}")
            raise
    
    def batch_process(self, 
                     input_folder: str, 
                     output_folder: str,
                     callback: Optional[callable] = None) -> list:
        """
        Process multiple images in batch.
        
        Args:
            input_folder: Path to input folder
            output_folder: Path to output folder
            callback: Optional callback function for progress updates
            
        Returns:
            List of processed file paths
        """
        try:
            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            # Get all image files
            supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
            image_files = [f for f in os.listdir(input_folder) 
                          if f.lower().endswith(supported_formats)]
            
            processed_files = []
            total_files = len(image_files)
            
            logger.info(f"Starting batch processing of {total_files} files...")
            
            for i, filename in enumerate(image_files):
                input_path = os.path.join(input_folder, filename)
                output_filename = os.path.splitext(filename)[0] + '_no_bg.png'
                output_path = os.path.join(output_folder, output_filename)
                
                try:
                    # Process image
                    result = self.remove_background(input_path)
                    result.save(output_path)
                    processed_files.append(output_path)
                    
                    logger.info(f"Processed {i+1}/{total_files}: {filename}")
                    
                    # Call progress callback if provided
                    if callback:
                        callback(i+1, total_files, filename)
                        
                except Exception as e:
                    logger.error(f"Failed to process {filename}: {e}")
                    continue
            
            logger.info(f"Batch processing completed. {len(processed_files)} files processed successfully.")
            return processed_files
            
        except Exception as e:
            logger.error(f"Error during batch processing: {e}")
            raise
    
    def get_available_models(self) -> list:
        """Get list of available models."""
        return ['u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use']
    
    def switch_model(self, model_name: str):
        """Switch to a different model."""
        if model_name in self.get_available_models():
            self.model_name = model_name
            self._initialize_model()
        else:
            raise ValueError(f"Model {model_name} not available")


class ImageProcessor:
    """
    Additional image processing utilities.
    """
    
    @staticmethod
    def resize_image(image: Image.Image, 
                    max_size: Tuple[int, int], 
                    maintain_aspect: bool = True) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: Input image
            max_size: Maximum size (width, height)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image
        """
        if maintain_aspect:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            return image
        else:
            return image.resize(max_size, Image.Resampling.LANCZOS)
    
    @staticmethod
    def optimize_for_processing(image: Image.Image, 
                              max_dimension: int = 1024) -> Image.Image:
        """
        Optimize image for faster processing.
        
        Args:
            image: Input image
            max_dimension: Maximum dimension for processing
            
        Returns:
            Optimized image
        """
        # Resize if too large
        width, height = image.size
        if max(width, height) > max_dimension:
            ratio = max_dimension / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def apply_feather(image: Image.Image, radius: int = 2) -> Image.Image:
        """
        Apply feathering to edges for smoother results.
        
        Args:
            image: Input image with alpha channel
            radius: Feathering radius
            
        Returns:
            Feathered image
        """
        if image.mode != 'RGBA':
            return image
        
        # Convert to numpy array for processing
        img_array = np.array(image)
        alpha = img_array[:, :, 3]
        
        # Apply Gaussian blur to alpha channel
        blurred_alpha = cv2.GaussianBlur(alpha, (radius*2+1, radius*2+1), 0)
        
        # Replace alpha channel
        img_array[:, :, 3] = blurred_alpha
        
        return Image.fromarray(img_array)


# Convenience function for simple usage
def remove_background_simple(input_path: str, 
                           output_path: str, 
                           model: str = "u2net") -> bool:
    """
    Simple function to remove background from an image.
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        model: Model name to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        remover = BackgroundRemover(model_name=model)
        result = remover.remove_background(input_path)
        result.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error in simple background removal: {e}")
        return False
