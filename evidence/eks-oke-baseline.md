# EKS/OKE Kubernetes Baseline Evidence

## Scope

Phase 11 adds a local-only Kubernetes baseline for comparing EKS and OKE concepts. It does not deploy real AWS or OCI resources.

## Evidence commands

```bash
make k8s-validate
git diff --check
```

Expected result:

- required Kubernetes manifests exist;
- static YAML checks pass;
- optional `kubectl kustomize` runs if `kubectl` is installed;
- no live cluster is required.

## What this proves

- The lab has a provider-neutral Kubernetes workload shape.
- The same baseline can be discussed against EKS and OKE.
- Cloud-specific integrations are documented separately from generic Kubernetes primitives.

## Future evidence

A future Floci EKS/k3s live demo can capture:

- local EKS-shaped cluster created;
- Kubernetes nodes ready;
- overlay applied;
- deployment rollout successful;
- service reachable inside the cluster;
- HPA and NetworkPolicy objects present.
