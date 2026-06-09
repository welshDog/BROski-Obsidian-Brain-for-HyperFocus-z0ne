# HyperAgent Graduate Bundle

## Run (standalone)
```bash
docker compose -f docker-compose.agents.yml up -d --build
```

## Join HyperCode V2.4 network
Find the real network name:
```bash
docker network ls | findstr agents-net
```

Then edit `docker-compose.agents.yml` to:
```yaml
networks:
  agents-net:
    external: true
    name: hypercode-v2-4_agents-net
```
