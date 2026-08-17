# mir-vda5050-adapter

Expose a MiR robot — real, or the in-repo `mir-emulator` — as a **VDA 5050
robot** over MQTT, so master controls like NVIDIA Isaac Mission Dispatch can
drive it. Speaks VDA 5050 2.0.0/2.1.0/3.0.0 (same profiles as
`vda5050-emulator`, whose Figure-8 order evaluator, MQTT stack and schema
validation it reuses); talks MiR REST 3.8.1 on the robot side (positions +
move-action missions + mission_queue + status polling).

```sh
uv run mir-emulator &                        # or a real MiR on the network
uv run vda5050-emulator --robots 0 &         # or any MQTT broker
uv run mir-vda5050-adapter --mir-url http://127.0.0.1:8080 --broker 127.0.0.1:1883
```

Scope (advertised in the factsheet): route orders without node/edge actions;
instant actions `cancelOrder`, `startPause`, `stopPause`, `stateRequest`,
`factsheetRequest`. Orders with unsupported actions are rejected with the
protocol's predefined errors. Includes the Mission-Dispatch compatibility
behaviors proven out on the emulator (1.x `instantActions` field, idempotent
redelivery).
