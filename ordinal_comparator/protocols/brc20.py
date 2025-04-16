"""
Comparator implementation for BRC20 token protocol.
"""

from typing import Dict, Any, List, Tuple
from deepdiff import DeepDiff
from jsonpath_ng import parse

from .comparator import BaseComparator


class BRC20Comparator(BaseComparator):
    """
    Comparator for BRC20 protocol block receipts.
    """

    def compare_block_receipts(self, primary_data: Dict[str, Any], secondary_data: Dict[str, Any]) -> Tuple[
        bool, List[str]]:
        """
        Compare two BRC20 block receipts and return any discrepancies.
        
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
            return False, ["Primary indexer is missing BRC20 data for this block"]
        elif not secondary_data:
            return False, ["Secondary indexer is missing BRC20 data for this block"]

        # Do deep comparison of BRC20 receipts
        diff = DeepDiff(primary_data, secondary_data)

        if not diff:
            return True, []

        # Format discrepancy messages
        discrepancies = []
        for diff_type, changes in diff.items():
            for change in changes:
                discrepancies.append(f"BRC20 discrepancy: {diff_type} - {change}")

        return False, discrepancies

    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the data structure to prepare for comparison.
        This method can be overridden by subclasses to handle protocol-specific normalization.

        Args:
            data: Raw data to normalize

        Returns:
            Normalized data structure
        """
        jsonpath_expr = parse('$.block[*].events[*]')
        matches = jsonpath_expr.find(data)

        # remove invalid events
        for match in matches:
            if not match.value['valid']:
                match.context.value.remove(match.value)

        # remove msg field from events
        jsonpath_expr_msg = parse('$.block[*].events[*].msg')
        for match in jsonpath_expr_msg.find(data):
            del match.context.value[match.path.fields[0]]

        return data
