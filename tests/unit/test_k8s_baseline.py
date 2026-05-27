from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_kubernetes_baseline_files_exist() -> None:
    required = [
        "docs/eks-oke-comparison.md",
        "docs/kubernetes-platform-baseline.md",
        "k8s/base/namespace.yaml",
        "k8s/base/serviceaccount.yaml",
        "k8s/base/configmap.yaml",
        "k8s/base/deployment.yaml",
        "k8s/base/service.yaml",
        "k8s/base/hpa.yaml",
        "k8s/base/networkpolicy.yaml",
        "k8s/base/kustomization.yaml",
        "k8s/overlays/eks-local/kustomization.yaml",
        "k8s/overlays/oke-reference/kustomization.yaml",
        "scripts/k8s-validate.sh",
        "evidence/eks-oke-baseline.md",
    ]
    for path in required:
        assert (ROOT / path).is_file(), path


def test_baseline_models_portable_kubernetes_primitives() -> None:
    expected = {
        "namespace.yaml": "Namespace",
        "serviceaccount.yaml": "ServiceAccount",
        "configmap.yaml": "ConfigMap",
        "deployment.yaml": "Deployment",
        "service.yaml": "Service",
        "hpa.yaml": "HorizontalPodAutoscaler",
        "networkpolicy.yaml": "NetworkPolicy",
    }
    for file_name, kind in expected.items():
        manifest = read(f"k8s/base/{file_name}")
        assert "apiVersion:" in manifest
        assert f"kind: {kind}" in manifest


def test_deployment_has_platform_operational_basics() -> None:
    deployment = read("k8s/base/deployment.yaml")
    for expected in [
        "replicas: 2",
        "readinessProbe:",
        "livenessProbe:",
        "resources:",
        "requests:",
        "limits:",
        "serviceAccountName: floci-cloud-lab-app",
        "image: floci-cloud-lab-app:local",
    ]:
        assert expected in deployment


def test_docs_keep_local_only_and_comparison_boundaries() -> None:
    comparison = read("docs/eks-oke-comparison.md")
    baseline = read("docs/kubernetes-platform-baseline.md")
    assert "does not deploy a real EKS or OKE cluster" in comparison
    assert "EKS" in comparison
    assert "OKE" in comparison
    assert "Floci" in baseline
    assert "local-only" in baseline
    assert "future phase" in baseline
