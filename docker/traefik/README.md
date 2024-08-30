# Traefik

Create the `proxy` network

```bash
docker network create proxy
```

Create `./config/acme_production.json` and `./config/acme_staging.json` with permissions `600`

```bash
touch ./config/acme_production.json ./config/acme_staging.json
chmod 600 ./config/acme_production.json ./config/acme_staging.json
```
