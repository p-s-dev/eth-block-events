"""
Configuration management for ETH Block Events ETL
Converts Spring Boot YAML configuration to Python
"""
import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path


class EventConfig(BaseModel):
    """Configuration for a contract event"""
    name: str
    signature: str
    topics: List[str] = Field(default_factory=list)
    enabled: bool = True


class ContractConfig(BaseModel):
    """Configuration for a smart contract"""
    name: str
    address: str
    events: List[EventConfig]


class EthereumConfig(BaseModel):
    """Ethereum node and blockchain configuration"""
    node_url: str = Field(alias="node-url")
    websocket_url: str = Field(alias="websocket-url")
    start_block: Optional[int] = Field(alias="start-block", default=None)
    block_polling_interval: int = Field(alias="block-polling-interval", default=1000)
    contracts: List[ContractConfig] = Field(default_factory=list)


class AppConfig(BaseModel):
    """Main application configuration"""
    ethereum: EthereumConfig
    logging_level: str = "INFO"
    
    class Config:
        allow_population_by_field_name = True


def load_config(config_file: str = "application.yml") -> AppConfig:
    """
    Load configuration from YAML file with environment variable substitution
    Mimics Spring Boot's configuration loading behavior
    """
    config_path = Path(__file__).parent / "src" / "main" / "resources" / config_file
    
    # Try different locations for config file
    possible_paths = [
        config_path,
        Path(__file__).parent / config_file,
        Path(config_file)
    ]
    
    config_data = None
    for path in possible_paths:
        if path.exists():
            with open(path, 'r') as f:
                config_data = yaml.safe_load(f)
            break
    
    if config_data is None:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    # Substitute environment variables
    config_data = _substitute_env_vars(config_data)
    
    return AppConfig(**config_data)


def load_local_config() -> AppConfig:
    """Load local configuration if available, fallback to default"""
    try:
        return load_config("application-local.yml")
    except FileNotFoundError:
        try:
            return load_config("application.yml") 
        except FileNotFoundError:
            # Return default config if no files found
            return AppConfig(
                ethereum=EthereumConfig(
                    node_url=os.getenv("ETHEREUM_NODE_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"),
                    websocket_url=os.getenv("ETHEREUM_WS_URL", "wss://mainnet.infura.io/ws/v3/YOUR_INFURA_PROJECT_ID"),
                    contracts=[]
                )
            )


def _substitute_env_vars(data: Any) -> Any:
    """Recursively substitute environment variables in configuration data"""
    if isinstance(data, dict):
        return {key: _substitute_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_substitute_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Simple environment variable substitution
        if data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            if ":" in env_var:
                var_name, default_value = env_var.split(":", 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(env_var, data)
        return data
    else:
        return data


# Global config instance
_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """Get global configuration instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = load_local_config()
    return _config