# Authelia

## Configuration

Create the `./config/secrets` directory and create the following files:

- `./config/secrets/jwt`
- `./config/secrets/session_secret`
- `./config/secrets/storage_encryption_key`

## Hashing passwords

When Authelia is running:

```bash
docker compose --env-file ../secret.env exec authelia authelia crypto hash generate
```

