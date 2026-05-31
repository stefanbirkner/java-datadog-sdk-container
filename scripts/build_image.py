#!/usr/bin/env python3

import json
import os
import subprocess
from typing import Tuple
import urllib.request


def fetch_agent_release_info() -> Tuple[str, str]:
    req = urllib.request.Request(
        "https://api.github.com/repos/DataDog/dd-trace-java/releases/latest"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            github_info = json.load(response)
            version = github_info.get("name")
            download_url = github_info.get("assets")[0].get("browser_download_url")
            return version, download_url
    except Exception as exc:
        raise RuntimeError(
            "Failed to fetch latest dd-java-agent version info from GitHub API"
        ) from exc


def create_dockerfile(url: str) -> str:
    with open("Dockerfile", "w") as f:
        f.write("FROM docker.io/eclipse-temurin:26-jdk-alpine\n\n")
        f.write(f"ADD '{url}' /opt/dd-java-agent.jar\n")
    return "Dockerfile"


def main() -> int:
    version, download_url = fetch_agent_release_info()
    dockerfile = create_dockerfile(download_url)
    tag_name = f"eclipse-temurin-datadog:26-jdk-alpine-{version}"
    subprocess.run(
        [
            "podman",
            "build",
            "-t",
            tag_name,
            ".",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    os.remove(dockerfile)
    print(tag_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
