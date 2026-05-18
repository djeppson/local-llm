# AGENTS.md

This instruction file provides critical context for agents working in this repository. All information here should be verified in the codebase before being used.

## Project Overview
These services provide a complete self-hosted local AI productivity solution
- **Ollama** as a local inference provider for LLM hosting
- **Open WebUI** provides chat interface and collaboration
- **SearXNG** as privacy-respecting search backend
- **OpenCode** for AI coding assistance
- **Nginx** and **AWS Route 53** for access by other systems on the local network

## Tech Stack
- **Arch Linux** host OS
- **Systemd** for service management
  - Uses standard systemd command format `systemctl [--user] <command> <service_name>`
  - For user service management the `--user` flag is required
  - Symbolic links to service configurations provided in this repo `*.service`
- **Podman** and **Podman Compose** (not Docker) for container management
  - Check status: `podman-compose ps` 
  - View logs: `podman-compose logs`
  - Note: Service status may not always reflect the latest file configurations

## Service Management
- User Service: `local-llm`
  - Open WebUI: http://localhost:3000
  - SearXNG: http://localhost:8411
- User Service: `ollama` with GPU acceleration via ROCm
  - Ollama API: http://localhost:11434
  - OpenAI-compatible API: http://localhost:11434/v1
  - Available models can be fetched from these endpoints:
    - Ollama tags endpoint: http://localhost:11434/api/tags
    - OpenAI models endpoint: http://localhost:11434/v1/models
- System Service: `nginx`
  - Open WebUI: https://dj7900-local.darrenjeppson.com/
  - Ollama: http://dj7900-local.darrenjeppson.com:11434
  - SearXNG: http://dj7900-local.darrenjeppson.com:8411

## Testing/Verification
- Test configuration by checking that services/containers are up and healthy
- Fetch service endpoints to confirm availability and expected responses
- Note: Endpoints are static and should remain consistent unless configuration changes
- Test endpoints in any order - clearly identify which ones fail to quickly diagnose service issues
