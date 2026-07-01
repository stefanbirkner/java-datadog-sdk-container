#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14.5"
# dependencies = []
# ///

import argparse
import json
import os
import subprocess
from textwrap import dedent
from typing import Tuple
import urllib.request


def fetch_sdk_release_info() -> Tuple[str, str]:
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


def image_exists(image_name_with_tag: str) -> bool:
    result = subprocess.run(
        [
            "podman",
            "pull",
            image_name_with_tag,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def write_containerfile(base_image: str, url: str) -> str:
    filename = "Containerfile"
    with open(filename, "w") as f:
        f.write(dedent(f"""\
            FROM {base_image}

            ADD '{url}' /opt/dd-java-agent.jar
            """))
    return filename


def build_image(image_name_with_tag: str) -> None:
    subprocess.run(
        [
            "podman",
            "build",
            "-t",
            image_name_with_tag,
            ".",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def push_image(image_name_with_tag: str) -> None:
    subprocess.run(
        [
            "podman",
            "push",
            image_name_with_tag,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )

def add_digest(image_name_with_tag: str) -> str:
    result = subprocess.run(
        [
            "podman",
            "inspect",
            "--format",
            "{{.Digest}}",
            image_name_with_tag,
        ],
        check=True,
        capture_output=True,
    )
    digest = result.stdout.decode().strip()
    return image_name_with_tag + "@" + digest


def extract_image_name_and_tag(base_image: str) -> Tuple[str, str]:
    # A container image reference consists of several components:
    # [HOST[:PORT]/]NAMESPACE/REPOSITORY[:TAG]
    repository_and_tag = base_image.split("/")[-1]
    return repository_and_tag.split(":")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_image", nargs="+")
    parser.add_argument("-rn", "--registry_and_namespace")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    version, download_url = fetch_sdk_release_info()
    for base_image in args.base_image:
        base_image_repository, base_image_tag = extract_image_name_and_tag(base_image)
        image_name_with_tag = f"{args.registry_and_namespace}/{base_image_repository}-datadog:{base_image_tag}-{version}-datadog"
        if not image_exists(image_name_with_tag):
            containerfile = write_containerfile(base_image, download_url)
            build_image(image_name_with_tag)
            os.remove(containerfile)
            push_image(image_name_with_tag)
            image_name_with_tag_and_digest = add_digest(image_name_with_tag)
            print(image_name_with_tag_and_digest)


if __name__ == "__main__":
    main()
