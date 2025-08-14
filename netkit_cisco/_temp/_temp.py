from netkit_cisco.device import CiscoDevice


node = CiscoDevice(ip="192.168.2.197",username="admin",password="MyPassword")

try:
    while node.is_connected == False and node.connection_attempts < 5:
        node.ssh_connect()
    
    print(f"is_connected: {node.is_connected}")
    if node.is_connected == True:
        node.auto_discovery()
    print(node.serial)
    print(node.model)

except Exception:
    node.last_exception