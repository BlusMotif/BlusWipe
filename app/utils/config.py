"""
Configuration management for BlusWipe application.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for BlusWipe application."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config_dir = Path(self.config_file).parent
        self.config_dir.mkdir(exist_ok=True)
        
        self._default_config = {
            "models": {
                "default": "u2net",
                "available": [
                    "u2net",
                    "u2netp", 
                    "u2net_human_seg",
                    "silueta",
                    "isnet-general-use"
                ],
                "cache_dir": str(self.config_dir / "models")
            },
            "processing": {
                "max_image_size": 2048,
                "quality": "high",
                "edge_enhancement": 1.0,
                "use_gpu": True,
                "batch_size": 1
            },
            "web": {
                "host": "127.0.0.1",
                "port": 8000,
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "max_batch_files": 10,
                "cleanup_interval": 3600,  # 1 hour
                "file_retention": 3600    # 1 hour
            },
            "desktop": {
                "window_size": [1000, 700],
                "theme": "dark",
                "auto_save": True,
                "show_preview": True
            },
            "paths": {
                "uploads": "uploads",
                "outputs": "outputs", 
                "temp": "temp",
                "logs": "logs"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": str(self.config_dir / "logs" / "bluswipe.log")
            }
        }
        
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Try to find project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Check if we're in development or installed
        if (project_root / "pyproject.toml").exists():
            # Development mode
            config_dir = project_root / "config"
        else:
            # Installed mode - use user config directory
            if os.name == 'nt':  # Windows
                config_dir = Path.home() / "AppData" / "Local" / "BlusWipe"
            else:  # Linux/macOS
                config_dir = Path.home() / ".config" / "bluswipe"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults (in case new options were added)
                config = self._deep_merge(self._default_config.copy(), loaded_config)
                return config
            else:
                # Create default config file
                self.save_config(self._default_config)
                return self._default_config.copy()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._default_config.copy()
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "models.default")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "models.default")
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current config if None)
        """
        config = config or self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def save(self):
        """Save current configuration to file."""
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._default_config.copy()
        self.save()
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model-related configuration."""
        return self.get("models", {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing-related configuration."""
        return self.get("processing", {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web-related configuration."""
        return self.get("web", {})
    
    def get_desktop_config(self) -> Dict[str, Any]:
        """Get desktop-related configuration."""
        return self.get("desktop", {})
    
    def get_paths_config(self) -> Dict[str, str]:
        """Get paths configuration."""
        return self.get("paths", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get("logging", {})
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        paths = self.get_paths_config()
        
        for path_name, path_value in paths.items():
            if path_name != "logs":  # Handle logs separately
                path = Path(path_value)
                path.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        log_file = self.get("logging.file")
        if log_file:
            log_path = Path(log_file).parent
            log_path.mkdir(parents=True, exist_ok=True)
        
        # Create models cache directory
        model_cache = self.get("models.cache_dir")
        if model_cache:
            Path(model_cache).mkdir(parents=True, exist_ok=True)
    
    def get_absolute_path(self, relative_path: str) -> str:
        """
        Convert relative path to absolute path based on project structure.
        
        Args:
            relative_path: Relative path string
            
        Returns:
            Absolute path string
        """
        if os.path.isabs(relative_path):
            return relative_path
        
        # Get project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        return str(project_root / relative_path)
    
    def validate_config(self) -> list:
        """
        Validate current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate models
        default_model = self.get("models.default")
        available_models = self.get("models.available", [])
        
        if default_model not in available_models:
            errors.append(f"Default model '{default_model}' not in available models")
        
        # Validate processing settings
        max_size = self.get("processing.max_image_size")
        if not isinstance(max_size, int) or max_size <= 0:
            errors.append("Invalid max_image_size in processing config")
        
        enhancement = self.get("processing.edge_enhancement")
        if not isinstance(enhancement, (int, float)) or enhancement < 0:
            errors.append("Invalid edge_enhancement in processing config")
        
        # Validate web settings
        port = self.get("web.port")
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("Invalid port in web config")
        
        max_file_size = self.get("web.max_file_size")
        if not isinstance(max_file_size, int) or max_file_size <= 0:
            errors.append("Invalid max_file_size in web config")
        
        return errors
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.config, indent=2)
    
    def __repr__(self) -> str:
        """Repr of configuration."""
        return f"Config(file='{self.config_file}')"


# Global configuration instance
config = Config()
