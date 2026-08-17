# The OFFICIAL MassRobotics AMR Interop reference receiver, built unmodified
# at a pinned commit — the external validation oracle for this repo's
# massrobotics-emulator sender. It validates every message with Ajv against
# the standard's schema and broadcasts {message, isValid, errors} verdicts
# to /ui WebSocket clients, which is how the harness witnesses acceptance.
#
# Upstream: https://github.com/MassRobotics-AMR/AMR_Interop_Standard
FROM node:14.16.0-alpine

ARG STANDARD_REPO=https://github.com/MassRobotics-AMR/AMR_Interop_Standard.git
# main @ 2021-10-08 (the only release lineage; watched for drift by hash in
# packages/massrobotics-emulator/src/massrobotics_emulator/schemas/registry.json)
ARG STANDARD_COMMIT=f9357a423ecabc3f7112e6d10025a5231943ec50

RUN apk add --no-cache git \
    && git clone ${STANDARD_REPO} /app \
    && git -C /app checkout ${STANDARD_COMMIT} \
    && rm -rf /app/.git

WORKDIR /app/MassRobotics-AMR-Receiver
RUN npm run install-server

EXPOSE 3000
ENTRYPOINT ["npm", "run", "start"]
