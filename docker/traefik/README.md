# Traefik

The Clouflare token requires:

- `Zone.Zone:Read`
- `Zone.DNS:Edit`

Create the `proxy` and `socket-proxy` networks

```bash
docker network create proxy
docker network create socket-proxy
```

Create `./config/acme.json` with permissions `600`

```bash
touch ./config/acme.json
chmod 600 ./config/acme.json
```
