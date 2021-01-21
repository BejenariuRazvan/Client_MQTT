from psutil import sensors_temperatures, cpu_percent, disk_partitions, \
    cpu_count, cpu_freq, disk_io_counters, disk_usage, virtual_memory, net_if_addrs, net_io_counters
import abc


def get_size(_bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if _bytes < factor:
            return f"{_bytes:.2f}{unit}{suffix}"
        _bytes /= factor


class SystemInformation(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_info(self):
        """This method should return a string with information specific to the class."""


# class with only one method that returns a string containing relevant information about the processor
class CpuInformation(SystemInformation):
    def get_info(self):
        info = ""

        info += "Physical cores:" + str(cpu_count(logical=False)) + "\n"
        info += "Total cores:" + str(cpu_count(logical=True)) + "\n"
        cpufreq = cpu_freq()
        info += f"Max Frequency: {cpufreq.max:.2f}Mhz" + "\n"
        info += f"Min Frequency: {cpufreq.min:.2f}Mhz" + "\n"
        info += f"Current Frequency: {cpufreq.current:.2f}Mhz" + "\n"

        return info


class CpuUsage(SystemInformation):
    def get_info(self):
        info = ""
        info += "CPU Usage Per Core:" + "\n"
        for i, percentage in enumerate(cpu_percent(percpu=True, interval=1)):
            info += f"Core {i}: {percentage}%" + "\n"
        info += f"Total CPU Usage: {cpu_percent()}%" + "\n"

        return info


class CpuTemperatures(SystemInformation):
    def get_info(self):
        info = ""
        temps = sensors_temperatures()
        info += "\nCore temperatures: \n"

        if temps:
            for name, entries in temps.items():
                if name == "coretemp":
                    for entry in entries:
                        info += str(entry.label) + " " + str(entry.current) + " °C\n"

        return info


class MemoryInformation(SystemInformation):
    def get_info(self):
        info = ""

        svmem = virtual_memory()
        info += "RAM:" + "\n"
        info += f"Total: {get_size(svmem.total)}" + "\n"
        info += f"Available: {get_size(svmem.available)}" + "\n"
        info += f"Used: {get_size(svmem.used)}" + "\n"
        info += f"Percentage: {svmem.percent}%" + "\n"

        return info


# class with only one method that returns a string containing relevant information about the disks that the computer has
class DiskInformation(SystemInformation):
    def get_info(self):
        info = ""

        # Disk Information
        info += "Partitions and Usage:" + "\n"
        # get all disk partitions
        partitions = disk_partitions()
        for partition in partitions:
            if partition.mountpoint == "/" or partition.mountpoint == "/home":
                info += f"=== Device: {partition.device} ===" + "\n"
                info += f"  Mountpoint: {partition.mountpoint}" + "\n"
                info += f"  File system type: {partition.fstype}" + "\n"
                try:
                    partition_usage = disk_usage(partition.mountpoint)
                except PermissionError:
                    # this can be catched due to the disk that
                    # isn't ready
                    continue
                info += f"  Total Size: {get_size(partition_usage.total)}" + "\n"
                info += f"  Used: {get_size(partition_usage.used)}" + "\n"
                info += f"  Free: {get_size(partition_usage.free)}" + "\n"
                info += f"  Percentage: {partition_usage.percent}%" + "\n"
        # get IO statistics since boot
        disk_io = disk_io_counters()
        info += f"Total read since boot: {get_size(disk_io.read_bytes)}" + "\n"
        info += f"Total write since boot: {get_size(disk_io.write_bytes)}" + "\n"

        return info


class NetworkInformation(SystemInformation):
    def get_info(self):
        info = ''
        if_addrs = net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                info += f"=== Interface: {interface_name} ===" + "\n"
                if str(address.family) == 'AddressFamily.AF_INET':
                    info += f"  IP Address: {address.address}" + "\n"
                    info += f"  Netmask: {address.netmask}" + "\n"
                    info += f"  Broadcast IP: {address.broadcast}" + "\n"
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    info += f"  MAC Address: {address.address}" + "\n"
                    info += f"  Netmask: {address.netmask}" + "\n"
                    info += f"  Broadcast MAC: {address.broadcast}" + "\n"
        net_io = net_io_counters()
        info += "Traffic since boot:\n"
        info += f"Total Bytes Sent: {get_size(net_io.bytes_sent)}\n"
        info += f"Total Bytes Received: {get_size(net_io.bytes_recv)}\n"

        return info


