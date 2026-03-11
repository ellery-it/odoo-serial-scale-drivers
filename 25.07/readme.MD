# IoTBox 25.07 — New Requirements for Serial Scale Drivers

**Applies to:** Odoo IoTBox firmware ≥ 25.07  
**Ref. base driver:** `odoo/addons/hw_drivers/iot_handlers/drivers/SerialScaleDriver.py` (v18)

---

## 1. Extended `ScaleProtocol` Named Tuple

Since 25.07, the base `SerialProtocol` namedtuple is **no longer sufficient** for scale drivers that support tare or zero operations. Custom drivers must define an extended namedtuple that includes the additional fields below.

```python
from collections import namedtuple
from odoo.addons.hw_drivers.iot_handlers.drivers.SerialBaseDriver import SerialProtocol

ScaleProtocol = namedtuple(
    'ScaleProtocol',
    SerialProtocol._fields + ('zeroCommand', 'tareCommand', 'clearCommand', 'autoResetWeight')
)
```

### New Fields

| Field | Type | Description |
|---|---|---|
| `zeroCommand` | `bytes \| None` | Command sent to zero/re-zero the scale. `None` if not supported. |
| `tareCommand` | `bytes \| None` | Command sent to tare the scale. `None` if not supported. |
| `clearCommand` | `bytes \| None` | Command sent to clear the tare. `None` if not supported (send `tareCommand` twice as fallback). |
| `autoResetWeight` | `bool` | If `True`, the driver resets the displayed weight to `0` automatically after a configurable timeout. |

---

## 2. `tare_mode` State and `net_weight_char`

The base `ScaleDriver.__init__` now initialises a `tare_mode` boolean flag (default `False`).  
Each driver subclass **must** declare `self.net_weight_char` in its `__init__` so the base class can detect when the scale is operating in net-weight (tare active) mode.

```python
def __init__(self, identifier, device):
    super().__init__(identifier, device)
    self.device_manufacturer = 'YourBrand'
    self.net_weight_char = b'<net_indicator_byte>'  # e.g. b'N', b'M-', b''
```

`_read_weight` (base class) sets `tare_mode = True` when `net_weight_char` is found in the raw answer. Drivers that do not support tare should set `net_weight_char = b''` or `None`.

---

## 3. Tare and Zero Actions Must Be Registered

Custom drivers that support tare/zero **must** override `_set_actions` and register the corresponding action handlers. The base class no longer provides default tare/zero stubs.

```python
def _set_actions(self):
    super()._set_actions()
    self._actions.update({
        'tare': self._tare_action,
        'zero': self._zero_action,
    })

def _tare_action(self, data):
    protocol = self._protocol
    if protocol.tareCommand:
        self._connection.write(protocol.tareCommand + protocol.commandTerminator)
        time.sleep(protocol.commandDelay)

def _zero_action(self, data):
    protocol = self._protocol
    if protocol.zeroCommand:
        self._connection.write(protocol.zeroCommand + protocol.commandTerminator)
        time.sleep(protocol.commandDelay)
```

If `clearCommand` is `None`, re-sending `tareCommand` should be used to cancel tare.

---

## 4. `_get_raw_response` — Preferred Implementation

The generic byte-by-byte loop in `ScaleDriver._get_raw_response` is still valid, but the recommended override for drivers with a known terminator is:

```python
@staticmethod
def _get_raw_response(connection):
    return connection.read_until(b'\n', size=64)  # adjust terminator and size
```

This avoids hanging on partial reads and is more reliable across USB-serial adapters.

---

## 5. `supported()` Probing — Best Practices

The `supported` classmethod is called during device discovery. Since 25.07, the following practices are expected:

- Use `read_until` instead of a fixed-length `read(N)` to avoid partial-read failures.
- Log the raw answer (including hex) at `INFO` level to ease field debugging.
- Always return `False` on any unexpected exception (already enforced by base, but must not be bypassed).

```python
@classmethod
def supported(cls, device):
    protocol = cls._protocol
    try:
        with serial_connection(device['identifier'], protocol, is_probing=True) as connection:
            connection.write(protocol.measureCommand + protocol.commandTerminator)
            time.sleep(protocol.commandDelay)
            answer = connection.read_until(b'\n', size=32)
            _logger.info('Probe answer: [%s] (hex: %s)', answer, answer.hex())
            if b'<expected_marker>' in answer:
                return True
    except serial.serialutil.SerialTimeoutException:
        pass
    except Exception:
        _logger.exception('Error probing %s with %s', device, protocol.name)
    return False
```

---

## 6. `_read_status` — Must Be Implemented

Every driver subclass **must** implement `_read_status(self, answer)`. Returning `pass` is acceptable only for scales that never return status frames, but the method must exist. Failing to implement it will raise `NotImplementedError` in future versions.

---

## 7. Sign Handling for Negative Weights

If your scale can output negative weight values (e.g. after tare), the `measureRegexp` **must** capture the sign, and the weight value stored in `self.data['value']` must reflect it as a negative `float`.

Example pattern capturing sign:

```python
measureRegexp=br"^[M ]([\-\s])\s*([0-9.]+)\s+kg"
```

And in a custom `_read_weight` override:

```python
sign = -1 if match.group(1).strip() == b'-' else 1
self.data = {'value': sign * float(match.group(2)), 'status': self._status}
```

---

## 8. Minimum Driver Checklist

Before submitting or deploying a custom driver for IoTBox ≥ 25.07:

- [ ] Protocol defined as extended `ScaleProtocol` (not bare `SerialProtocol`)
- [ ] `zeroCommand`, `tareCommand`, `clearCommand`, `autoResetWeight` all explicitly set
- [ ] `self.net_weight_char` declared in `__init__`
- [ ] `_set_actions` registers `tare` and `zero` if supported
- [ ] `_read_status` implemented (not missing)
- [ ] `measureRegexp` handles negative values if the scale supports tare
- [ ] `supported()` uses `read_until` and logs raw answer + hex
- [ ] `priority` class attribute set to avoid conflicts with `AdamEquipmentDriver` (`priority = 0`)
