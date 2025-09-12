"""
USB/HID stubs for mapping dictaphone buttons (e.g., Dragon PowerMic, Philips SpeechMike)
to the same behavior as the global hotkey in windows_client.py.

These are placeholders. Real HID integration depends on vendor-specific usage pages and
button codes. For production, consider using vendor SDKs or community packages.

Suggested approach:
- Install 'hidapi' (pip install hidapi) and enumerate devices
- Filter by known vendor/product IDs
- Open device and read input reports in a background thread
- On press of the desired button, call the provided callback
"""

from typing import Callable


def start_hid_listener(on_press: Callable[[], None]) -> None:
    """Start a background HID listener that calls on_press() when the record button is pressed.

    Not implemented by default. See docstring for guidance.
    """
    # Example skeleton (disabled):
    # import hid, threading
    # def worker():
    #     for dev in hid.enumerate():
    #         print(dev)
    #     # Open target device by vendor_id/product_id and read in a loop
    #     # if packet matches record button press, invoke callback
    # threading.Thread(target=worker, daemon=True).start()
    raise NotImplementedError("HID listener not implemented. Use vendor SDK or hidapi.")

