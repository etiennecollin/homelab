# Traefik

The Clouflare token requires:

- `Zone.Zone:Read`
- `Zone.DNS:Edit`

Create the `proxy` network

```bash
docker network create proxy
```

Create `./config/acme.json` with permissions `600`

```bash
touch ./config/acme.json
chmod 600 ./config/acme.json
```
