# arcl-emulator

Emulator of the **Omron ARCL** (Advanced Robotics Command Language) telnet
interface spoken by LD/HD mobile robots (ARAM) and the Fleet Manager
(Enterprise Manager) queuing surface — the plaintext TCP protocol a WMS/MES
integrates against. Implemented from the official reference manual
**I617-E-02** (publicly published by Omron); provenance with sha256 in
`src/arcl_emulator/specs/registry.json`, per-command manual pages in
`specs/arcl_commands.json`.

```sh
arcl-emulator                # ARCL server on :7171, password "adept"
telnet 127.0.0.1 7171        # then: queuepickup Goal1  /  status  /  queueshow
```

Implemented faithfully: password login + command banner, `status` /
`oneLineStatus`, `getGoals` / `getRoutes` / `getDateTime`, `odometer`(+reset),
`dock` / `undock` (with charging), `stop`, `say`, `arclSendText`,
application faults (`applicationFaultSet/Clear/Query`, `faultsGet`), and the
fleet queuing loop — `queuePickup`, `queuePickupDropoff`, `queueQuery`,
`queueShow`, `queueCancel` (with shortcuts `qp`/`qpd`/`qq`/`qs`/`qc`) —
including the documented asynchronous `QueueUpdate:` broadcast lifecycle
(`Pending → InProgress {Allocated, BeforePickup, Driving, After…} →
Completed`) and the two-line `CommandError:` / `CommandErrorDescription:`
error form. One virtual AMR drives between named goals on simulated time
(`--time-scale`), drains and charges battery, and honors an e-stop.

Deliberately **not** implemented (documented in `arcl_commands.json`): config
import/export, data store, I/O banks, tasks/macros, custom commands,
localization scanning. The non-standard `emulator` command (battery, e-stop,
teleport, time scale) is the fault-injection side channel and is marked as
such in the help banner.

```python
from arcl_emulator import ArclServer, Sim
```
