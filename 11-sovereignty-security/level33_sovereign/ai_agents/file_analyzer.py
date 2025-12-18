#!/usr/bin/env python3
"""
Intelligent File Analyzer for Level 33
AI-powered file organization and analysis
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import mimetypes


class FileAnalyzer:
    """AI-powered file analysis and organization"""
    
    def __init__(self, model="gemma2:9b"):
        self.model = model
        self.ollama_url = "http://localhost:11434"
        
    def query_llm(self, prompt, system_prompt=None):
        """Query the local LLM"""
        request = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            request["system"] = system_prompt
        
        try:
            result = subprocess.run(
                ["curl", "-s", "-X", "POST",
                 f"{self.ollama_url}/api/generate",
                 "-d", json.dumps(request)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get('response', '')
            return ""
        except:
            return ""
    
    def analyze_filename(self, filename):
        """
        Analyze filename to suggest better name
        
        Args:
            filename: Original filename
            
        Returns:
            Suggested filename
        """
        prompt = f"""Suggest a better, more descriptive filename for: {filename}

Rules:
- Keep it concise (max 50 chars)
- Use underscores instead of spaces
- Keep the file extension
- Make it descriptive and searchable

Suggested filename:"""
        
        system_prompt = "You are a file naming assistant. Suggest clear, descriptive filenames."
        
        suggestion = self.query_llm(prompt, system_prompt).strip()
        
        # Validate suggestion
        if suggestion and len(suggestion) < 100 and '/' not in suggestion:
            return suggestion
        return filename
    
    def categorize_file(self, filepath):
        """
        Categorize file based on content and metadata
        
        Args:
            filepath: Path to file
            
        Returns:
            Category and confidence
        """
        path = Path(filepath)
        
        if not path.exists():
            return "unknown", 0.0
        
        # Get file info
        filename = path.name
        extension = path.suffix.lower()
        size = path.stat().st_size
        mime_type = mimetypes.guess_type(str(path))[0] or "unknown"
        
        # Read first few lines if text file
        content_preview = ""
        if mime_type and mime_type.startswith('text'):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_preview = f.read(500)
            except:
                pass
        
        prompt = f"""Categorize this file into ONE category: work, personal, finance, media, code, documents, archive, or other.

Filename: {filename}
Extension: {extension}
MIME type: {mime_type}
Size: {size} bytes
Content preview: {content_preview[:200]}

Category (one word):"""
        
        system_prompt = "You are a file categorization assistant. Respond with only one word."
        
        category = self.query_llm(prompt, system_prompt).strip().lower()
        
        valid_categories = ['work', 'personal', 'finance', 'media', 'code', 'documents', 'archive', 'other']
        
        if category in valid_categories:
            return category, 0.8
        return 'other', 0.5
    
    def suggest_organization(self, directory):
        """
        Suggest organization structure for directory
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Organization suggestions
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {}
        
        # Analyze files
        files = list(dir_path.glob('*'))
        file_info = []
        
        for file in files[:20]:  # Limit to 20 files
            if file.is_file():
                category, confidence = self.categorize_file(file)
                file_info.append({
                    'name': file.name,
                    'category': category,
                    'confidence': confidence
                })
        
        # Group by category
        suggestions = {}
        for info in file_info:
            category = info['category']
            if category not in suggestions:
                suggestions[category] = []
            suggestions[category].append(info['name'])
        
        return suggestions
    
    def detect_duplicates(self, directory, similarity_threshold=0.9):
        """
        Detect potential duplicate files
        
        Args:
            directory: Directory to scan
            similarity_threshold: Name similarity threshold
            
        Returns:
            List of potential duplicate groups
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return []
        
        files = [f for f in dir_path.glob('*') if f.is_file()]
        duplicates = []
        
        # Simple name-based duplicate detection
        seen = {}
        for file in files:
            base_name = file.stem.lower()
            
            # Check for similar names
            for existing_base, existing_files in seen.items():
                # Simple similarity: check if one name contains the other
                if base_name in existing_base or existing_base in base_name:
                    existing_files.append(file.name)
                    break
            else:
                seen[base_name] = [file.name]
        
        # Filter groups with multiple files
        duplicates = [files for files in seen.values() if len(files) > 1]
        
        return duplicates
    
    def extract_metadata(self, filepath):
        """
        Extract and analyze file metadata
        
        Args:
            filepath: Path to file
            
        Returns:
            Metadata dictionary
        """
        path = Path(filepath)
        
        if not path.exists():
            return {}
        
        stat = path.stat()
        
        metadata = {
            'filename': path.name,
            'extension': path.suffix,
            'size_bytes': stat.st_size,
            'size_human': self._format_size(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'mime_type': mimetypes.guess_type(str(path))[0],
        }
        
        return metadata
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def generate_file_report(self, directory):
        """
        Generate comprehensive file analysis report
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Report dictionary
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {}
        
        files = [f for f in dir_path.glob('*') if f.is_file()]
        
        # Collect statistics
        total_size = sum(f.stat().st_size for f in files)
        file_types = {}
        
        for file in files:
            ext = file.suffix.lower() or 'no_extension'
            if ext not in file_types:
                file_types[ext] = {'count': 0, 'size': 0}
            file_types[ext]['count'] += 1
            file_types[ext]['size'] += file.stat().st_size
        
        report = {
            'directory': str(dir_path),
            'total_files': len(files),
            'total_size': self._format_size(total_size),
            'file_types': file_types,
            'organization_suggestions': self.suggest_organization(directory),
            'potential_duplicates': self.detect_duplicates(directory)
        }
        
        return report


# Test functionality
if __name__ == "__main__":
    print("=== File Analyzer Test ===\n")
    
    analyzer = FileAnalyzer()
    
    # Test on Downloads folder
    downloads = Path.home() / "Downloads"
    
    if downloads.exists():
        print(f"Analyzing: {downloads}\n")
        
        report = analyzer.generate_file_report(downloads)
        
        print(f"Total files: {report['total_files']}")
        print(f"Total size: {report['total_size']}\n")
        
        print("File types:")
        for ext, info in list(report['file_types'].items())[:10]:
            print(f"  {ext}: {info['count']} files")
        
        print("\nOrganization suggestions:")
        for category, files in report['organization_suggestions'].items():
            print(f"  {category}: {len(files)} files")
        
        if report['potential_duplicates']:
            print(f"\nPotential duplicates: {len(report['potential_duplicates'])} groups")
    else:
        print("Downloads folder not found")
