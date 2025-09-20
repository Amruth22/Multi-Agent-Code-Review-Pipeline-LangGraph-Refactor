import os
import logging
from typing import Dict, Any, Optional
from ..utils.error_handling import ConfigurationError

# Default configuration
DEFAULT_CONFIG = {
    # GitHub API Configuration
    "GITHUB_TOKEN": "",
    "GITHUB_API_URL": "https://api.github.com",
    
    # Email Configuration
    "EMAIL_FROM": "",
    "EMAIL_PASSWORD": "",
    "EMAIL_TO": "",
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,
    
    # Gemini AI Configuration
    "GEMINI_API_KEY": "",
    "GEMINI_MODEL": "gemini-2.0-flash",
    
    # Quality Thresholds
    "PYLINT_THRESHOLD": 7.0,           # Minimum code quality score (0-10)
    "COVERAGE_THRESHOLD": 80.0,        # Minimum test coverage percentage
    "AI_CONFIDENCE_THRESHOLD": 0.8,    # Minimum AI analysis confidence
    "SECURITY_THRESHOLD": 8.0,         # Minimum security score (0-10)
    "DOCUMENTATION_THRESHOLD": 70.0,   # Minimum documentation coverage
    
    # Logging Configuration
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "logs/code_review.log"
}

# Logger
logger = logging.getLogger("config")

class ConfigManager:
    """Configuration manager for the application"""
    
    _instance = None
    _config = {}
    _initialized = False
    
    def __new__(cls):
        """Singleton implementation"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager"""
        if not self.__class__._initialized:
            self._load_config()
            self.__class__._initialized = True
    
    def _load_config(self):
        """Load configuration from environment variables and defaults"""
        config = DEFAULT_CONFIG.copy()
        
        # Override with environment variables
        for key in config:
            env_value = os.environ.get(key)
            if env_value is not None:
                # Convert numeric values
                if isinstance(config[key], (int, float)):
                    try:
                        if isinstance(config[key], int):
                            config[key] = int(env_value)
                        else:
                            config[key] = float(env_value)
                    except ValueError:
                        logger.warning(f"Invalid numeric value for {key}: {env_value}")
                else:
                    config[key] = env_value
        
        # Override with .env file if it exists
        self._load_env_file(config)
        
        self._config = config
    
    def _load_env_file(self, config: Dict[str, Any]) -> None:
        """Load configuration from .env file"""
        env_file = os.environ.get("ENV_FILE", ".env")
        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Remove quotes if present
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            
                            if key in config:
                                # Convert numeric values
                                if isinstance(config[key], (int, float)):
                                    try:
                                        if isinstance(config[key], int):
                                            config[key] = int(value)
                                        else:
                                            config[key] = float(value)
                                    except ValueError:
                                        logger.warning(f"Invalid numeric value for {key}: {value}")
                                else:
                                    config[key] = value
            except Exception as e:
                logger.warning(f"Error loading .env file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def validate(self) -> None:
        """Validate required configuration values"""
        required_keys = [
            "GITHUB_TOKEN",
            "GEMINI_API_KEY",
            "EMAIL_FROM",
            "EMAIL_PASSWORD",
            "EMAIL_TO"
        ]
        
        missing = [key for key in required_keys if not self._config.get(key)]
        if missing:
            raise ConfigurationError(
                f"Missing required configuration values: {', '.join(missing)}",
                {"missing_keys": missing}
            )
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values (for testing)"""
        return self._config.copy()

# Convenience function to get config instance
def get_config() -> ConfigManager:
    return ConfigManager()

# Function to get a specific config value
def get_config_value(key: str, default: Any = None) -> Any:
    return get_config().get(key, default)

# Function to validate configuration
def validate_config() -> None:
    get_config().validate()