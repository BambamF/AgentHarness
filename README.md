# Harness Engineering for Agentic Code Generation

## A harness design for agentic code generation

This project proposes an agent harness engineered for repository scope code generation and error resolution.

### Model - Claude Opus 5

### Tech Used
* Language: Python
* Runtime: Docker container
* Runtime Image: python:3.12-slim

### Requirements
* Anthropic Claude Opus 5 API Key
* Docker
* pip (python package manager)
* Virtual Machine Environment (optional) - (VirtualBox recommended)
* Virtual Operating System (optional) - (Ubuntu Server recommended)

# IT IS HIGHLY RECOMMENDED YOU RUN THIS CODE IN A VIRTUAL MACHINE ENVIRONMENT, AGENT EXECUTIONS ARE CONTAINERISED BUT PRECAUTIONS ARE ADVISED.

## Quick Start

### Prerequisites
* Python (3.12 or 3.13)
* Anthropic API Key

### Installations - (bash)

Clone via HTTPS: 

git clone https://github.com/BambamF/AgentHarness.git

or

Clone via SSH:

git@github.com:BambamF/AgentHarness.git

### Change location into the root of the project

cd agent-harness

### Create a virtual environment

python -m .venv venv

### Activate the virtual environment

source .venv/bin/activate

### Install dependencies

pip install -r requirements.txt

### Run the program

PYTHONPATH=. python src/main.py


### Installations - (powershell)

Clone via HTTPS: 

git clone https://github.com/BambamF/AgentHarness.git

or...

Clone via SSH:

git@github.com:BambamF/AgentHarness.git

### Change location into the root of the project

Set-Location -Path agent-harness

### Create a virtual environment

python -m .venv venv

### Activate the virtual environment

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

then...

.\venv\Scripts\Activate.ps1

### Install dependencies

python -m pip install -r requirements.txt

### Run the program

$env:PYTHONPATH=. ; py src/main.py

## Interacting with the agent

Once you run the main script you should see a prompt with ">>" in the terminal.

This indicates the script has initialised successfully and you can procede to type your prompt in the terminal.

You can prompt the agent to write python code to fulfil your requirement.

## Architecture Overview

src
* agents: Contains the agents generation and reflection scripts
* harness: Contains the harness modules including artefact definitions, context and state scripts and the harness orchestrator loop
    * artefacts: Contains the artefact interface and subclasses (frozen dataclasses)
* logging: Contains the log file for documenting events
* memory: Contains the projects memory logic
* permissions: Contains the projects permissioning logic
* planner: Contains the agents planning script
* prompts: Contains the prompt handling logic
* repositories: Contains the repository management logic
* tools: contains the tool interface and subclasses (frozen dataclasses)
runtime: Contains the executions directory that holds the agent's execution environment, and the runtime code
tests: Contains the projects testing suite
Dockerfile: The configs for docker
pyproject.toml: configs for running module scripts
requirements.txt: dependencies for the project

## Testing 

bash

PYTHONPATH=. pytest -v tests/

powershell

$env:PYTHONPATH=. ; py -m pytest tests
