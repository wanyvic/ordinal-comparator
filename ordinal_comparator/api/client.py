import logging
import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, HTTPError, Timeout
from jsonpath_ng import parse
from urllib.parse import urljoin


class APIClient:
    """Base API client for making requests to indexer endpoints."""
    
    def __init__(self, base_url: str):
        """
        Initialize the API client with a base URL.
        
        Args:
            base_url: Base URL for the API endpoint
        """
        self.base_url = base_url.rstrip('/')
    
    def fetch_block_receipts(self, block_hash: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Fetch block receipts from the API endpoint.
        
        Args:
            block_hash: The hash of the block to fetch receipts for
            timeout: Request timeout in seconds
            
        Returns:
            Block receipt data
            
        Raises:
            RequestException: If the request fails
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_node_info(self, timeout: int = 10) -> Dict[str, Any]:
        """
        Retrieve node information from the API endpoint.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            Node information data
            
        Raises:
            RequestException: If the request fails
        """
        url = f"{self.base_url}/api/v1/node/info"
        response_data = self._fetch_json(url, timeout, "node info")
        data = response_data.get('data', {})

        # Normalize network name if it's "mainnet"
        jsonpath_expr = parse('$.chainInfo.network')
        for match in jsonpath_expr.find(data):
            if match.value == "mainnet":
                match.context.value[match.path.fields[0]] = "bitcoin"
        return data
    
    def get_block_hash_by_height(self, height: int, timeout: int = 5) -> str:
        """
        Retrieve block hash for a given height.
        
        Args:
            height: Block height to get hash for
            timeout: Request timeout in seconds
            
        Returns:
            Block hash as string
            
        Raises:
            RequestException: If the request fails
        """
        url = f"{self.base_url}/blockhash/{height}"
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            response.raise_for_status()
            return response.text.strip()
        except RequestException as error:
            logging.debug(f"Error fetching block hash for height {height}: {error}, URL: {url}")
            raise
    
    def _fetch_json(self, url: str, timeout: int, description: str) -> Dict[str, Any]:
        """
        Helper method to fetch JSON data from a URL with error handling.
        
        Args:
            url: URL to fetch data from
            timeout: Request timeout in seconds
            description: Description of what's being fetched (for logs)
            
        Returns:
            Parsed JSON response
            
        Raises:
            RequestException: If the request fails
        """
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            logging.debug(f"HTTP error fetching {description}: {http_err}, URL: {url}")
            raise
        except RequestException as req_err:
            logging.debug(f"Request error fetching {description}: {req_err}, URL: {url}")
            raise


class OrdinalAPIClient(APIClient):
    """API client for Ordinal indexer endpoints."""
    
    def fetch_block_receipts(self, block_hash: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Fetch Ordinals block receipts from the API endpoint.
        
        Args:
            block_hash: The hash of the block to fetch receipts for
            timeout: Request timeout in seconds
            
        Returns:
            Ordinals block receipt data
            
        Raises:
            RequestException: If the request fails
        """
        url = f"{self.base_url}/api/v1/ord/block/{block_hash}/events"
        return self._fetch_json(url, timeout, "Ordinals block receipts").get('data', {})


class BRC20APIClient(APIClient):
    """API client for BRC20 indexer endpoints."""
    
    def fetch_block_receipts(self, block_hash: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Fetch BRC20 block receipts from the API endpoint.
        
        Args:
            block_hash: The hash of the block to fetch receipts for
            timeout: Request timeout in seconds
            
        Returns:
            BRC20 block receipt data
            
        Raises:
            RequestException: If the request fails
        """
        url = f"{self.base_url}/api/v1/brc20/block/{block_hash}/events"
        return self._fetch_json(url, timeout, "BRC20 block receipts").get('data', {}) 