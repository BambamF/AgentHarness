from types import SimpleNamespace
from unittest.mock import Mock, patch
import pytest

from src.permissions.permissions import PermissionManager
from src.permissions.permission_level import PermissionLevel

@pytest.fixture
def permission_manager():
    return PermissionManager()

@pytest.fixture
def action():
    return SimpleNamespace(input={}, execution_id="test-execution", producer="agent", caller="test")

def test_get_command_target_simple_command(permission_manager):
    target = permission_manager.get_command_target("ls -la")

    assert target == "ls"

def test_get_command_target_git_command(permission_manager):
    target = permission_manager.get_command_target("status", prefix="git")

    assert target == "git status"

def test_get_command_target_subcommand(permission_manager):
    target = permission_manager.get_command_target("pip install pytest")

    assert target == "pip install"

def test_get_command_targets_and_chain(permission_manager):
    targets = permission_manager.get_command_targets("ls -la && cat README.md") 

    assert targets == ["ls", "cat"]

def test_get_command_targets_semicolon_chain(permission_manager):
    targets = permission_manager.get_command_targets("echo hello; cat README.md")

    assert targets == ["echo", "cat"]

def test_get_command_targets_pipe_chain(permission_manager):
    targets = permission_manager.get_command_targets("cat README.md | grep hello")

    assert targets == ["cat", "grep"]

def test_get_command_targets_or_chain(permission_manager):
    targets = permission_manager.get_command_targets("python test.py || echo failed")

    assert targets == ["python", "echo"]

@pytest.mark.parametrize(
        "command",
        ["echo hello && sudo ls",
         "ls; sudo ls",
         "cat file || sudo rm file",
         "echo hello | sudo cat",
         "python test.py && shutdown",
         "ls && reboot"]
        )

def test_chained_blocked_command_is_blocked(permission_manager, command):
    assert permission_manager.is_blocked_command(command) is True


@pytest.mark.parametrize(
        "command",
        ["ls && cat README.md",
         "echo hello; grep test file.txt",
         "git status && git log",
         "python test.py || echo failed"
         ]
        )

def test_chained_safe_commands_are_not_blocked(permission_manager, command):
    assert permission_manager.is_blocked_command(command) is False


@pytest.mark.parametrize(
        "command",
        ["rm -rf /",
         "echo hello && rm -rf /",
         "ls; rm -rf /",
         "cat file | rm -rf /",
         "echo x > /dev/sda",
         ":(){ :|:& };:"
         ]
        )

def test_dangerous_commands_are_blocked(permission_manager, command):
    assert permission_manager.is_blocked_command(command) is True

def test_malformed_shell_command_is_not_safe(permission_manager):
    command = "echo 'unterminated"
    targets = permission_manager.get_command_targets(command)

    assert targets
