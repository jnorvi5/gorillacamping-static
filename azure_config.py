"""
Azure Services Configuration and Integration
Provides fallback-compatible Azure service integrations for Gorilla Camping
"""

import os
import logging
from typing import Optional, Dict, Any

# --- AZURE COSMOS DB ---
try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceNotFoundError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    print("⚠️ Azure Cosmos DB SDK not installed")

# --- AZURE BLOB STORAGE ---
try:
    from azure.storage.blob import BlobServiceClient
    BLOB_STORAGE_AVAILABLE = True
except ImportError:
    BLOB_STORAGE_AVAILABLE = False
    print("⚠️ Azure Blob Storage SDK not installed")

# --- AZURE KEY VAULT ---
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("⚠️ Azure Key Vault SDK not installed")

# --- AZURE APPLICATION INSIGHTS ---
try:
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    APPLICATION_INSIGHTS_AVAILABLE = True
except ImportError:
    APPLICATION_INSIGHTS_AVAILABLE = False
    print("⚠️ Azure Application Insights SDK not installed")


class AzureCosmosDB:
    """Azure Cosmos DB wrapper with MongoDB-compatible interface"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.containers = {}
        
        if not COSMOS_AVAILABLE:
            return
            
        try:
            cosmos_endpoint = os.environ.get('AZURE_COSMOS_ENDPOINT')
            cosmos_key = os.environ.get('AZURE_COSMOS_KEY')
            database_name = os.environ.get('AZURE_COSMOS_DATABASE', 'gorillacamping')
            
            if cosmos_endpoint and cosmos_key:
                self.client = CosmosClient(cosmos_endpoint, cosmos_key)
                self.database = self.client.get_database_client(database_name)
                print("✅ Azure Cosmos DB initialized")
            else:
                print("⚠️ Azure Cosmos DB credentials not found")
        except Exception as e:
            print(f"❌ Azure Cosmos DB initialization failed: {e}")
    
    def get_container(self, container_name: str):
        """Get or create a Cosmos DB container (equivalent to MongoDB collection)"""
        if not self.database:
            return None
            
        if container_name not in self.containers:
            try:
                # Try to get existing container
                container = self.database.get_container_client(container_name)
                # Test if it exists
                container.read()
                self.containers[container_name] = container
                print(f"✅ Connected to Cosmos DB container: {container_name}")
            except CosmosResourceNotFoundError:
                # Create container if it doesn't exist
                try:
                    container = self.database.create_container(
                        id=container_name,
                        partition_key=PartitionKey(path="/id"),
                        offer_throughput=400  # Minimum throughput
                    )
                    self.containers[container_name] = container
                    print(f"✅ Created Cosmos DB container: {container_name}")
                except Exception as e:
                    print(f"❌ Failed to create container {container_name}: {e}")
                    return None
            except Exception as e:
                print(f"❌ Failed to access container {container_name}: {e}")
                return None
                
        return self.containers.get(container_name)
    
    def is_available(self) -> bool:
        return self.client is not None


class AzureBlobStorage:
    """Azure Blob Storage wrapper for file uploads and static content"""
    
    def __init__(self):
        self.client = None
        
        if not BLOB_STORAGE_AVAILABLE:
            return
            
        try:
            connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
            if connection_string:
                self.client = BlobServiceClient.from_connection_string(connection_string)
                print("✅ Azure Blob Storage initialized")
            else:
                print("⚠️ Azure Blob Storage connection string not found")
        except Exception as e:
            print(f"❌ Azure Blob Storage initialization failed: {e}")
    
    def upload_file(self, container_name: str, blob_name: str, data: bytes) -> Optional[str]:
        """Upload file to blob storage and return URL"""
        if not self.client:
            return None
            
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(data, overwrite=True)
            return blob_client.url
        except Exception as e:
            print(f"❌ Failed to upload blob {blob_name}: {e}")
            return None
    
    def is_available(self) -> bool:
        return self.client is not None


class AzureKeyVault:
    """Azure Key Vault wrapper for secrets management"""
    
    def __init__(self):
        self.client = None
        
        if not KEY_VAULT_AVAILABLE:
            return
            
        try:
            vault_url = os.environ.get('AZURE_KEY_VAULT_URL')
            if vault_url:
                credential = DefaultAzureCredential()
                self.client = SecretClient(vault_url=vault_url, credential=credential)
                print("✅ Azure Key Vault initialized")
            else:
                print("⚠️ Azure Key Vault URL not found")
        except Exception as e:
            print(f"❌ Azure Key Vault initialization failed: {e}")
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret value from Key Vault with fallback to environment variables"""
        # First try Key Vault
        if self.client:
            try:
                secret = self.client.get_secret(secret_name)
                return secret.value
            except Exception as e:
                print(f"⚠️ Failed to get secret {secret_name} from Key Vault: {e}")
        
        # Fallback to environment variables
        return os.environ.get(secret_name)
    
    def is_available(self) -> bool:
        return self.client is not None


class AzureApplicationInsights:
    """Azure Application Insights wrapper for monitoring"""
    
    def __init__(self):
        self.exporter = None
        
        if not APPLICATION_INSIGHTS_AVAILABLE:
            return
            
        try:
            connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
            if connection_string:
                self.exporter = AzureMonitorTraceExporter.from_connection_string(connection_string)
                print("✅ Azure Application Insights initialized")
            else:
                print("⚠️ Application Insights connection string not found")
        except Exception as e:
            print(f"❌ Azure Application Insights initialization failed: {e}")
    
    def is_available(self) -> bool:
        return self.exporter is not None


# Initialize Azure services
azure_cosmos = AzureCosmosDB()
azure_blob = AzureBlobStorage()
azure_keyvault = AzureKeyVault()
azure_insights = AzureApplicationInsights()


def get_secret(secret_name: str, fallback_env_var: str = None) -> Optional[str]:
    """Get secret with Azure Key Vault fallback to environment variables"""
    # Try Azure Key Vault first
    secret = azure_keyvault.get_secret(secret_name)
    if secret:
        return secret
    
    # Fallback to environment variable (with optional different name)
    env_var = fallback_env_var or secret_name
    return os.environ.get(env_var)


def get_database_client():
    """Get database client - Azure Cosmos DB if available, otherwise returns None for MongoDB fallback"""
    if azure_cosmos.is_available():
        return azure_cosmos
    return None


def log_to_azure(message: str, level: str = "INFO"):
    """Log message to Azure Application Insights if available"""
    if azure_insights.is_available():
        # This would be implemented with proper telemetry client
        pass
    
    # Always log locally as fallback
    getattr(logging, level.lower(), logging.info)(message)