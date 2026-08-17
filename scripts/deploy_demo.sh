#!/usr/bin/env bash
# Build the mir-emulator Lambda bundle and deploy the public demo stack.
#
#   ./scripts/deploy_demo.sh            # build + deploy + smoke test
#   SKIP_SMOKE=1 ./scripts/deploy_demo.sh
#
# The bundle is cross-built for the Lambda runtime (aarch64-manylinux,
# CPython 3.13) because jsonschema pulls the binary rpds-py wheel — a
# macOS-built zip would import-error in Lambda.

set -e
set -o nounset
set -o pipefail

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

sha256() { # portable: macOS has shasum, GitHub runners have both
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 | cut -d' ' -f1
    else
        sha256sum | cut -d' ' -f1
    fi
}

STACK_NAME="${STACK_NAME:-mir-emulator-demo}"
DOMAIN_NAME="${DOMAIN_NAME:-amr-emulator.com}"        # DOMAIN_NAME="" skips the custom domain
LEGACY_DOMAIN_NAME="${LEGACY_DOMAIN_NAME:-}"          # old alias kept alive (e.g. mir.advin.io)
CFN_ROLE_ARN="${CFN_ROLE_ARN:-}"           # optional CloudFormation service role
REGION="${AWS_REGION:-$(aws configure get region)}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
BUCKET="mir-emulator-artifacts-${ACCOUNT_ID}-${REGION}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/mir-emulator-lambda.XXXXXX")"
trap 'rm -rf "$BUILD_DIR"' EXIT

log "Building wheel"
uv build --package mir-emulator --wheel -o "$BUILD_DIR/wheels" >/dev/null

log "Cross-installing for aarch64-manylinux2014 / CPython 3.13"
uv pip install \
    --target "$BUILD_DIR/site" \
    --python-version 3.13 \
    --python-platform aarch64-manylinux2014 \
    --only-binary :all: \
    "$BUILD_DIR"/wheels/mir_emulator-*.whl >/dev/null

find "$BUILD_DIR/site" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

# Site pages ship inside the bundle: the advin.io landing at /, the MiR
# console at /console (+ /mir), and the VDA 5050 / Omron ARCL app pages at
# their own routes.
cp "$REPO_ROOT/docs/index.html" "$BUILD_DIR/site/mir_emulator/console.html"
cp "$REPO_ROOT/docs/landing.html" "$BUILD_DIR/site/mir_emulator/landing.html"
cp "$REPO_ROOT/docs/vda5050.html" "$BUILD_DIR/site/mir_emulator/vda5050.html"
cp "$REPO_ROOT/docs/omron.html" "$BUILD_DIR/site/mir_emulator/omron.html"

log "Zipping bundle"
(cd "$BUILD_DIR/site" && zip -qr "$BUILD_DIR/code.zip" .)
ZIP_SHA="$(sha256 < "$BUILD_DIR/code.zip")"
S3_KEY="${STACK_NAME}/${ZIP_SHA}.zip"
log "Bundle: $(du -h "$BUILD_DIR/code.zip" | cut -f1 | tr -d ' ') sha256=${ZIP_SHA}"

if ! aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
    log "Creating private artifacts bucket ${BUCKET}"
    if [[ "$REGION" == "us-east-1" ]]; then
        aws s3api create-bucket --bucket "$BUCKET" >/dev/null
    else
        aws s3api create-bucket --bucket "$BUCKET" \
            --create-bucket-configuration "LocationConstraint=${REGION}" >/dev/null
    fi
    aws s3api put-public-access-block --bucket "$BUCKET" \
        --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
    # Build artifacts are only needed at deploy time - don't accrete forever.
    aws s3api put-bucket-lifecycle-configuration --bucket "$BUCKET" \
        --lifecycle-configuration '{"Rules":[{"ID":"expire-artifacts","Status":"Enabled","Filter":{},"Expiration":{"Days":30}}]}'
fi

if ! aws s3api head-object --bucket "$BUCKET" --key "$S3_KEY" >/dev/null 2>&1; then
    log "Uploading s3://${BUCKET}/${S3_KEY}"
    aws s3 cp --no-progress "$BUILD_DIR/code.zip" "s3://${BUCKET}/${S3_KEY}" >/dev/null
else
    log "Bundle already uploaded (content-addressed), skipping"
fi

zone_for_domain() { # walk the labels: apex domains own their zone, subdomains sit in a parent's
    local candidate="$1" zone_id
    while [[ "$candidate" == *.* ]]; do
        zone_id="$(aws route53 list-hosted-zones-by-name --dns-name "$candidate" \
            --query "HostedZones[?Name=='${candidate}.'].Id | [0]" --output text)"
        zone_id="${zone_id##*/}"
        if [[ -n "$zone_id" && "$zone_id" != "None" ]]; then
            echo "$zone_id"
            return 0
        fi
        candidate="${candidate#*.}"
    done
    return 1
}

