from pathlib import Path
import ast
import json
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.repository.repository import RepositoryArtefact
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Set
import entrypoints
from collections import defaultdict
import os
import logging
import uuid
from uuid import UUID

class RepositoryManager:

    @staticmethod
    def get_repository_artefact(repository_root: str, artefact_store: ArtefactStore, execution_id: UUID):

        commit_hash = RepositoryManager.get_commit_hash()
        languages = RepositoryManager.get_languages(repository_root=repository_root)
        entry_points = RepositoryManager.get_entry_points(repository_root=repository_root)
        topology = RepositoryManager.get_topology(repository_root=repository_root)
        dependency_graph = RepositoryManager.build_dependency_graph(repo_path=repository_root)
        config_files = RepositoryManager.scan_config_files(repository_root=repository_root)

        params = {
                "repository_root": str(repository_root),
                "commit_hash": commit_hash,
                "languages": languages,
                "entry_points": entry_points,
                "topology": topology,
                "dependency_graph": dependency_graph,
                "config_files": config_files
                }
        full_params = {"artefact_id": uuid.uuid4(),
                       "execution_id": execution_id,
                       "producer": "system",
                       "timestamp": datetime.now(),
                       "metadata": None,
                       "payload": commit_hash,
                       "caller": "system"}
        full_params.update(params)

        logging.info(f"[REPO ARTEFACT] Producer: RepositoryManager | Repository Root: {repository_root} | Commit Hash: {commit_hash} | Languages: {",".join(languages) if languages else None} | N Entry Points: {len(entry_points) if entry_points else None} | Topology: {len(topology)} | Dependency Graph: {len(dependency_graph) if dependency_graph else None} | N Config Files: {len(config_files) if config_files else None}")

        repo_artefact = ArtefactFactory.builder(artefact_type=RepositoryArtefact, params=full_params, artefact_store=artefact_store)

    @staticmethod
    def scan_config_files(repository_root: str) -> List[str] | None:

        CONFIG_EXTENSIONS = {".json", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".xml", ".properties", ".env"}
        CONFIG_FILENAMES = {"dockerfile", "makerfile", "pipfile", "pipfile.lock", "gemfile", "vagrantfile", "procfile", "pyproject.toml"}
        IGNORE_DIRS = {".git", ".hg", ".svn", "node_modules", "venv", ".venv", "__pycache__", "build", "dist", ".idea", ".vscode"}

        repository_root = os.path.abspath(repository_root)
        config_files = []

        if not os.path.isdir(repository_root):
            return None

        for root, dirs, files in os.walk(repository_root):

            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:

                file_lower = file.lower()
                file_name, file_ext = os.path.splitext(file_lower)
                is_dotfile_config = file_lower.startswith(".")
                is_known_filename = file_lower in CONFIG_FILENAMES
                has_config_extension = file_ext in CONFIG_EXTENSIONS

                if is_dotfile_config or is_known_filename or has_config_extension:
                    full_path = os.path.join(root, file)
                    config_files.append(full_path)

        return config_files
    
    @staticmethod
    def get_commit_hash() -> str | None:
        try:
            response = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, text=True, capture_output=True, timeout=120)
            logging.info(f"[COMMIT HASH] Producer: RepositoryManager | Command: git rev-parse HEAD | Hash: {response.stdout}")
            return response.stdout if response.stdout else None
        except subprocess.TimeoutExpired as e:
            logging.error(f"[COMMIT HASH ERROR] Producer: RepositoryManager | Command: git rev-parse HEAD | Reason: Timeout | Error: {e}")
            return None
        except Exception as e:
            logging.error(f"[COMMIT HASH ERROR] Producer: RepositoryManager | Command: git rev-parse HEAD | Reason: Error | Error: {e}")
            return None

    @staticmethod
    def get_language_dict():
        language_dict = {
                ".py": "python",
                ".java": "java",
                ".cpp": "cpp",
                ".ts": "typescript",
                ".js": "javascript",
                ".sql": "sql",
                ".c": "c",
                ".h": "c/cpp",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
                ".rb": "ruby",
                ".php": "php",
                ".swift": "swift",
                ".kt": "kotlin",
                ".sh": "shell"
                }
        return language_dict

    @staticmethod
    def get_languages(repository_root: str) -> List[str]:
        languages_set = set()
        repository_root = os.path.abspath(repository_root)
        language_dict = RepositoryManager.get_language_dict()

        for root, dirs, files in os.walk(repository_root):
            for filename in files:
                ext = Path(filename).suffix.lower()
                lang = language_dict.get(ext)
                if lang:
                    languages_set.add(lang)
        return sorted(languages_set)


    @staticmethod
    def get_entry_points(repository_root: str) -> Dict[str, str]:
        repository_root = os.path.abspath(repository_root)
        console_scripts = entrypoints.get_group_all('console_scripts')
        return console_scripts
    
    @staticmethod
    def get_topology(repository_root: str) -> Dict[str, Any]:
        topology = {}
        repository_root = os.path.abspath(repository_root)
        topology[repository_root] = [RepositoryManager.get_topology(os.path.join(repository_root, child)) if os.path.isdir(os.path.join(repository_root, child)) else child for child in os.listdir(repository_root)]
        return topology

    @staticmethod
    def get_typed_topology(repository_root: str) -> Dict[str, Any]:
        repository_root = os.path.abspath(repository_root)
        d = {"name": os.path.basename(repository_root)}
        if os.path.isdir(repository_root):
            d["type"] = "directory"
            d["children"] = [RepositoryManager.get_typed_topology(repository_root=os.path.join(repository_root, child)) for child in os.listdir(repository_root)]
        else:
            d["type"] = "file"
        return d

    @staticmethod
    def dict_to_json(d: Dict[str, Any]) -> Any:
        return json.dumps(d)
    
    @staticmethod
    def extract_imports_from_file(file_path: Path, repo_root: Path) -> List[str]:
        """
        Parses a python file and extracts all imported module names
        """
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError):
            # skip files with syntax errors or unreadable encoding
            return []

        for node in ast.walk(tree):
            # handle standard imports like 'import os'
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name) 
            
            # handle from imports
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                prefix = "." * node.level

                if module:
                    imports.append(f"{prefix}{module}".lstrip("."))
                else:
                    imports.append(prefix.strip(".") or ".")
        return imports
    
    @staticmethod
    def get_module_name(file_path: Path, repo_root: Path) -> str:
        """Converts a path into a python dot notation string"""
        relative_path = file_path.relative_to(repo_root)
        if relative_path.name == "__init__.py":
            module_parts = relative_path.parent.parts
        else:
            module_parts = relative_path.with_suffix("").parts
        return ".".join(module_parts)

    @staticmethod
    def build_dependency_graph(repo_path: str) -> Dict:
        repo_root = Path(repo_path).resolve()
        graph = {}
        file_mapping = {}

        # Discover all python files and map their paths to module names
        for root, _, files in os.walk(repo_root):
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root)/file
                    module_name = RepositoryManager.get_module_name(file_path=full_path, repo_root=repo_root)
                    if module_name == "":
                        module_name = repo_root.name
                    file_mapping[full_path] = module_name
                    graph[module_name] = []

        # Parse imports and filter for internal repository modules
        internal_modules = set(graph.keys())

        for file_path, module_name in file_mapping.items():
            found_imports = RepositoryManager.extract_imports_from_file(file_path=file_path, repo_root=repo_root)
            dependencies = set()

            for imp in found_imports:
                # Check if the import matches an internal module exactly
                for internal_mod in internal_modules:
                    if imp == internal_mod or imp.startswith(internal_mod+"."):
                        dependencies.add(internal_mod)

            # Remove self dependencies if any
            dependencies.discard(module_name)
            graph[module_name] = sorted(list(dependencies))
        return graph
