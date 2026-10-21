"""Deployment must reject builds that would erase the company reference corpus."""
from pathlib import Path
import os
import runpy
import shutil
import subprocess

ROOT = Path(__file__).parents[1]


def test_deploy_refuses_empty_corpus_before_remote_access(tmp_path):
    (tmp_path / "deploy").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "dist").mkdir()
    shutil.copy2(ROOT / "deploy/deploy.sh", tmp_path / "deploy/deploy.sh")
    shutil.copy2(ROOT / "scripts/check_site.py", tmp_path / "scripts/check_site.py")
    (tmp_path / "dist/index.html").write_text('<link rel="canonical" href="https://defunctcompanies.com/" />')
    (tmp_path / "dist/privacy.html").write_text("Privacy")
    (tmp_path / "dist/sitemap.xml").write_text('<loc>https://defunctcompanies.com/</loc>')
    binaries = tmp_path / "bin"
    binaries.mkdir()
    marker = tmp_path / "remote-command-attempted"
    (binaries / "ssh").write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 97\n')
    (binaries / "rsync").write_text('#!/bin/sh\necho "rsync version 3"\n')
    for binary in binaries.iterdir():
        binary.chmod(0o755)
    result = subprocess.run(
        ["bash", str(tmp_path / "deploy/deploy.sh")],
        env={**os.environ, "DEPLOY_HOST": "never-connect", "BUILD": "0", "PATH": str(binaries) + os.pathsep + os.environ["PATH"]},
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "No company pages" in result.stderr
    assert not marker.exists()


def test_link_guard_prevents_missing_privacy_from_shipping(tmp_path):
    check = runpy.run_path(str(ROOT / "scripts/check_site.py"))["check"]
    (tmp_path / "companies").mkdir()
    (tmp_path / "index.html").write_text('<a href="companies/brand.html">Brand</a>')
    (tmp_path / "companies/brand.html").write_text('<a href="../privacy.html?from=brand#contact">Privacy</a>')
    assert any("privacy.html" in error for error in check(tmp_path))
    (tmp_path / "privacy.html").write_text('<a href="/index.html">Home</a>')
    assert check(tmp_path) == []
