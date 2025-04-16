"""
Core comparator implementation for blockchain indexers.

This module contains the main IndexerComparator class which orchestrates the 
comparison between different indexer endpoints.
"""

from datetime import timedelta
import time
import logging
import signal
from gevent import pool, event, GreenletExit
from tqdm import tqdm
from typing import Optional, Dict, Any, List, Tuple
import gevent
from gevent.greenlet import Greenlet

from ordinal_comparator.core.blockchain import Blockchain
from ordinal_comparator.core.protocol import Protocol
from ordinal_comparator.protocols import get_comparator
from ordinal_comparator.api.client import APIClient, OrdinalAPIClient, BRC20APIClient


class IndexerComparator:
    """
    Manager class for comparing blockchain indexers.
    
    This class orchestrates the comparison of block receipts between two indexer endpoints,
    handling concurrency, error recovery, and graceful shutdown.
    """
    
    def __init__(
        self, 
        primary_endpoint: str, 
        secondary_endpoint: str, 
        blockchain: Blockchain, 
        protocol: Protocol,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None
    ):
        """
        Initialize a new indexer comparator.
        
        Args:
            primary_endpoint: URL of the primary indexer endpoint
            secondary_endpoint: URL of the secondary indexer endpoint
            blockchain: Type of blockchain to compare
            protocol: Protocol to compare (BRC20 or Ordinal)
            start_block: Starting block height (default: chain-specific first block)
            end_block: Ending block height (default: lowest current height of both endpoints)
        """
        self.primary_endpoint = primary_endpoint
        self.secondary_endpoint = secondary_endpoint
        self.blockchain = blockchain
        self.protocol = protocol
        self.shutdown_event = event.Event()
        self._is_shutdown_handled = False

        # Initialize API clients based on protocol
        self.primary_client, self.secondary_client = self._create_api_clients()
        
        # Retrieve and validate chain information
        primary_chain_info = self.primary_client.get_node_info()['chainInfo']
        secondary_chain_info = self.secondary_client.get_node_info()['chainInfo']
        self._validate_network_compatibility(primary_chain_info, secondary_chain_info)
        
        # Get appropriate comparator
        self.comparator = get_comparator(blockchain, protocol)
        
        # Determine block range
        self.start_block = self._determine_start_block(start_block)
        primary_latest_block = primary_chain_info['ordBlockHeight']
        secondary_latest_block = secondary_chain_info['ordBlockHeight']
        min_latest_block = min(primary_latest_block, secondary_latest_block)
        self.end_block = self._determine_end_block(end_block, min_latest_block)
        
        # Validate block range
        if self.end_block < self.start_block:
            raise ValueError(
                f'End block {self.end_block} is less than start block {self.start_block}. '
                f'Please check parameters.'
            )
            
        logging.info(f'Initialized comparator for {blockchain.name} {protocol.name} '
                     f'from block {self.start_block} to {self.end_block}')

    def _create_api_clients(self) -> Tuple[APIClient, APIClient]:
        """
        Create the appropriate API clients based on protocol.
        
        Returns:
            Tuple of (primary_client, secondary_client)
        """
        if self.protocol == Protocol.BRC20:
            return (
                BRC20APIClient(self.primary_endpoint), 
                BRC20APIClient(self.secondary_endpoint)
            )
        elif self.protocol == Protocol.ORDINAL:
            return (
                OrdinalAPIClient(self.primary_endpoint), 
                OrdinalAPIClient(self.secondary_endpoint)
            )
        else:
            raise ValueError(f'Unsupported protocol: {self.protocol}')

    def _validate_network_compatibility(self, primary_info: Dict[str, Any], secondary_info: Dict[str, Any]) -> None:
        """
        Validate that both endpoints are on the same network.
        
        Args:
            primary_info: Chain info from primary endpoint
            secondary_info: Chain info from secondary endpoint
            
        Raises:
            ValueError: If endpoints are on different networks
        """
        primary_network = primary_info['network']
        secondary_network = secondary_info['network']
        expected_network = self.blockchain.name.lower()
        
        if primary_network != expected_network or secondary_network != expected_network:
            raise ValueError(
                f'Endpoints are not on the same network. '
                f'Expected: {expected_network}, '
                f'Primary: {primary_network}, '
                f'Secondary: {secondary_network}'
            )

    def _determine_start_block(self, start_block: Optional[int]) -> int:
        """
        Determine the starting block height.
        
        Args:
            start_block: User-provided starting block height
            
        Returns:
            Resolved starting block height
        """
        if start_block is not None:
            return start_block
            
        # Use protocol-specific default starting blocks
        if self.protocol == Protocol.ORDINAL:
            return self.blockchain.get_first_inscription_height()
        elif self.protocol == Protocol.BRC20:
            return self.blockchain.get_first_brc20_height()
        else:
            raise ValueError(f'Cannot determine start block for protocol: {self.protocol}')

    def _determine_end_block(self, end_block: Optional[int], min_latest_block: int) -> int:
        """
        Determine the ending block height.
        
        Args:
            end_block: User-provided ending block height
            min_latest_block: Minimum latest block height between endpoints
            
        Returns:
            Resolved ending block height
        """
        if end_block is not None and end_block < min_latest_block:
            logging.info(
                f'Using specified end block {end_block} '
                f'(less than latest common block {min_latest_block})'
            )
            return end_block
        return min_latest_block

    def run(self, thread_pool: pool.Pool) -> None:
        """
        Run the indexer comparison process.
        
        Args:
            thread_pool: Gevent pool for concurrent processing
        """
        def signal_handler(sig, frame):
            """Handle interrupt signals for graceful shutdown."""
            if self._is_shutdown_handled:
                return
                
            self._is_shutdown_handled = True
            logging.info('Interrupt received, initiating graceful shutdown...')
            self.shutdown_event.set()

        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)

        start_time = time.time()
        logging.info(
            f'Starting comparison from block {self.start_block} to {self.end_block} '
            f'using protocol {self.protocol.name} on {self.blockchain.name} '
            f'with {thread_pool.size} concurrent workers'
        )
        
        # Track spawned tasks
        active_tasks: List[Greenlet] = []
        
        try:
            # Process blocks in range
            with tqdm(total=self.end_block - self.start_block + 1, desc="Processing Blocks") as progress:
                for height in range(self.start_block, self.end_block + 1):
                    if self.shutdown_event.is_set():
                        logging.info('Exiting due to shutdown signal')
                        break
                        
                    task = thread_pool.spawn(self._process_block, height, progress)
                    active_tasks.append(task)
                    
            # Wait for tasks to complete
            gevent.joinall(active_tasks)
            
            # Print completion message
            self._log_completion_metrics(start_time)
            
        except KeyboardInterrupt:
            # Handle keyboard interrupts
            logging.info('Keyboard interrupt detected.')
            self.shutdown_event.set()
            self._perform_graceful_shutdown(thread_pool, active_tasks)
        
        except Exception as e:
            # Handle unexpected errors
            logging.error(f'Fatal error: {e}', exc_info=True)
            self.shutdown_event.set()
            self._perform_graceful_shutdown(thread_pool, active_tasks)
            raise

    def _perform_graceful_shutdown(self, thread_pool: pool.Pool, active_tasks: List[Greenlet]) -> None:
        """
        Perform a graceful shutdown of the running tasks.
        
        Args:
            thread_pool: The gevent thread pool in use
            active_tasks: List of active greenlet tasks
        """
        try:
            logging.info('Canceling active tasks...')
            for task in active_tasks:
                if not task.ready():
                    task.kill(block=False)
                    
            logging.info('Waiting for tasks to terminate...')
            thread_pool.join(timeout=5)
            
            logging.info('Graceful shutdown completed.')
        except Exception as e:
            logging.error(f'Error during shutdown: {e}', exc_info=True)

    def _log_completion_metrics(self, start_time: float) -> None:
        """
        Log metrics about the completed comparison run.
        
        Args:
            start_time: Timestamp when the run was started
        """
        end_time = time.time()
        elapsed = end_time - start_time
        elapsed_delta = timedelta(seconds=elapsed)
        blocks_processed = self.end_block - self.start_block + 1
        avg_time_per_block = elapsed / blocks_processed if blocks_processed > 0 else 0
        
        logging.info(f'Comparison completed in {elapsed_delta}')
        logging.info(f'Processed {blocks_processed} blocks ({avg_time_per_block:.4f} seconds/block)')
        logging.info(f'Block range: {self.start_block} to {self.end_block}')

    def _process_block(self, height: int, progress: Optional[tqdm] = None) -> None:
        """
        Process a single block comparison.
        
        Args:
            height: Block height to process
            progress: Optional progress bar to update
        """
        if not self._is_block_eligible(height):
            if progress:
                progress.update(1)
            return
            
        try:
            # Get block hash
            try:
                block_hash = self.primary_client.get_block_hash_by_height(height)
            except Exception as e:
                logging.warning(f'Failed to get block hash for height {height}: {e}')
                return
                
            # Fetch block receipts from both endpoints
            primary_data = self._fetch_with_retry(
                lambda: self.primary_client.fetch_block_receipts(block_hash), 
                f"primary {self.protocol.name} block {height}"
            )
            
            secondary_data = self._fetch_with_retry(
                lambda: self.secondary_client.fetch_block_receipts(block_hash), 
                f"secondary {self.protocol.name} block {height}"
            )
            
            # Compare receipts
            matched, discrepancies = self.comparator.compare_block_receipts(primary_data, secondary_data)
            
            if not matched:
                logging.warning(f"Discrepancies found in block {height} ({block_hash}):")
                for discrepancy in discrepancies:
                    logging.warning(f"  {discrepancy}")
            else:
                logging.debug(f"Block {height} ({block_hash}) matched successfully.")
                
        except GreenletExit:
            # Task was killed during shutdown
            logging.debug(f'Process block {height} task killed during shutdown')
            
        except Exception as e:
            logging.error(f'Error processing block {height}: {e}', exc_info=True)
            
        finally:
            if progress and not self.shutdown_event.is_set():
                progress.update(1)

    def _is_block_eligible(self, height: int) -> bool:
        """
        Check if a block is eligible for comparison.
        
        Args:
            height: Block height to check
            
        Returns:
            True if the block should be processed, False otherwise
        """
        # Additional checks could be added here based on criteria
        return True
        
    def _fetch_with_retry(self, fetch_func, description: str, max_retries: int = 5) -> Dict[str, Any]:
        """
        Fetch data with automatic retry on failure.
        
        Args:
            fetch_func: Function to call for fetching data
            description: Description of what's being fetched (for logs)
            max_retries: Maximum number of retry attempts
            
        Returns:
            The fetched data
            
        Raises:
            Exception: If all retry attempts fail
        """
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                return fetch_func()
            except Exception as e:
                retry_count += 1
                last_error = e
                
                if retry_count < max_retries:
                    logging.debug(f'Retrying {description} ({retry_count}/{max_retries}) after error: {e}')
                    # Exponential backoff: 1s, 2s, 4s, ...
                    gevent.sleep(2 ** (retry_count - 1))
                else:
                    logging.warning(f'Failed to fetch {description} after {max_retries} attempts: {e}')
                    
        raise last_error or Exception(f'Failed to fetch {description} after {max_retries} attempts') 