# Java Datadog Agent Container

Running containerized Java applications with [Datadog's Application Performance Monitoring (APM)](https://docs.datadoghq.com/tracing/) requires Datadog's SDK (aka agent) that collects traces. The SDK needs to be downloaded from Datadog. Usually you want to avoid downloading the SDK every time you build your application's container image. Instead it is recommendable to use a base image that contains Java and the Datadog SDK. This repository contains the necessary scripts for creating such an image. Currently the scripts only rung on Linux and macOS. If you need Windows support, please [create an issue at GitHub](https://github.com/stefanbirkner/datadog-agent-container/issues).

## Usage

Choose a Java base image (e.g. `eclipse-temurin:26-jdk-alpine`) and run the command

    ./scripts/build-image.sh eclipse-temurin:26-jdk-alpine

A new image will be created locally.
