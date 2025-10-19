# Project Status

This document tracks the status of different projects supported by the Raspberry Pi USB Simulator tool.

## Overview

The USBTool supports three main projects, each with specific device configurations tailored for different testing scenarios:

1. **MIB3** - ✅ Complete
2. **GEI** - 🚧 In Progress
3. **User** - 🚧 In Progress

## Project Details

### MIB3 (Complete)

**Status:** ✅ Done

The MIB3 project is fully configured and ready for production use. It includes:

- **ECM Devices:** 9 predefined Ethernet adapters (category 0) + 1 generic (category 1)
- **HID Devices:** 1 keyboard device
- **CDC Devices:** 5 devices including ETC Card Reader and AOAP variants
- **TEST Devices:** 8 test mode devices
- **MSC Devices:** 14 filesystem types including:
  - MIB Compliance Media
  - Multiple filesystem types (ext2, ext3, ext4, FAT16, FAT32, VFAT, NTFS, exFAT, HFSPlus, Btrfs)
  - Partition support
  - Corrupted filesystem testing
- **Robot Framework Integration:** Full support with all filesystem types

### GEI (In Progress)

**Status:** 🚧 Progressing

The GEI project is partially configured. Current status:

**Completed:**
- **HID Devices:** 1 keyboard device configured
- **CDC Devices:** 1 SIM Card Reader device configured
- **TEST Devices:** 8 test mode devices configured
- **MSC Devices:** 7 filesystem types configured:
  - GEI Compliance Media
  - FAT16, FAT32, NTFS, exFAT
  - Free Partition
  - Corrupted filesystem

**Missing/Incomplete:**
- **ECM Devices:** No Ethernet adapters configured (both category 0 and 1 are empty)
- **MSC Devices:** Limited filesystem support compared to MIB3:
  - Missing: ext2, ext3, ext4, VFAT, HFSPlus, Btrfs, Partition support
- **Robot Framework:** Uses MIB3 compliance media reference instead of GEI-specific configuration

**Recommended Actions:**
- [ ] Add relevant ECM (Ethernet) devices for GEI testing
- [ ] Determine if additional filesystem types are needed for GEI
- [ ] Update Robot Framework configuration to use GEI compliance media

### User (In Progress)

**Status:** 🚧 Progressing

The User project is designed for custom/generic testing scenarios. Current status:

**Completed:**
- **ECM Devices:** 2 D-Link adapters (category 0) + 1 generic (category 1)
- **HID Devices:** 1 keyboard device (both categories)
- **CDC Devices:** 5 devices (ETC Card Reader and AOAP variants)
- **TEST Devices:** 8 test mode devices configured
- **MSC Devices:** 14 filesystem types (same as MIB3):
  - User Compliance Media
  - Full filesystem support
- **Robot Framework Integration:** Present but uses MIB3 references

**Missing/Incomplete:**
- **ECM Devices:** Fewer Ethernet adapters than MIB3 (only 2 vs 9)
- **Documentation:** No specific use case documentation for "User" project
- **Robot Framework:** References MIB3 compliance media instead of user-specific configuration

**Recommended Actions:**
- [ ] Document the intended use case for the "User" project
- [ ] Determine if additional ECM devices are needed
- [ ] Update Robot Framework configuration to use User compliance media reference
- [ ] Consider if this should be a template for users to customize

## How to Switch Projects

Projects can be switched in the USBSimulator GUI:

1. Open **USBSimulator.exe**
2. Click on **Projects** menu in the menu bar
3. Select one of: **MIB3**, **GEI**, or **User**
4. The selected project will be saved in `Config.json` and loaded automatically on next startup

## Device Configuration File

All project configurations are stored in `device_proj.json`. Each project defines:

- **ECM:** Ethernet/CDC Ethernet Control Model devices
- **HID:** Human Interface Devices (keyboards, mice, etc.)
- **CDC:** Communication Device Class devices
- **TEST:** USB test mode devices
- **MSC:** Mass Storage Class devices with various filesystems
- **Robot:** Robot Framework integration mappings

## Contributing

To add or modify devices in any project:

1. Edit `device_proj.json`
2. Follow the existing structure for your project
3. Test the configuration with the USBSimulator tool
4. Update this document if adding major features