DOMAIN_PARAMS=()
if [[ -n "$DOMAIN_NAME" ]]; then
    if ! HOSTED_ZONE_ID="$(zone_for_domain "$DOMAIN_NAME")"; then
        log "ERROR: no public hosted zone found for ${DOMAIN_NAME}"
        exit 1
    fi
    log "Custom domain ${DOMAIN_NAME} in zone ${HOSTED_ZONE_ID}"
    DOMAIN_PARAMS=("DomainName=${DOMAIN_NAME}" "HostedZoneId=${HOSTED_ZONE_ID}")
fi

if [[ -n "$LEGACY_DOMAIN_NAME" ]]; then
    if ! LEGACY_ZONE_ID="$(zone_for_domain "$LEGACY_DOMAIN_NAME")"; then
        log "ERROR: no public hosted zone found for ${LEGACY_DOMAIN_NAME}"
        exit 1
    fi
    log "Legacy domain ${LEGACY_DOMAIN_NAME} in zone ${LEGACY_ZONE_ID}"
    DOMAIN_PARAMS+=("LegacyDomainName=${LEGACY_DOMAIN_NAME}" "LegacyHostedZoneId=${LEGACY_ZONE_ID}")
fi

ROLE_ARGS=()
if [[ -n "$CFN_ROLE_ARN" ]]; then
    ROLE_ARGS=(--role-arn "$CFN_ROLE_ARN")
fi

log "Deploying CloudFormation stack ${STACK_NAME}"
aws cloudformation deploy \
    --region "$REGION" \
    --stack-name "$STACK_NAME" \
    --template-file "$REPO_ROOT/deploy/template.yaml" \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset \
    ${ROLE_ARGS[@]+"${ROLE_ARGS[@]}"} \
    --parameter-overrides "CodeS3Bucket=${BUCKET}" "CodeS3Key=${S3_KEY}" \
    ${DOMAIN_PARAMS[@]+"${DOMAIN_PARAMS[@]}"}

API_URL="$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)"
log "Deployed: ${API_URL}"

if [[ "${SKIP_SMOKE:-0}" == "1" ]]; then
    exit 0
fi

log "Smoke testing"
# tr strips GNU base64's 76-column line wrap (macOS base64 never wraps).
AUTH_TOKEN="$(printf '%s:%s' distributor "$(printf distributor | sha256)" | base64 | tr -d '\n')"

check() { # check <expected_status> <url> [curl args...]
    local expected="$1" url="$2"
    shift 2
    local status
    status="$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$@" "$url" || true)"
    if [[ "$status" != "$expected" ]]; then
        log "FAIL ${url} -> ${status} (wanted ${expected})"
        return 1
    fi
    log "ok   ${expected} ${url}"
}

check 200 "${API_URL}/healthz"
check 200 "${API_URL}/"
check 200 "${API_URL}/console"
check 200 "${API_URL}/vda5050"
check 200 "${API_URL}/omron"
check 401 "${API_URL}/latest/api/v2.0.0/status"
check 401 "${API_URL}/fleet/latest/api/v1/system/version"
for v in $(curl -s "${API_URL}/healthz" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin)["versions"]))'); do
    check 200 "${API_URL}/${v}/api/v2.0.0/status" -H "Authorization: Basic ${AUTH_TOKEN}"
done
# /api/v1/system/version is the one operation every tracked fleet version
# serves (e.g. /robots only exists from 1.4.0 on — the emulator is
# version-faithful, so the smoke must be too).
for v in $(curl -s "${API_URL}/healthz" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin).get("fleet_versions", [])))'); do
    check 200 "${API_URL}/fleet/${v}/api/v1/system/version" -H "x-api-key: distributor"
done

if [[ -n "$DOMAIN_NAME" ]]; then
    # Fresh alias records can take a moment to resolve everywhere.
    for attempt in $(seq 1 10); do
        if check 200 "https://${DOMAIN_NAME}/healthz" 2>/dev/null; then
            break
        fi
        if [[ "$attempt" == "10" ]]; then
            log "FAIL https://${DOMAIN_NAME}/healthz never came up"
            exit 1
        fi
        log "waiting for DNS (${attempt}/10)"
        sleep 15
    done
    check 200 "https://${DOMAIN_NAME}/console"
    check 200 "https://${DOMAIN_NAME}/latest/api/v2.0.0/status" -H "Authorization: Basic ${AUTH_TOKEN}"
fi
if [[ -n "$LEGACY_DOMAIN_NAME" ]]; then
    check 200 "https://${LEGACY_DOMAIN_NAME}/healthz"
fi
log "Smoke test passed"
