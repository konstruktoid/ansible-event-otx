#!/usr/bin/python3
"""
Stream subscribed OTX events.

Arguments:
    count: minimum count of related pulses that is required for the
        IP to be added to the blocklist.

Example playbook:
    - name: otx events
      hosts: all
      sources:
        - name: Match all messages
          ansible.eda.otx:
            count: "1"
      rules:
        - name: Send to playboox
          condition: event.otx is defined
          action:
            run_playbook:
              name: otx_ufw.yml
"""

import os
import datetime
import ipaddress
import asyncio
import sys
import time
from typing import Any, Dict
from OTXv2 import OTXv2, IndicatorTypes

OTX_APIKEY = os.getenv("OTX_APIKEY")
otx = OTXv2(OTX_APIKEY)


def get_indicator(indicator_type, indicator_address, count):
    """Get indicator IP address."""
    count = int(count)
    block_ips = set()

    indicator_type_map = {
        "domain": IndicatorTypes.DOMAIN,
        "hostname": IndicatorTypes.HOSTNAME,
        "IPv4": IndicatorTypes.IPv4,
        "IPv6": IndicatorTypes.IPv6,
    }

    if indicator_type not in indicator_type_map:
        return

    event_indicator = otx.get_indicator_details_full(
        indicator_type_map[indicator_type], indicator_address
    )

    if event_indicator["general"]["pulse_info"]["count"] < count:
        return

    for dns in event_indicator["passive_dns"]["passive_dns"]:
        try:
            if ipaddress.ip_address(dns["address"]):
                block_ips.add(dns["address"])
        except ValueError:
            pass

    if block_ips:
        return block_ips


async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    """
    Main loop that sends any pulse info to the get_indicator function
    and add adds otx={"ip": block_ip} to the queue.
    """
    delay = args.get("delay", 1)
    count = args.get("count", [])
    block_ips = set()
    reported_ips = set()

    if not count:
        sys.exit(1)

    while True:
        queue_time = (
            datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ).isoformat()
        pulses = otx.getall(modified_since=queue_time)

        # Just so we don't trigger rate-limit.
        time.sleep(300)

        for pulse in pulses:
            if pulse["indicators"]:
                supported_types = ["domain", "hostname", "IPv4", "IPv6"]
                if (
                    pulse["indicators"][0]["is_active"] == 1
                    and pulse["indicators"][0]["type"] in supported_types
                ):
                    block_ips = get_indicator(
                        pulse["indicators"][0]["type"],
                        pulse["indicators"][0]["indicator"],
                        count,
                    )

        try:
            for block_ip in block_ips:
                if block_ip not in reported_ips:
                    reported_ips.add(block_ip)
                    await queue.put(dict(otx={"ip": block_ip}))
                    await asyncio.sleep(delay)
                    if len(reported_ips) >= 1000:
                        reported_ips = set()
        except TypeError:
            pass


if __name__ == "__main__":

    class MockQueue:
        """Create a mock queue for testing."""

        async def put(self, event):
            """Print event."""
            print(event)

    asyncio.run(main(MockQueue(), {"count": "1"}))
