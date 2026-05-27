# EKS and OKE Comparison

This document compares AWS Elastic Kubernetes Service (EKS) with Oracle Kubernetes Engine (OKE) for a DevOps engineer who already works with OCI and wants to transfer Kubernetes platform knowledge into AWS.

## Local-only boundary

This repository does not deploy a real EKS or OKE cluster. Phase 11 adds portable Kubernetes manifests and local validation so the same workload shape can be discussed across both providers.

Floci can expose an EKS-shaped local service backed by k3s, but this phase intentionally starts with manifests and static validation first. A future phase can run a live Floci EKS/k3s demo after explicit approval.

## Mental model

Kubernetes concepts are mostly provider-neutral. EKS and OKE differ mainly in the cloud integrations around the cluster:

- identity and workload access to cloud APIs;
- VPC/VCN networking and CNI behavior;
- load balancer controllers and ingress integration;
- node pool lifecycle and autoscaling;
- logging, metrics, audit, and cost tooling;
- image registries and secret managers.

## High-level mapping

| Area | AWS / EKS | OCI / OKE | What to compare in interviews |
| --- | --- | --- | --- |
| Managed Kubernetes | EKS cluster | OKE cluster | Managed control plane, version upgrades, API endpoint access. |
| Worker capacity | Managed node groups, self-managed nodes, Fargate profiles | Node pools, virtual nodes depending on region/features | Scaling, patching, AMIs/images, labels/taints, capacity types. |
| Container registry | ECR | OCIR | Image lifecycle, scanning, auth, promotion. |
| Workload identity | IRSA or EKS Pod Identity | OKE Workload Identity / OCI resource principals patterns | How pods access cloud APIs without static keys. |
| Network base | VPC | VCN | CIDR, subnets, route tables, NAT, private endpoints. |
| Pod networking | Amazon VPC CNI, alternatives such as Cilium/Calico | OCI VCN-native pod networking or supported CNIs | IP allocation, pod routability, network policy support. |
| Service LoadBalancer | NLB/CLB via service annotations, AWS Load Balancer Controller | OCI Load Balancer / Network Load Balancer integrations | Public/private LBs, annotations, health checks, TLS. |
| Ingress | AWS Load Balancer Controller for ALB/NLB, NGINX, Gateway API | OCI Native Ingress Controller, NGINX, Gateway API | L7 routing, TLS, controller ownership, annotations. |
| Observability | CloudWatch Container Insights, CloudWatch Logs, Prometheus/Grafana | OCI Logging/Monitoring, Prometheus/Grafana | Metrics, logs, dashboards, alarms, retention. |
| Secrets | AWS Secrets Manager, SSM Parameter Store, External Secrets | OCI Vault, External Secrets | Rotation, mounting/injection, avoiding plaintext secrets. |
| IAM/RBAC boundary | AWS IAM controls cluster/API access plus Kubernetes RBAC | OCI IAM controls cluster/API access plus Kubernetes RBAC | Two-layer authorization model. |
| Autoscaling | HPA/VPA, Cluster Autoscaler, Karpenter | HPA/VPA, Cluster Autoscaler/node pool scaling | Pod scaling vs node scaling and cost impact. |
| Audit | EKS control plane logs, CloudTrail | OKE control plane/audit options, OCI Audit | Who changed what, API server logs, compliance evidence. |

## Common Kubernetes baseline

These resources are intentionally portable between EKS and OKE:

- `Namespace`
- `ServiceAccount`
- `ConfigMap`
- `Deployment`
- `Service`
- `HorizontalPodAutoscaler`
- `NetworkPolicy`

The files under `k8s/base/` model this common baseline. Provider-specific overlays under `k8s/overlays/` document where EKS and OKE differ without requiring real cloud credentials.

## Interview talking points

### What is the same between OKE and EKS?

The Kubernetes API and workload primitives are the same: deployments, services, pods, labels, selectors, probes, resource requests/limits, HPAs, namespaces, service accounts, and RBAC. A well-designed manifest should be mostly portable.

### What changes between providers?

The provider integrations change: cluster provisioning, worker node lifecycle, pod identity, container registry auth, load balancer controllers, network implementation, observability stack, secrets integration, and cost model.

### How would this lab map to real EKS?

A real EKS version would add Terraform for the EKS cluster, VPC/subnets, node group or Fargate profile, IAM roles, ECR repository, AWS Load Balancer Controller, metrics-server, CloudWatch integration, and optional external-secrets integration.

### How would this lab map to real OKE?

A real OKE version would add Terraform for VCN/subnets, OKE cluster, node pool, OCIR repository, OCI load balancer integration, OCI IAM policies/dynamic groups or workload identity, OCI Logging/Monitoring, and OCI Vault integration.

## What not to overclaim

Do not say this phase deploys real EKS or OKE. Say:

> This phase creates a portable Kubernetes baseline and documents how it maps to EKS and OKE. It is ready for a future live local Floci EKS/k3s demo or for real-cloud Terraform once explicitly approved.
