# Floci Local Workflow

## Start Floci

```bash
docker compose up -d
```

## Export local AWS environment

```bash
source .env.example
```

or:

```bash
eval $(make floci-env)
```

## Use AWS CLI locally

```bash
aws --endpoint-url http://localhost:4566 s3 ls
```

The credentials are fake local values. Any non-empty values work for the emulator.

## Stop Floci

```bash
docker compose down
```

## Persistence

The Phase 1 default is memory mode for fast, clean runs. Later phases may add persistent/hybrid profiles for demos that preserve local state.
