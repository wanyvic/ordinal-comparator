"""
Comparator implementation for Ordinal inscriptions protocol.
"""

from typing import Dict, Any, List, Tuple
from deepdiff import DeepDiff

from .comparator import BaseComparator


class OrdinalComparator(BaseComparator):
    """
    Comparator for Ordinal protocol block receipts.
    """

    def compare_block_receipts(self, primary_data: Dict[str, Any], secondary_data: Dict[str, Any]) -> Tuple[
        bool, List[str]]:
        """
        Compare two Ordinal block receipts and return any discrepancies.
        
        Args:
            primary_data: Block receipt data from the primary indexer
            secondary_data: Block receipt data from the secondary indexer
            
        Returns:
            A tuple containing:
                - Boolean indicating if the receipts match
                - List of discrepancy messages if any were found
        """
        # Apply any normalization needed
        primary_data = self._normalize_data(primary_data)
        secondary_data = self._normalize_data(secondary_data)

        # Check if both receipts exist
        if not primary_data and not secondary_data:
            return True, []
        elif not primary_data:
            return False, ["Primary indexer is missing Ordinal data for this block"]
        elif not secondary_data:
            return False, ["Secondary indexer is missing Ordinal data for this block"]

        # Do deep comparison of Ordinal receipts
        diff = DeepDiff(primary_data, secondary_data)

        if not diff:
            return True, []

        # Format discrepancy messages
        discrepancies = []
        for diff_type, changes in diff.items():
            for change in changes:
                discrepancies.append(f"Ordinal discrepancy: {diff_type} - {change}")

        return False, discrepancies
