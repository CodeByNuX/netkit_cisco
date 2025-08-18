from netkit_cisco.device import CiscoDevice


# NXOS 192.168.2.193
# iou1"
# netkitRouter

TEST = "IOSXE"
if TEST == "NXOS":
    node = CiscoDevice(ip="192.168.2.193",username="admin",password="MyPassword")
if TEST == "IOSXE":
    node = CiscoDevice(ip="netkitRouter",username="admin",password="MyPassword")

try:
    while node.is_connected == False and node.connection_attempts < 5:
        node.ssh_connect()
    
    print(f"is_connected: {node.is_connected}")
    if node.is_connected == True:
        node.auto_discovery()
    print(node.hostname)
    print(node.os.family)
    print(node.os.major)
    print(node.os.minor)

    print(node.serial)
    print(node.model)
    print(node.storage.name)
    print(node.storage.total_free_B)
    print(node.storage.total_size_B)
    print("****************")

except Exception:
    node.last_exception

