from pathlib import Path
import ast
import json
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.repository.repository import RepositoryArtefact
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Set
from  importlib.metadata import entry_points as discover_entry_points
from collections import defaultdict
import os
import logging
import uuid
from uuid import UUID


class RepositoryManager:
    IGNORE_DIRS = {
            ".git",
            ".hg",
            ".svn",
            ".venv",
            "venv",
            "env",
            "node_modules",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "build",
            "dist",
            ".tox",
            ".idea",
            "site-packages",
            ".vscode"
            }

    IGNORE_FILES = {".DS_Store"}

    MAX_FILES = 256_000

    @staticmethod
    def get_topology(repository_root:str, max_depth: int = 4) -> dict:
        root = Path(repository_root).resolve()

        def build_tree(directory: Path, depth: int) -> dict:
            result = {
                    "name": directory.name,
                    "type": "directory",
                    "children": []
                    }
            if depth >= max_depth:
                result["truncated"] = True
                return result

            try:
                children = sorted(directory.iterdir(), key=lambda path: (not path.is_dir(), path.name.lower()))
            except OSError:
                result["error"] = "unreadable"
                return result

            for child in children:
                if child.is_symlink():
                    continue
                if child.is_dir() and child.name in RepositoryManager.IGNORE_DIRS:
                    continue

                if child.is_dir():
                    result["children"].append(build_tree(child, depth+1))
                else:
                    result["children"].append({"name": child.name, "type": "file"})
            return result
        return build_tree(root, depth=0)

    @staticmethod
    def get_entry_points(repository_root: str) -> dict[str, str]:
        discovered = discover_entry_points()
        result = {}

        for entry_point in discovered:
            result[entry_point.name] = entry_point.value
        return result

    @staticmethod
    def get_language_dict():
        return {
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

    @staticmethod
    def get_languages(repository_root: str) -> list[str]:
        languages = set()
        language_dict = RepositoryManager.get_language_dict()

        for path in RepositoryManager.iter_repository_files(repository_root):
            language = language_dict.get(path.suffix.lower())
            if language:
                languages.add(language)
        return sorted(languages)

    @staticmethod
    def iter_repository_files(repository_root: str):
        root = Path(repository_root).resolve()

        for path in root.rglob("*"):
            if any(path in IGNORE_DIRS for part in path.parts):
                continue
            if path.name in IGNORE_FILES:
                continue
            if path.is_file():
                yield path

    @staticmethod
    def build_repository_index(repository_root: str) -> dict[str, Any]:
        root = Path(repository_root).resolve()
        files = []
        config_files = []
        languages = set()

        language_map = RepositoryManager.get_language_dict()

        for path in iter_repository_files(repository_root):
            relative_path = path.relative_to(root).as_posix()
            suffix = path.suffix.lower()

            try:
                size = path.stat.st_size()
            except OSError:
                continue

            files.append({
                "path": relative_path,
                "type": "file",
                "size": size
                })

            language = languages_map.get(suffix)
            if language:
                languages.add(language)

            if (suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"} 
                or path.name.lower() in {"dockerfile", "makefile", "pyproject.toml", "package.json", "requirements.txt"}):
                config_files.append(relative_path)

        return {
                "repository_root": str(root),
                "languages": sorted(languages),
                "file_count": len(files),
                "config_files": sorted(config_files),
                "files": files
                }

    @staticmethod
    def get_repository_artefact(repository_root: str, artefact_store: ArtefactStore, execution_id: UUID):

        commit_hash = RepositoryManager.get_commit_hash(repository_root)
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

        repo_artefact = ArtefactFactory.builder(artefact_type=RepositoryArtefact, params=full_params, artefact_store=artefact_store, execution_id=execution_id, caller="system")
        return repo_artefact

    @staticmethod
    def get_commit_hash(repository_root) -> str | None:
        try:
            response = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repository_root, check=True, text=True, capture_output=True, timeout=120)
            commit_hash = response.stdout.strip()
            logging.info(f"[COMMIT HASH] Producer: Repository Manager | Command: git rev-parse HEAD | Repository: {repository_root} | Hash: {commit_hash}")
            return commit_hash or None
        except subprocess.TimeoutExpired as e:
            logging.exception(f"[COMMIT HASH] Producer: Repository Manager | Command: git rev-parse HEAD | Reason: Timeout | Repository: {repository_root} | Exception: {str(e)}")
            return None
        except Exception as e: 
            logging.exception(f"[COMMIT HASH] Producer: Repository Manager | Command: git rev-parse HEAD | Reason: Exception encountered | Repository: {repository_root} | Exception: {str(e)}")
            return None

    

    @staticmethod
    def scan_config_files(repository_root: str) -> List[str] | None:

        CONFIG_EXTENSIONS = {".json", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".xml", ".properties", ".env"}
        CONFIG_FILENAMES = {"dockerfile", "makerfile", "pipfile", "pipfile.lock", "gemfile", "vagrantfile", "procfile", "pyproject.toml"}
        IGNORE_DIRS = {".git", ".hg", ".svn", "node_modules", "venv", ".venv", "__pycache__", "build", "dist", ".idea", ".vscode", ".gitignore"}

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


            language = languages_map.get(suffix)
            if language:
                languages.add(language)

            if (suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"} 
                or path.name.lower() in {"dockerfile", "makefile", "pyproject.toml", "package.json", "requirements.txt"}):
                config_files.append(relative_path)

        return {
                "repository_root": str(root),
                "languages": sorted(languages),
                "file_count": len(files),
                "config_files": sorted(config_files),
                "files": files
                }


    @staticmethod
    def extract_imports_from_file(file_path, repo_root):
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

        for file_path in RepositoryManager.iter_repository_files(repo_root):
            if file_path.suffix != ".py":
                continue

            module_name = RepositoryManager.get_module_name(file_path=file_path, repo_root=repo_root)

            if not module_name:
                module_name = repo_root.name

            file_mapping[file_path] = module_name
            graph[module_name] = []

        internal_modules = set(graph)
        for file_path, module_name in file_mapping.items():
            imports = RepositoryManager.extract_imports_from_file(file_path, repo_root)
            dependencies = set()
            for imported_module in imports:
                for internal_modules in internal_modules:
                    if imported_module == internal_module or imported_module.startswith(internal_module + "."):
                        dependencies.add(internal_module)
            dependencies.discard(module_name)
            graph[module_name] = sorted(dependencies)

        return graph
