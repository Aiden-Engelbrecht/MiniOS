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
        self.history = []
        self.history_index = -1
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
        readme = File("README.txt", "Welcome to MiniOS!\n\nThis is a virtual file system.\n\nYou can create, delete, and navigate files and folders.", documents)
        documents.add_item(readme)
        
        notes = File("notes.txt", "Remember to save your work.\n\nProject ideas:\n- Build more apps\n- Add themes\n- Improve performance", documents)
        documents.add_item(notes)
        
        # Create a sample image description
        image_info = File("image_info.txt", "Sample image files would be stored here.\n\nSupported formats: PNG, JPG, GIF, BMP", pictures)
        pictures.add_item(image_info)
        
        # Add some files to Downloads
        download1 = File("file1.zip", "This is a dummy zip file.\n\nContains sample data.", downloads)
        downloads.add_item(download1)
        
        download2 = File("file2.pdf", "Sample PDF document.\n\nThis is a placeholder for PDF files.", downloads)
        downloads.add_item(download2)
        
        # Add a system folder
        system = Folder("System", self.root)
        self.root.add_item(system)
        
        config = File("config.json", '{"theme": "dark", "language": "en", "auto_save": true}', system)
        system.add_item(config)
        
        # Add a trash folder
        trash = Folder(".Trash", self.root)
        self.root.add_item(trash)
        
    def cd(self, path: str) -> bool:
        """Change directory with history"""
        success = False
        old_dir = self.current_directory
        
        if path == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
                success = True
        elif path == "/":
            self.current_directory = self.root
            success = True
        else:
            item = self.current_directory.get_item(path)
            if item and isinstance(item, Folder):
                self.current_directory = item
                success = True
        
        if success and old_dir != self.current_directory:
            # Add to history
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_directory)
            self.history_index = len(self.history) - 1
        
        return success
    
    def go_back(self) -> bool:
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_directory = self.history[self.history_index]
            return True
        return False
    
    def go_forward(self) -> bool:
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_directory = self.history[self.history_index]
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
    
    def rename_item(self, old_name: str, new_name: str) -> bool:
        """Rename a file or folder"""
        item = self.current_directory.get_item(old_name)
        if not item:
            return False
        if new_name in self.current_directory.children:
            return False
        
        self.current_directory.remove_item(old_name)
        item.name = new_name
        self.current_directory.add_item(item)
        return True
    
    def copy_item(self, name: str, destination: Folder) -> bool:
        """Copy a file or folder to destination"""
        item = self.current_directory.get_item(name)
        if not item:
            return False
        
        if isinstance(item, File):
            new_file = File(item.name, item.content, destination)
            destination.add_item(new_file)
            return True
        elif isinstance(item, Folder):
            new_folder = Folder(item.name, destination)
            destination.add_item(new_folder)
            # Copy all children recursively
            for child in item.list_items():
                if isinstance(child, File):
                    new_child = File(child.name, child.content, new_folder)
                    new_folder.add_item(new_child)
                elif isinstance(child, Folder):
                    self._copy_folder(child, new_folder)
            return True
        return False
    
    def _copy_folder(self, source: Folder, destination: Folder):
        """Helper to copy folder recursively"""
        new_folder = Folder(source.name, destination)
        destination.add_item(new_folder)
        for child in source.list_items():
            if isinstance(child, File):
                new_child = File(child.name, child.content, new_folder)
                new_folder.add_item(new_child)
            elif isinstance(child, Folder):
                self._copy_folder(child, new_folder)
    
    def move_item(self, name: str, destination: Folder) -> bool:
        """Move a file or folder to destination"""
        item = self.current_directory.get_item(name)
        if not item:
            return False
        
        if self.current_directory.remove_item(name):
            destination.add_item(item)
            return True
        return False
    
    def get_path_for_item(self, item: FileSystemItem) -> str:
        """Get the path for a file system item"""
        return item.get_path()
    
    def get_all_items(self) -> List[FileSystemItem]:
        """Get all items in current directory (alias for get_current_items)"""
        return self.get_current_items()