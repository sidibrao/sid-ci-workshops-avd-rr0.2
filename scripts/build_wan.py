#!/usr/bin/env python3
"""Build BR-WAN extra config snippets from extra_configs/wan_vars.yml."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def add_block(lines: list[str], block: list[str]) -> None:
    lines.extend(block)
    lines.append("!")


def render_router(name: str, data: dict) -> str:
    lines: list[str] = ["!"]

    add_block(
        lines,
        [
            "no aaa root",
            "transceiver qsfp default-mode 4x10G",
            "service routing protocols model multi-agent",
            f"hostname {data.get('hostname', name)}",
            "spanning-tree mode rapid-pvst",
            "vrf instance mgmt",
        ],
    )

    for vlan in data.get("vlans", []):
        add_block(lines, [f"vlan {vlan['id']}", f"   name {vlan['name']}"])

    add_block(
        lines,
        [
            "management api http-commands",
            "   no shutdown",
            "   !",
            "   vrf mgmt",
            "      no shutdown",
        ],
    )

    for interface in data.get("switched_interfaces", []):
        block = [f"interface {interface['name']}"]
        if description := interface.get("description"):
            block.append(f"   description {description}")
        block.extend(
            [
                f"   switchport trunk allowed vlan {interface['allowed_vlans']}",
                "   switchport mode trunk",
            ]
        )
        add_block(lines, block)

    for interface in data.get("routed_interfaces", []):
        block = [f"interface {interface['name']}"]
        if description := interface.get("description"):
            block.append(f"   description {description}")
        if mtu := interface.get("mtu"):
            block.append(f"   mtu {mtu}")
        block.extend(
            [
                "   no switchport",
                f"   ip address {interface['ip_address']}",
            ]
        )
        add_block(lines, block)

    if loopback0 := data.get("loopback0"):
        add_block(lines, ["interface Loopback0", f"   ip address {loopback0}"])

    add_block(
        lines,
        [
            "interface Management1",
            "   vrf mgmt",
            f"   ip address {data['management_ip']}",
        ],
    )

    for vlan in data.get("vlans", []):
        if svi_ip := vlan.get("svi_ip"):
            add_block(lines, [f"interface Vlan{vlan['id']}", f"   ip address {svi_ip}"])

    mlag = data.get("mlag", {})
    if mlag.get("enabled"):
        add_block(
            lines,
            [
                "mlag configuration",
                f"   domain-id {mlag['domain_id']}",
                f"   local-interface {mlag['local_interface']}",
                f"   peer-address {mlag['peer_address']}",
                f"   peer-link {mlag['peer_link']}",
                "   reload-delay mlag 300",
                "   reload-delay non-mlag 330",
            ],
        )

    add_block(
        lines,
        [
            "ip routing",
            "no ip routing vrf mgmt",
            "ip route vrf mgmt 0.0.0.0/0 192.168.0.1",
        ],
    )

    bgp = [
        f"router bgp {data['bgp_as']}",
        f"   router-id {data['router_id']}",
        "   maximum-paths 4",
    ]
    for neighbor in data.get("bgp_neighbors", []):
        bgp.extend(
            [
                f"   neighbor {neighbor['ip']} remote-as {neighbor['remote_as']}",
                f"   neighbor {neighbor['ip']} description {neighbor['description']}",
            ]
        )
    bgp.extend(["   redistribute connected", "   !", "   address-family ipv4"])
    for neighbor in data.get("bgp_neighbors", []):
        bgp.append(f"      neighbor {neighbor['ip']} activate")
    add_block(lines, bgp)

    add_block(lines, ["management ssh", "   vrf mgmt"])
    lines.append("end")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build BR-WAN config snippets.")
    parser.add_argument(
        "--vars",
        default="extra_configs/wan_vars.yml",
        type=Path,
        help="WAN variables YAML relative to the lab directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="extra_configs",
        type=Path,
        help="Output directory relative to the lab directory.",
    )
    args = parser.parse_args()

    lab_dir = Path(__file__).resolve().parents[1]
    vars_path = args.vars if args.vars.is_absolute() else lab_dir / args.vars
    output_dir = args.output_dir if args.output_dir.is_absolute() else lab_dir / args.output_dir

    with vars_path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, router_data in data["wan_routers"].items():
        (output_dir / f"{name}.cfg").write_text(render_router(name, router_data), encoding="utf-8")


if __name__ == "__main__":
    main()
