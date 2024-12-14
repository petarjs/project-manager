from pathlib import Path
from typing import TYPE_CHECKING, List, cast
import pytest

from project_manager.services.script_service import ScriptService

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


def test_execute_new_project_script_success(mocker: "MockerFixture") -> None:
    """Test successful execution of new project script."""
    # Setup
    script_service = ScriptService()
    mock_popen = mocker.patch("subprocess.Popen")
    mock_process = mocker.MagicMock()
    mock_process.stdout.readline.side_effect = ["Line 1\n", "Line 2\n", ""]
    mock_process.poll.return_value = 0
    mock_popen.return_value = mock_process
    
    # Mock Path.exists to return True
    mocker.patch("pathlib.Path.exists", return_value=True)

    # Create a list to capture output
    output_lines: List[str] = []
    
    # Execute
    result = script_service.execute_new_project_script(
        "testapp",
        "Test App",
        3000,
        0,
        lambda line: output_lines.append(line)
    )

    # Verify
    assert result is True
    assert output_lines == ["Line 1", "Line 2"]
    mock_popen.assert_called_once()
    
    # Get the actual environment variables passed to Popen
    call_kwargs = mock_popen.call_args[1]
    env = call_kwargs["env"]
    
    # Verify only our specific environment variables
    assert env["APP_NAME"] == "testapp"
    assert env["APP_NAME_PRETTY"] == "Test App"
    assert env["PORT"] == "3000"
    assert env["REDIS_DB"] == "0"


def test_execute_new_project_script_failure(mocker: "MockerFixture") -> None:
    """Test handling of script execution failure."""
    # Setup
    script_service = ScriptService()
    mock_popen = mocker.patch("subprocess.Popen")
    mock_process = mocker.MagicMock()
    mock_process.stdout.readline.side_effect = ["Error message\n", ""]
    mock_process.poll.return_value = 1
    mock_popen.return_value = mock_process
    
    # Mock Path.exists to return True
    mocker.patch("pathlib.Path.exists", return_value=True)

    # Execute
    output_lines: List[str] = []
    result = script_service.execute_new_project_script(
        "testapp",
        "Test App",
        3000,
        0,
        lambda line: output_lines.append(line)
    )

    # Verify
    assert result is False
    assert output_lines == ["Error message"]


def test_execute_new_project_script_missing_script(mocker: "MockerFixture") -> None:
    """Test handling of missing script file."""
    # Setup
    script_service = ScriptService()
    mocker.patch("pathlib.Path.exists", return_value=False)

    # Execute & Verify
    with pytest.raises(FileNotFoundError):
        script_service.execute_new_project_script("testapp", "Test App", 3000, 0)