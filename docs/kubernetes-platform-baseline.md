# Kubernetes Platform Baseline

Phase 11 introduces a local-only Kubernetes baseline for comparing EKS and OKE.

## Goal

Create a small, portable workload shape that exercises the Kubernetes concepts a DevOps engineer should be able to explain before discussing cloud-specific integrations.

## Files

| File | Purpose |
| --- | --- |
| `k8s/base/namespace.yaml` | Isolates the lab workload in `floci-cloud-lab`. |
| `k8s/base/serviceaccount.yaml` | Models workload identity attachment point. |
| `k8s/base/configmap.yaml` | Keeps runtime configuration outside the image. |
| `k8s/base/deployment.yaml` | Runs the local API container shape with probes and resource requests/limits. |
| `k8s/base/service.yaml` | Exposes the deployment inside the cluster. |
| `k8s/base/hpa.yaml` | Models pod autoscaling. |
| `k8s/base/networkpolicy.yaml` | Models default ingress restriction for the app. |
| `k8s/base/kustomization.yaml` | Builds the provider-neutral base. |
| `k8s/overlays/eks-local/kustomization.yaml` | EKS/Floci-local study overlay. |
| `k8s/overlays/oke-reference/kustomization.yaml` | OKE reference comparison overlay. |

## Local validation

Run:

```bash
make k8s-validate
```

The validation is intentionally safe. It does not require a live Kubernetes cluster, real AWS credentials, or OCI credentials. If `kubectl` is installed, the script also runs `kubectl kustomize` for both overlays. If not, it performs static checks and clearly reports the optional skip.

## Baseline workload shape

The baseline models the app as if it were running in Kubernetes:

- two replicas;
- `/health` readiness and liveness probes;
- explicit CPU and memory requests/limits;
- service account as the future cloud identity attachment point;
- config map for local endpoint/table/bucket names;
- internal `ClusterIP` service;
- HPA model;
- NetworkPolicy model.

## Why not start with real EKS?

The learning goal is OKE to EKS transfer. The first step is understanding what is plain Kubernetes and what is cloud integration. Starting with portable manifests keeps the concepts clear.

## Future live Floci EKS/k3s demo

Floci supports an EKS-shaped service backed by k3s. A future phase can add a live demo that:

1. starts Floci with Docker-backed EKS support;
2. creates an EKS-shaped local cluster;
3. retrieves kubeconfig;
4. applies `k8s/overlays/eks-local`;
5. verifies rollout, service endpoints, and HPA objects;
6. captures evidence.

That future phase should remain local-only unless real AWS/OCI deployment is explicitly approved.
