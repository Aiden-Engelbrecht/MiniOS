"""
Recycle Bin for MiniOS
Stores deleted files with restore and empty functionality
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional


class RecycleBinItem:
    """An item in the recycle bin"""
    
    def __init__(self, original_path: str, file_name: str, file_type: str, size: int):
        self.original_path = original_path
        self.file_name = file_name
        self.file_type = file_type  # 'file' or 'folder'
        self.size = size
        self.deleted_date = datetime.now().isoformat()
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "original_path": self.original_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "size": self.size,
            "deleted_date": self.deleted_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RecycleBinItem':
        """Create from dictionary"""
        item = cls(
            data["original_path"],
            data["file_name"],
            data["file_type"],
            data["size"]
        )
        item.deleted_date = data["deleted_date"]
        return item


class RecycleBin:
    """Manages deleted files and folders"""
    
    def __init__(self, data_path: str = "data/recycle_bin.json"):
        self.data_path = data_path
        self.items: List[RecycleBinItem] = []
        self.load_items()
        
    def load_items(self):
        """Load recycle bin items from file"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                    self.items = [RecycleBinItem.from_dict(item) for item in data]
            except:
                self.items = []
        else:
            self.save_items()
    
    def save_items(self):
        """Save recycle bin items to file"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, 'w') as f:
            json.dump([item.to_dict() for item in self.items], f, indent=4)
    
    def add_item(self, original_path: str, file_name: str, file_type: str, size: int):
        """Add an item to the recycle bin"""
        item = RecycleBinItem(original_path, file_name, file_type, size)
        self.items.append(item)
        self.save_items()
        return item
    
    def remove_item(self, index: int) -> bool:
        """Remove an item from the recycle bin by index"""
        if 0 <= index < len(self.items):
            del self.items[index]
            self.save_items()
            return True
        return False
    
    def empty(self):
        """Empty the recycle bin"""
        self.items.clear()
        self.save_items()
    
    def get_items(self) -> List[RecycleBinItem]:
        """Get all items in the recycle bin"""
        return self.items
    
    def get_count(self) -> int:
        """Get number of items in the recycle bin"""
        return len(self.items)
    
    def get_total_size(self) -> int:
        """Get total size of all items"""
        return sum(item.size for item in self.items)
    
    def format_size(self, size: int) -> str:
        """Format file size for display"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"