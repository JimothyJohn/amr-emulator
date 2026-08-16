# vda5050-emulator

Spec-faithful emulator of VDA 5050 mobile robots (MQTT + JSON), with an
embedded MQTT 3.1.1 broker so evaluation needs zero infrastructure. Speaks
VDA 5050 **2.0.0, 2.1.0 and 3.0.0** (switchable), validating every message —
inbound and outbound — against the official JSON schemas vendored from
[VDA5050/VDA5050](https://github.com/VDA5050/VDA5050).

```sh
vda5050-emulator                       # embedded broker on :1883 + one 3.0.0 robot
vda5050-emulator --spec 2.1.0          # speak VDA 5050 2.1.0 instead
vda5050-emulator --broker 10.0.0.5     # join YOUR existing broker instead
vda5050-emulator --robots 5 --time-scale 60
```

Point your master control at the printed broker address; the robot answers on
the standard topics (`.../order`, `.../instantActions` in, `.../state`,
`.../connection`, `.../factsheet`, `.../visualization` out, plus
`zoneSet`/`responses` on 3.0.0). Fault injection — emergency stop, field
violation, localization loss, battery override, teleport, forced action
failures, connection drop — goes through the non-standard `.../_emulator`
topic or the Python API.

```python
from vda5050_emulator import AGVConfig, Broker, MasterControl, VirtualAGV
```

See the repository README for the full feature list and test harness.
