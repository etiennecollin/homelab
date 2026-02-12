# Authelia

## Configuration

Create the `./config/secrets` directory and create the following files:

- `./config/secrets/jwt`
- `./config/secrets/session_secret`
- `./config/secrets/storage_encryption_key`

Fill them with random 128+ char keys.

## Hashing passwords

To compute the hash of user passwords (`./config/authelia/users_database.yml`), when Authelia is running, run:

```bash
docker compose --env-file ../secret.env exec authelia authelia crypto hash generate
```

