from pathlib import Path
from ../harness/artefacts/artefact_store import ArtefactStore
from ../harness/artefacts/repository import RepositoryArtefact
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Set
import entrypoints
from collections import defaultdict

class RepositoryManager:

    def get_repository_artefact(self, repository_root: str | Path, logger: logging.logger) -> RepositoryArtefact:
        pass

    def get_commit_hash(self, logger: logging.logger) -> str | None:
        try:
            response = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, text=True, capture_output=True, timeout=120)
            logger.info(f"[COMMIT HASH] Producer: RepositoryManager | Command: git rev-parse HEAD | Hash: {response.stdout} | Timestamp: {datetime.now()}")
            return response.stdout if response.stdout else None
        except subprocess.TimeoutExpired as e:
            logger.error(f"[COMMIT HASH ERROR] Producer: RepositoryManager | Command: git rev-parse HEAD | Reason: Timeout | Error: {e} | Timestamp: {datetime.now()}")
            return None
        except Exception as e:
            logger.error(f"[COMMIT HASH ERROR] Producer: RepositoryManager | Command: git rev-parse HEAD | Reason: Error | Error: {e} | Timestamp: {datetime.now()}")
            return None

    def get_language_dict(self,):
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

    def get_repository_languages(self, repository_root: str | Path, languages_set: Set[string]) -> List[str]:
        
        language_dict = get_language_dict()

        for root, dirs, files in os.walk(repository_root):
            for filename in files:
                ext = Path(filename).suffix.lower()
                lang = language_dict.get(ext)_
                languages_set.add(lang)
        return sorted(languages_set)

    def get_repository_entry_points(self, repository_root: str | Path) -> Dict[str, str]:
        console_scripts = entrypoints.get_group_all('console_scripts')
        return console_scripts

    def get_repository_topology(self, repository_root: str | Path) -> Dict[str, Any]:
        d = {"name": os.path.basename(repositort_root)}
        if os.path.isdir(repository_root):
            d["type"] = "directory"
            d["children"] = [self.get_repository_topology(os.path.join(repository_root), child) for child in os.listdir(repository_root)]
        else:
            d["type"] = "file"
        return d

    def dict_to_json(self, d: Dict[str, Any]) -> Any:
        return json.dumps(d)

    def get_dependency_graph(self) -> Dict[str, Any]:
        graph_imports: Dict[str, Set[str]] = defaultdict(Set)
        graph_refs: Dict[str, Set[str]] = defaultdict(Set)
        node: Set[str] = Set()

        language_dict = get_language_dict()
