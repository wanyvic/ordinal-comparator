#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Ordinal and BRC20 Indexer Comparator Tool

This tool compares block receipts from two different indexers to identify discrepancies.
It supports both Ordinal and BRC20 protocols on Bitcoin and Fractal blockchains.
"""

import argparse
import logging
import sys
import urllib3

from gevent import monkey, pool

from ordinal_comparator.core.blockchain import Blockchain
from ordinal_comparator.utils.logging import setup_logging
from ordinal_comparator.core.comparator import IndexerComparator
from ordinal_comparator.core.protocol import Protocol

# Configure gevent to improve HTTP request handling
monkey.patch_all(ssl=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_arguments():
    """
    Parse command-line arguments for the indexer comparator.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='ordinal-comparator',
        description='Compare block receipts from two indexers for verification and quality assurance.'
    )

    # Required arguments
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument(
        '-p', '--primary-endpoint',
        help='URL of the primary indexer endpoint (reference)',
        type=str,
        required=True,
        dest='primary_endpoint'
    )
    required_args.add_argument(
        '-s', '--secondary-endpoint',
        help='URL of the secondary indexer endpoint (to verify)',
        type=str,
        required=True,
        dest='secondary_endpoint'
    )
    required_args.add_argument(
        '-m', '--protocol',
        help='Protocol to compare (ORDINAL or BRC20)',
        type=Protocol.from_string,
        required=True
    )
    required_args.add_argument(
        '-c', '--chain',
        help='Blockchain to compare (BITCOIN or FRACTAL)',
        type=Blockchain.from_string,
        required=True,
        dest='blockchain'
    )

    # Optional arguments
    optional_args = parser.add_argument_group('Optional Arguments')
    optional_args.add_argument(
        '--start-block',
        help='Starting block height (default: first protocol-specific block)',
        type=int,
        dest='start_block'
    )
    optional_args.add_argument(
        '--end-block',
        help='Ending block height (default: latest common block)',
        type=int,
        dest='end_block'
    )
    optional_args.add_argument(
        '--threads',
        help='Number of concurrent worker threads (default: 100)',
        type=int,
        default=100
    )
    
    # Logging options
    log_args = parser.add_argument_group('Logging Options')
    log_args.add_argument(
        '--log-level',
        help='Set the logging level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        dest='log_level'
    )
    log_args.add_argument(
        '--log-file',
        help='Path to the log file (default: log to console)',
        type=str,
        dest='log_file'
    )

    return parser.parse_args()


def main():
    """
    Main entry point for the indexer comparator tool.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_file, args.log_level)
    logging.info(f"Starting comparison with arguments: {args}")
    
    try:
        # Initialize the comparator
        comparator = IndexerComparator(
            primary_endpoint=args.primary_endpoint,
            secondary_endpoint=args.secondary_endpoint,
            blockchain=args.blockchain,
            protocol=args.protocol,
            start_block=args.start_block,
            end_block=args.end_block
        )
        
        # Create thread pool and run comparison
        thread_pool = pool.Pool(args.threads)
        comparator.run(thread_pool)
        
        return 0
    except KeyboardInterrupt:
        logging.info("Program interrupted by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main()) 