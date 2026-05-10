# Troubleshooting

## Common Issues

### Containers Won't Start

```bash
# Check for errors
podman compose logs

# Verify images exist
podman compose images

# Pull fresh images
podman compose pull
```

### Port Already in Use

If you see `port is already allocated` errors:

```bash
# Check what's using the port
ss -tlnp | grep -E '8411|3000|11434'

# Stop conflicting services
# Then restart the stack
podman compose down
podman compose up -d
```

### SearXNG Configuration Errors

SearXNG is strict about its configuration. Common issues:

1. **Secret key missing:** `core-config/secret_key` must exist and be non-empty
2. **Invalid settings.yml:** YAML syntax errors will prevent startup
3. **Permission issues:** Ensure `core-config/` is readable by your user

```bash
# Fix permissions
chmod -R u+rw core-config/

# Verify secret key exists
cat core-config/secret_key
```

### Open WebUI Can't Connect to Ollama

```bash
# Verify Ollama is running
systemctl --user status ollama

# Test the API
curl http://localhost:11434/api/tags

# Check Open WebUI logs for connection errors
podman compose logs open-webui
```

### Open WebUI Can't Connect to SearXNG

```bash
# Verify SearXNG is responding
curl http://localhost:8411/search?q=test&format=json

# Check SearXNG logs
podman compose logs searxng-core
```

### Systemd Service Issues

```bash
# Check service status
systemctl --user status local-llm

# View service logs
journalctl --user -u local-llm -f

# Restart the service
systemctl --user restart local-llm
```

### Service Doesn't Start on Boot

```bash
# Verify linger is enabled
loginctl show-user jeppson | grep Linger

# Enable if not set
loginctl enable-linger jeppson

# Verify service is enabled
systemctl --user is-enabled local-llm
```

### Podman Storage Issues

```bash
# Check disk space
df -h /home/jeppson/.local/share/containers

# Clean unused images and containers
podman system prune -a

# Verify storage driver
podman info | grep -A 5 "graphDriverName"
```

### Volume Permission Problems

```bash
# Fix volume permissions
podman volume inspect local-llm_core-data
podman volume inspect local-llm_valkey-data

# Recreate volumes if corrupted
podman compose down -v
podman compose up -d
```

## Diagnostic Commands

### Full Stack Status
```bash
# One-liner to check everything
echo "=== Containers ===" && podman ps --filter name=searxng --filter name=open-webui && echo "=== Systemd ===" && systemctl --user is-active local-llm && echo "=== Ports ===" && ss -tlnp | grep -E '8411|3000'
```

### Resource Usage
```bash
# Memory and CPU per container
podman stats --no-stream

# Disk usage by volumes
podman system df -v
```

### Network Connectivity
```bash
# Test SearXNG from inside Open WebUI container
podman exec open-webui curl -s http://localhost:8411/search?q=test

# Test Ollama from inside Open WebUI container
podman exec open-webui curl -s http://localhost:11434/api/tags
```

## Recovery Procedures

### Complete Reset
```bash
# Stop everything
systemctl --user stop local-llm
podman compose down -v

# Clean up
podman rm -f $(podman ps -aq --filter name=searxng) $(podman ps -aq --filter name=open-webui)
podman volume rm local-llm_core-data local-llm_valkey-data

# Fresh start
podman compose up -d
```

### Restore from Backup
```bash
# Restore volumes
podman volume import local-llm_core-data < core-data-backup.tar
podman volume import local-llm_valkey-data < valkey-data-backup.tar

# Restore config
tar xzf core-config-backup.tar.gz

# Restore Open WebUI data
tar xzf open-webui-data-backup.tar.gz -C /home/jeppson/.local/share/containers/storage/volumes/open-webui/

# Restart
podman compose up -d
```

## Getting Help

- [SearXNG Issues](https://github.com/searxng/searxng/issues)
- [Open WebUI Issues](https://github.com/open-webui/open-webui/issues)
- [Podman Issues](https://github.com/containers/podman/issues)
