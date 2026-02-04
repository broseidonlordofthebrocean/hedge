"""Parser for 10-K SEC filings."""

import re
import logging
from typing import Optional, Any
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class TenKParser:
    """Parse 10-K filings to extract fundamental data."""

    XBRL_TAGS = {
        "total_assets": ["us-gaap:Assets", "Assets"],
        "total_liabilities": ["us-gaap:Liabilities", "Liabilities"],
        "total_equity": ["us-gaap:StockholdersEquity", "StockholdersEquity"],
        "total_revenue": ["us-gaap:Revenues", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"],
        "gross_profit": ["us-gaap:GrossProfit", "GrossProfit"],
        "operating_income": ["us-gaap:OperatingIncomeLoss", "OperatingIncomeLoss"],
        "net_income": ["us-gaap:NetIncomeLoss", "NetIncomeLoss"],
        "long_term_debt": ["us-gaap:LongTermDebt", "LongTermDebt"],
        "short_term_debt": ["us-gaap:ShortTermBorrowings", "ShortTermBorrowings"],
        "cash": ["us-gaap:CashAndCashEquivalentsAtCarryingValue"],
        "intangible_assets": ["us-gaap:IntangibleAssetsNetExcludingGoodwill", "us-gaap:Goodwill"],
        "property_plant_equipment": ["us-gaap:PropertyPlantAndEquipmentNet"],
    }

    def parse(self, content: str) -> dict[str, Any]:
        """Parse 10-K content and extract financial data."""
        result = {
            "total_assets": None,
            "tangible_assets": None,
            "intangible_assets": None,
            "total_liabilities": None,
            "total_debt": None,
            "long_term_debt": None,
            "short_term_debt": None,
            "cash_and_equivalents": None,
            "total_revenue": None,
            "gross_profit": None,
            "gross_margin": None,
            "operating_income": None,
            "operating_margin": None,
            "net_income": None,
            "net_margin": None,
        }

        for field, tags in self.XBRL_TAGS.items():
            value = self._extract_xbrl_value(content, tags)
            if value is not None:
                result[field] = value

        # Calculate derived values
        if result["total_assets"] and result.get("intangible_assets"):
            result["tangible_assets"] = result["total_assets"] - result["intangible_assets"]

        if result.get("long_term_debt") or result.get("short_term_debt"):
            result["total_debt"] = (result.get("long_term_debt") or 0) + (result.get("short_term_debt") or 0)

        if result["total_revenue"] and result.get("gross_profit"):
            result["gross_margin"] = Decimal(result["gross_profit"]) / Decimal(result["total_revenue"]) * 100

        if result["total_revenue"] and result.get("operating_income"):
            result["operating_margin"] = Decimal(result["operating_income"]) / Decimal(result["total_revenue"]) * 100

        if result["total_revenue"] and result.get("net_income"):
            result["net_margin"] = Decimal(result["net_income"]) / Decimal(result["total_revenue"]) * 100

        return result

    def _extract_xbrl_value(self, content: str, tags: list[str]) -> Optional[int]:
        """Extract numeric value from XBRL content."""
        for tag in tags:
            patterns = [
                rf'<[^>]*name="{tag}"[^>]*>([^<]+)<',
                rf'<{tag}[^>]*>([^<]+)</{tag}>',
            ]
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    try:
                        value_str = match.group(1).strip()
                        value_str = re.sub(r'[,$]', '', value_str)
                        value_str = value_str.replace('(', '-').replace(')', '')
                        return int(Decimal(value_str))
                    except (ValueError, InvalidOperation):
                        continue
        return None

    def extract_geographic_revenue(self, content: str) -> dict[str, Decimal]:
        """Extract geographic revenue breakdown."""
        regions = {}
        patterns = [
            (r'United States[^0-9]*\$?([\d,]+)', 'us'),
            (r'Europe[^0-9]*\$?([\d,]+)', 'europe'),
            (r'Asia[^0-9]*\$?([\d,]+)', 'asia'),
            (r'International[^0-9]*\$?([\d,]+)', 'international'),
        ]
        for pattern, region in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(',', '')
                    regions[region] = Decimal(value_str)
                except:
                    continue
        return regions
