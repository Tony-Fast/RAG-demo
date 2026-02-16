"""
Token Usage Monitor Service

Tracks and limits daily token consumption across the application
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class TokenUsageMonitor:
    """
    Monitor and limit daily token usage
    """
    
    def __init__(self):
        self.token_limit = 2000000  # 每日token使用上限
        self.token_file = Path(__file__).parent.parent / "data" / "token_usage.json"
        self._ensure_token_file_exists()
        self._check_and_reset_daily_usage()
    
    def _ensure_token_file_exists(self):
        """
        Ensure token usage file exists
        """
        if not self.token_file.parent.exists():
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.token_file.exists():
            initial_data = {
                "last_reset_date": str(date.today()),
                "daily_usage": 0,
                "usage_history": {}
            }
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def _check_and_reset_daily_usage(self):
        """
        Check if we need to reset daily usage based on date
        """
        with open(self.token_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        last_reset = date.fromisoformat(data["last_reset_date"])
        today = date.today()
        
        if last_reset < today:
            # Save yesterday's usage to history
            if data["daily_usage"] > 0:
                data["usage_history"][str(last_reset)] = data["daily_usage"]
            
            # Reset daily usage
            data["daily_usage"] = 0
            data["last_reset_date"] = str(today)
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reset daily token usage for {today}")
    
    def add_token_usage(self, tokens: int) -> bool:
        """
        Add token usage and check if within limit
        
        Args:
            tokens: Number of tokens used
            
        Returns:
            True if usage is within limit, False otherwise
        """
        with open(self.token_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if adding tokens would exceed limit
        new_usage = data["daily_usage"] + tokens
        if new_usage > self.token_limit:
            logger.warning(f"Token usage limit exceeded: {new_usage} > {self.token_limit}")
            return False
        
        # Update usage
        data["daily_usage"] = new_usage
        
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Added {tokens} tokens to usage. Total: {new_usage}/{self.token_limit}")
        return True
    
    def get_token_usage(self) -> Dict[str, any]:
        """
        Get current token usage information
        
        Returns:
            Dictionary with usage information
        """
        self._check_and_reset_daily_usage()
        
        with open(self.token_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "current_usage": data["daily_usage"],
            "daily_limit": self.token_limit,
            "remaining": self.token_limit - data["daily_usage"],
            "last_reset_date": data["last_reset_date"],
            "usage_percentage": (data["daily_usage"] / self.token_limit) * 100 if self.token_limit > 0 else 0
        }
    
    def check_limit(self, tokens: int) -> bool:
        """
        Check if adding tokens would exceed limit
        
        Args:
            tokens: Number of tokens to check
            
        Returns:
            True if within limit, False otherwise
        """
        self._check_and_reset_daily_usage()
        
        with open(self.token_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data["daily_usage"] + tokens <= self.token_limit
    
    def get_usage_history(self) -> Dict[str, int]:
        """
        Get usage history
        
        Returns:
            Dictionary with date as key and usage as value
        """
        with open(self.token_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("usage_history", {})
    
    def reset_usage(self):
        """
        Reset token usage manually
        """
        data = {
            "last_reset_date": str(date.today()),
            "daily_usage": 0,
            "usage_history": {}
        }
        
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Manually reset token usage for {date.today()}")


# Singleton instance
token_usage_monitor = TokenUsageMonitor()