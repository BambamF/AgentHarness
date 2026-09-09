from pathlib import Path
from src.repositories.repository_manager import RepositoryManager

def test_get_topology(tmp_path):
    # set up the paths
    (tmp_path/"src").mkdir()
    (tmp_path/"src"/"main.py").touch()
    (tmp_path/"README.md").touch()

    # call the topology getter method
    topology = RepositoryManager.get_topology(str(tmp_path))

    # test assertions
    assert topology["type"] == "directory"
    assert topology["name"] == tmp_path.name

    children = {child["name"]: child for child in topology["children"]}

    assert "src" in children
    assert "README.md" in children

    assert children["src"]["type"] == "directory"
    assert children["README.md"]["type"] == "file"

def test_get_topology_ignores_directories(tmp_path):
    # set up the paths
    (tmp_path/"src").mkdir()
    (tmp_path/"src"/"main.py").touch()

    (tmp_path/".git").mkdir()
    (tmp_path/".git"/"config").touch()

    (tmp_path/"node_modules").mkdir()
    (tmp_path/"node_modules"/"package.js").touch()

    (tmp_path/"README.md").touch()
    
    # call the topology getter
    topology = RepositoryManager.get_topology(str(tmp_path))

    # test assertions
    names = {child["name"] for child in topology["children"]}

    assert "src" in names
    assert "README.md" in names

    assert ".git" not in names
    assert "node_modules" not in names

def test_iter_repository_files(tmp_path):
    # set up the paths
    (tmp_path/"src").mkdir()
    
    source_file = tmp_path/"src"/"main.py"
    source_file.touch()

    (tmp_path/".git").mkdir()
    ignored_file = tmp_path/".git"/"config"
    ignored_file.touch()

    (tmp_path/"node_modules").mkdir()
    ignored_second = tmp_path/"node_modules"/"package.js"
    ignored_second.touch()

    # get the repo files
    files = list(RepositoryManager.iter_repository_files(str(tmp_path)))

    # test assertions
    assert source_file in files
    assert ignored_file not in files
    assert ignored_second not in files

def test_get_languages(tmp_path):
    # set up the paths
    (tmp_path/"main.py").touch()
    (tmp_path/"src.java").touch()
    (tmp_path/"quert.sql").touch()

    # get the languages
    languages = list(RepositoryManager.get_languages(str(tmp_path)))

    # test assertions
    assert "java" in languages
    assert "python" in languages
    assert "sql" in languages
