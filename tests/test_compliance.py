import os
import py_compile
import pytest

def test_rule_repo_size_under_10mb():
    """Validates Hack2Skill Rule: The repository size must be less than 10 MB."""
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total_bytes = 0
    for root, dirs, files in os.walk(repo_dir):
        # Skip git metadata
        if ".git" in root or ".pytest_cache" in root or "__pycache__" in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            total_bytes += os.path.getsize(fp)

    total_mb = total_bytes / (1024 * 1024)
    print(f"Total codebase size: {round(total_mb, 3)} MB")
    assert total_mb < 10.0, f"Repository exceeded 10 MB limit! Size: {total_mb} MB"

def test_security_gitignore_protects_env():
    """Validates that .env is explicitly protected in .gitignore to prevent secret leaks."""
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gitignore_path = os.path.join(repo_dir, ".gitignore")
    assert os.path.exists(gitignore_path), ".gitignore file is missing!"
    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert ".env" in content, ".env must be listed in .gitignore!"

def test_required_files_exist():
    """Validates that all essential components required by judges are present."""
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_files = [
        "app.py",
        "README.md",
        "SECURITY.md",
        "ACCESSIBILITY.md",
        ".github/workflows/ci.yml",
        "requirements.txt",
        "index.html",
        "utils/ai_helpers.py",
        "utils/doc_parser.py",
        "utils/simulation_view.py"
    ]
    for rf in required_files:
        path = os.path.join(repo_dir, rf)
        assert os.path.exists(path), f"Required project file missing: {rf}"

def test_app_syntax_compilation():
    """Validates that app.py compiles cleanly with zero syntax errors."""
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(repo_dir, "app.py")
    # py_compile will raise py_compile.PyCompileError on syntax error
    py_compile.compile(app_path, doraise=True)
