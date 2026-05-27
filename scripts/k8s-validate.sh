#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_DIR="${ROOT_DIR}/k8s/base"
OVERLAYS=("${ROOT_DIR}/k8s/overlays/eks-local" "${ROOT_DIR}/k8s/overlays/oke-reference")

required_base_files=(
  namespace.yaml
  serviceaccount.yaml
  configmap.yaml
  deployment.yaml
  service.yaml
  hpa.yaml
  networkpolicy.yaml
  kustomization.yaml
)

for file in "${required_base_files[@]}"; do
  test -f "${BASE_DIR}/${file}"
done

for dir in "${OVERLAYS[@]}"; do
  test -f "${dir}/kustomization.yaml"
done

python3 - <<'PY' "${ROOT_DIR}"
from pathlib import Path
import sys
root = Path(sys.argv[1])
files = sorted(root.glob('k8s/**/*.yaml'))
errors = []
for path in files:
    text = path.read_text(encoding='utf-8')
    if '	' in text:
        errors.append(f'{path}: tabs are not allowed')
    if 'kind:' not in text:
        errors.append(f'{path}: missing kind')
    if 'apiVersion:' not in text:
        errors.append(f'{path}: missing apiVersion')
    if path.name != 'kustomization.yaml' and 'metadata:' not in text:
        errors.append(f'{path}: missing metadata')

expected_kinds = {
    'namespace.yaml': 'Namespace',
    'serviceaccount.yaml': 'ServiceAccount',
    'configmap.yaml': 'ConfigMap',
    'deployment.yaml': 'Deployment',
    'service.yaml': 'Service',
    'hpa.yaml': 'HorizontalPodAutoscaler',
    'networkpolicy.yaml': 'NetworkPolicy',
}
for name, kind in expected_kinds.items():
    text = (root / 'k8s/base' / name).read_text(encoding='utf-8')
    if f'kind: {kind}' not in text:
        errors.append(f'k8s/base/{name}: expected kind {kind}')

if errors:
    print(chr(10).join(errors))
    raise SystemExit(1)
print(f'static-yaml-check: ok ({len(files)} files)')
PY

if command -v kubectl >/dev/null 2>&1; then
  kubectl kustomize "${ROOT_DIR}/k8s/overlays/eks-local" >/dev/null
  kubectl kustomize "${ROOT_DIR}/k8s/overlays/oke-reference" >/dev/null
  echo "kubectl-kustomize: ok"
else
  echo "kubectl-kustomize: skipped (kubectl not installed)"
fi

echo "k8s-validate: ok"
