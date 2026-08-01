
"""
Virtual File System for MiniOS
Manages files and folders in memory
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class FileSystemItem:
    """Base class for files and folders"""
    
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
        self.created = datetime.now()
        self.modified = datetime.now()
        
    def get_path(self) -> str:
        """Get full path of this item"""
        if self.parent:
            return os.path.join(self.parent.get_path(), self.name)
        return self.name
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat()
        }


class File(FileSystemItem):
    """A file in the virtual file system"""
    
    def __init__(self, name: str, content: str = "", parent=None):
        super().__init__(name, parent)
        self.content = content
        self.size = len(content)
        
    def read(self) -> str:
        """Read file content"""
        return self.content
    
    def write(self, content: str):
        """Write content to file"""
        self.content = content
        self.size = len(content)
        self.modified = datetime.now()
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data["type"] = "file"
        data["content"] = self.content
        data["size"] = self.size
        return data


class Folder(FileSystemItem):
    """A folder in the virtual file system"""
    
    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.children: Dict[str, FileSystemItem] = {}
        
    def add_item(self, item: FileSystemItem):
        """Add a file or folder to this folder"""
        self.children[item.name] = item
        item.parent = self
        self.modified = datetime.now()
        
    def remove_item(self, name: str) -> bool:
        """Remove an item by name"""
        if name in self.children:
            del self.children[name]
            self.modified = datetime.now()
            return True
        return False
    
    def get_item(self, name: str) -> Optional[FileSystemItem]:
        """Get an item by name"""
        return self.children.get(name)
    
    def list_items(self) -> List[FileSystemItem]:
        """List all items in this folder"""
        return list(self.children.values())
    
    def get_files(self) -> List[File]:
        """Get all files in this folder"""
        return [item for item in self.children.values() if isinstance(item, File)]
    
    def get_folders(self) -> List['Folder']:
        """Get all subfolders in this folder"""
        return [item for item in self.children.values() if isinstance(item, Folder)]
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data["type"] = "folder"
        data["children"] = {name: child.to_dict() for name, child in self.children.items()}
        return data


class VirtualFileSystem:
    """Main virtual file system manager"""
    
    def __init__(self):
        self.root = Folder("root")
        self.current_directory = self.root
        self.init_default_structure()
        
    def init_default_structure(self):
        """Initialize with some default files and folders"""
        # Create home folder
        home = Folder("home", self.root)
        self.root.add_item(home)
        
        # Create user folder
        user = Folder("user", home)
        home.add_item(user)
        
        # Create some folders
        documents = Folder("Documents", user)
        user.add_item(documents)
        
        downloads = Folder("Downloads", user)
        user.add_item(downloads)
        
        pictures = Folder("Pictures", user)
        user.add_item(pictures)
        
        # Create some files
        readme = File("README.txt", "Welcome to MiniOS!\n\nThis is a virtual file system.", documents)
        documents.add_item(readme)
        
        notes = File("notes.txt", "Remember to save your work.", documents)
        documents.add_item(notes)
        
        # Create a sample image description
        image_info = File("image_info.txt", "Sample image files would be stored here.", pictures)
        pictures.add_item(image_info)
        
        # Add some files to Downloads
        download1 = File("file1.zip", "This is a dummy zip file.", downloads)
        downloads.add_item(download1)
        
        # Add a system folder
        system = Folder("System", self.root)
        self.root.add_item(system)
        
        config = File("config.json", '{"theme": "dark", "language": "en"}', system)
        system.add_item(config)
        
    def cd(self, path: str) -> bool:
        """Change directory"""
        if path == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
                return True
            return False
        elif path == "/":
            self.current_directory = self.root
            return True
        else:
            # Check if path exists in current directory
            item = self.current_directory.get_item(path)
            if item and isinstance(item, Folder):
                self.current_directory = item
                return True
            return False
    
    def ls(self) -> List[str]:
        """List contents of current directory"""
        return [item.name for item in self.current_directory.list_items()]
    
    def pwd(self) -> str:
        """Get current path"""
        return self.current_directory.get_path()
    
    def mkdir(self, name: str) -> bool:
        """Create a new folder"""
        if name in self.current_directory.children:
            return False
        new_folder = Folder(name, self.current_directory)
        self.current_directory.add_item(new_folder)
        return True
    
    def touch(self, name: str, content: str = "") -> bool:
        """Create a new file"""
        if name in self.current_directory.children:
            return False
        new_file = File(name, content, self.current_directory)
        self.current_directory.add_item(new_file)
        return True
    
    def cat(self, name: str) -> Optional[str]:
        """Read a file's content"""
        item = self.current_directory.get_item(name)
        if item and isinstance(item, File):
            return item.read()
        return None
    
    def get_current_items(self) -> List[FileSystemItem]:
        """Get all items in current directory"""
        return self.current_directory.list_items()
    
    def get_item_info(self, name: str) -> Optional[Dict]:
        """Get information about an item"""
        item = self.current_directory.get_item(name)
        if item:
            return {
                "name": item.name,
                "type": "folder" if isinstance(item, Folder) else "file",
                "size": item.size if isinstance(item, File) else 0,
                "created": item.created,
                "modified": item.modified,
                "path": item.get_path()
            }
        return None