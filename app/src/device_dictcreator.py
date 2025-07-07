import json
from collections import defaultdict


class DeviceDictCreator():

    msc_dict = defaultdict(lambda: "Error Not Present")

    def __init__(self, device_map: json):
        self.device_map = device_map

    def _transfer_json_to_dict(self) -> dict:
        with open(self.device_map,'r', encoding="utf8") as f:
            device_dict = json.load(f)
            f.close()
        return device_dict
    
    def fill_msc_dictionary(self) -> None:
        device_dict = self._transfer_json_to_dict()
        for _, proj in enumerate(device_dict):
            for _, dev in enumerate(device_dict[proj]["MSC"]["0"]):
                if dev["dev"] not in self.msc_dict.keys():
                    self.msc_dict[dev["dev"]] = {"img": dev["img"], "mnt": dev["mnt"]}

    def fill_msc_dictionary_robot(self) -> None:
        device_dict = self._transfer_json_to_dict()
        for _, proj in enumerate(device_dict):
            for _, FS in enumerate(device_dict[proj]["Robot"]):
                if FS not in self.msc_dict.keys():
                    self.msc_dict[FS] = {"img": device_dict[proj]["Robot"][FS]["img"], "mnt": device_dict[proj]["Robot"][FS]["mnt"]}
                