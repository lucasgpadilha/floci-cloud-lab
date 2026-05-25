#!/usr/bin/env bash
set -euo pipefail

: "${FLOCI_ENDPOINT:=http://localhost:4566}"
: "${AWS_DEFAULT_REGION:=us-east-1}"
: "${AWS_ACCESS_KEY_ID:=test}"
: "${AWS_SECRET_ACCESS_KEY:=test}"

cat <<EOF
export AWS_ENDPOINT_URL=${FLOCI_ENDPOINT}
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
EOF
