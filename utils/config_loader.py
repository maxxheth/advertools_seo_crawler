"""
Configuration Loader - Loads and merges YAML config with environment variables
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and merge with environment variables.

    Args:
        config_path: Path to YAML config file. If None, uses CONFIG_PATH env var.

    Returns:
        Merged configuration dictionary
    """
    # Load environment variables
    load_dotenv()

    if config_path is None:
        config_path = os.getenv('CONFIG_PATH', '/app/config/config.yaml')

    # Load YAML config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}

    # Merge environment variables
    config = _merge_env_vars(config)

    return config


def _merge_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge environment variables into config dictionary.

    Args:
        config: Base configuration dictionary

    Returns:
        Configuration with environment variables merged in
    """
    # Map environment variable names to config paths
    env_mappings = {
        'DEFAULT_PAGE_LIMIT': ('crawl_settings', 'default_page_limit'),
        'WATCH_MODE': ('watch_settings', 'enabled'),
        'WATCH_PORT': ('watch_settings', 'websocket_port'),
        'DASHBOARD_MODE': ('dashboard', 'mode'),
        'AUTO_REFRESH_INTERVAL': ('dashboard', 'auto_refresh_interval'),
        'OUTPUT_PATH': ('output_settings', 'output_path'),
        'REPORT_STORAGE_PATH': ('analysis_settings', 'report_storage'),
        'ENABLE_ANALYSIS_REPORTS': ('analysis_settings', 'enable_reports'),
        'REPORT_RETENTION_DAYS': ('report_retention', 'days'),
        'REPORT_COMPRESSION': ('report_retention', 'compression'),
        'AUTO_CLEANUP': ('report_retention', 'auto_cleanup'),
        'SCREENSHOT_STORAGE': ('storage', 'screenshot_storage'),
        'S3_BUCKET': ('storage', 's3_bucket'),
        'S3_REGION': ('storage', 's3_region'),
        'S3_ACCESS_KEY': ('storage', 's3_access_key'),
        'S3_SECRET_KEY': ('storage', 's3_secret_key'),
        'MAX_CONCURRENT_CRAWLERS': ('crawl_settings', 'max_concurrent'),
    }

    for env_var, config_path in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Navigate/create config path and set value
            _set_nested_value(config, config_path, env_value)

    return config


def _set_nested_value(config: Dict[str, Any], path: tuple, value: Any) -> None:
    """
    Set a value in a nested dictionary using a path tuple.

    Args:
        config: Dictionary to modify
        path: Tuple of keys representing the path
        value: Value to set
    """
    current = config
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Convert string values to appropriate types
    if isinstance(value, str):
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)

    current[path[-1]] = value


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a value from config using dot notation (e.g., 'crawl_settings.default_page_limit').

    Args:
        config: Configuration dictionary
        path: Dot-notated path to value
        default: Default value if path doesn't exist

    Returns:
        Configuration value or default
    """
    keys = path.split('.')
    current = config

    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default

    return current if current is not None else default
