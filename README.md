# Java Datadog SDK Container

Running containerized Java applications with [Datadog's Application Performance Monitoring (APM)](https://docs.datadoghq.com/tracing/) requires the [Datadog SDK](https://docs.datadoghq.com/tracing/trace_collection/dd_libraries/java) to collect traces. The SDK has to be downloaded from Datadog — but instead of downloading it on every build, you can use a base image that bundles Java and the Datadog SDK together.

This repository maintains such an image and updates it automatically whenever a new SDK version is published. To get started, clone or fork this repository to your GitHub account.

The original source of this repository is:
- https://github.com/stefanbirkner/java-datadog-sdk-container


## How it works

It queries the [dd-trace-java GitHub releases API](https://api.github.com/repos/DataDog/dd-trace-java/releases/latest) to determine the latest Datadog SDK version. It then checks whether an image for that version already exists in the registry. If not, it builds a new image — starting from your chosen Java base image and adding the SDK at `/opt/dd-java-agent.jar` — and pushes it to the registry.


## Usage

### Using the Datadog SDK in your container

The container images store the Datadog SDK at `/opt/dd-java-agent.jar`. Start your Java application with:

    java -javaagent:/opt/dd-java-agent.jar -jar my_app.jar


### GitHub workflow

1. Clone or fork the repository.
2. Set your desired Java base image in `.github/workflows/build_image.yml`.

The workflow runs every hour. It builds an initial image on first run, then creates a new image whenever a new Datadog SDK version is available.

Image names follow this pattern:

    ghcr.io/<owner>/eclipse-temurin-datadog:26-jdk-alpine-1.63.0-datadog

#### Triggering additional actions

`build_image.py` writes the new image name, tag and digest to stdout, e.g.:

    ghcr.io/stefanbirkner/eclipse-temurin-datadog:26-jdk-alpine-1.63.0-datadog@sha256:0bf9aff42dce7d336dc70e410bdb9f1fc62ea200a3c25360ac335d00e9da6d7f

Nothing is written to stdout if the script didn't create a new image because the latest image is already up to date.

You can pipe the output to another command to trigger follow-up actions. For example, to send an email when a new image is built:

```yaml
- name: Build and push OCI container image
  run: uv run build_image.py --registry_and_namespace ghcr.io/${{ github.repository_owner }} eclipse-temurin:26-jdk-alpine | uv run send_mail.py
```


### Script only

`build_image.py` can also be used directly without a CI/CD system.

Choose a Java base image (e.g. `eclipse-temurin:26-jdk-alpine`) and run:

    uv run build_image.py --registry_and_namespace <registry>/<namespace> eclipse-temurin:26-jdk-alpine

A new image will be built and pushed to the specified registry.


#### Prerequisites

- [Python 3](https://www.python.org/)
- [Podman](https://podman.io/)
