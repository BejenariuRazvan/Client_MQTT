from psutil import sensors_temperatures, cpu_percent, disk_partitions, process_iter
import abc
from cpuinfo import get_cpu_info

class information(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_info(self):
        pass


# class with only one method that returns a string containing relevant information about the processor
class cpu_information(information):
    def get_info(self):
        info = ""

        info += get_cpu_info()['brand_raw'] + "\n\n"
        iterator = 1
        info += "Core loads:\n"
        for cpu in cpu_percent(0.1,True):
            info = info + "Core " + str(iterator) + ": " + str(cpu) + "%\n"
            iterator = iterator + 1

        temps = sensors_temperatures()

        info += "\nCore temperatures: \n"

        if temps:
            for name, entries in temps.items():
                if(name == "coretemp"):
                    for entry in entries:
                        info += str(entry.label) + " " + str(entry.current)+" °C\n" 

        return info

# class with only one method that returns a string containing relevant information about the disks that the computer has
class disk_information(information):
    def get_info(self):
        info = ""

        for disk in disk_partitions():
            info += str(disk) + "\n"

        return info

# class with only one method that returns a string containing relevant information about the current running processes
class running_processes(information):
    def get_info(self):
        info = ""
        for proc in process_iter(['pid', 'name', 'username']):
            info += str(proc) + "\n"

        return info


# for testing purposes
if __name__ == "__main__":
    cpu_info = cpu_information()
    disk_info = disk_information()
    proc_info = running_processes()
    print(cpu_info.get_info())
    print(disk_info.get_info())
    print(proc_info.get_info())
