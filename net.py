import ipaddress
import math

NETWORK = ipaddress.ip_network("138.70.0.0/16")

wan_start = ipaddress.ip_address("138.70.255.0")

# LANs: name -> required number of IP addresses
LANs = {
    "Belfast": 5000,
    "Galway": 2000,
    "Dublin": 1800,
    "Letterkenny": 1000,
    "Cork": 500,
}

# WAN connections
WANs = [
    ("Belfast", "Galway"),
    ("Belfast", "Dublin"),
    ("Belfast", "Letterkenny"),
    ("Galway", "Cork"),
    ("Dublin", "Cork"),
]


def required_prefix(hosts):
    """Return the smallest CIDR prefix capable of holding `hosts` devices."""
    host_bits = math.ceil(math.log2(hosts + 2))
    return 32 - host_bits


def subnet_info(name, hosts, network):
    """Print useful information about a subnet."""
    first = network.network_address + 1
    last = network.broadcast_address - 1

    print(f"\n{name} LAN")
    print("-" * 40)
    print(f"Network:       {network}")
    print(f"Subnet mask:   {network.netmask}")
    print(f"Total IPs:     {network.num_addresses}")
    print(f"Usable hosts:  {network.num_addresses - 2}")
    print(f"1st host:      {first}")
    print(f"Last host:     {last}")
    print(f"Broadcast:     {network.broadcast_address}")


# ---------------------------------------------------------
# Allocate LAN subnets
# ---------------------------------------------------------

print(f"Global network: {NETWORK}")
print(f"Global mask:    {NETWORK.netmask}")

current_address = NETWORK.network_address

# Largest networks first
LANs_sorted = sorted(LANs.items(), key=lambda x: x[1], reverse=True)

allocated = {}

for name, hosts in LANs_sorted:
    prefix = required_prefix(hosts)

    # Create a candidate network at the current address
    candidate = ipaddress.ip_network(
        f"{current_address}/{prefix}",
        strict=False
    )

    # Make sure it fits
    if not candidate.subnet_of(NETWORK):
        print(f"ERROR: {name} does not fit inside {NETWORK}")
        break

    allocated[name] = candidate

    subnet_info(name, hosts, candidate)

    # Move to the next available address
    current_address = candidate.broadcast_address + 1


# ---------------------------------------------------------
# Allocate WAN /30 networks from the end
# ---------------------------------------------------------

print("\n\nWAN CONNECTIONS")
print("=" * 50)

for i, (router_a, router_b) in enumerate(WANs):
    network = ipaddress.ip_network(
        f"{wan_start}/30",
        strict=False
    )

    hosts = list(network.hosts())

    print(f"\n{router_a} - {router_b}")
    print("-" * 40)
    print(f"Network:       {network}")
    print(f"Subnet mask:   {network.netmask}")
    print(f"{router_a}:       {hosts[0]}")
    print(f"{router_b}:       {hosts[1]}")
    print(f"Broadcast:     {network.broadcast_address}")

    # Next /30
    wan_start = network.broadcast_address + 1

