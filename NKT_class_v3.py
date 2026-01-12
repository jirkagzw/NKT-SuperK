# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 12:25:29 2024

@author: jirka
"""
from NKTP_DLL import *

class VariaModule:
    VARIA_ADDRESS = 16
    FIANIUM_ADDRESS = 15

    def __init__(self, portname):
        self.portname = portname
        self.devices = {}

    def scan_for_devices(self):
        print('Scanning for devices on port:', self.portname)
        if (getLegacyBusScanning()):
            print('Scanning following ports in legacy mode:', getAllPorts())
        else:
            print('Scanning following ports in normal mode:', getAllPorts())

        # Use the openPorts function with Auto & Live settings
        print(openPorts(getAllPorts(), 1, 1))

        print('Following ports have modules:', getOpenPorts())

        # Retrieve found modules via the deviceGetAllTypes function
        portlist = getOpenPorts().split(',')
        for portName in portlist:
            result, devList = deviceGetAllTypes(portName)
            for devId in range(0, len(devList)):
                if (devList[devId] != 0):
                    print('Comport:', portName, 'Device type:', "0x%0.2X" % devList[devId], 'at address:', devId)
                    self.devices[portName] = devList  # Store found devices

    def set_wavelength(self, center_wl_nm, full_width_nm):
        """
        Set the laser wavelength center and full width for the device.
        The wavelength is set in units of wavelength_nm * 10.
        """
        module_address = self.VARIA_ADDRESS
        if 300 <= center_wl_nm-full_width_nm/2 <= center_wl_nm+full_width_nm/2 <= 1000: #to be tested
                    
            # Calculate lower and upper bounds and convert to settings
            lower_bound_setting = int((center_wl_nm - (full_width_nm / 2)) * 10)
            upper_bound_setting = int((center_wl_nm + (full_width_nm / 2)) * 10)
    
            # Set lower and upper bounds
            print(self.portname,module_address,0x34,lower_bound_setting,-1)
            print(self.portname, module_address, 0x33, upper_bound_setting, -1)
            result_lower = registerWriteU16(self.portname, module_address, 0x34, lower_bound_setting, -1)
            result_upper = registerWriteU16(self.portname, module_address, 0x33, upper_bound_setting, -1)
            
        else:
                print("Lower range must be above 300 nm and upper range must be balow 1000 nm")

    def get_wavelength(self):
        """
        Get the current wavelength settings (center wavelength and bandwidth) for the device.
        Returns a tuple (center_wavelength, full_width) in nanometers.
        """
        module_address = self.VARIA_ADDRESS  # Hardcoded address

        # Read lower and upper bounds
        lower_bound_setting = registerReadU16(self.portname, module_address, 0x34,  -1)
        upper_bound_setting = registerReadU16(self.portname, module_address, 0x33,  -1)
        print(lower_bound_setting,upper_bound_setting)

        if lower_bound_setting is not None and upper_bound_setting is not None:
            lower_wavelength = lower_bound_setting[1] / 10  # Convert to nm
            upper_wavelength = upper_bound_setting[1] / 10  # Convert to nm
            
            # Calculate center wavelength and full width (bandwidth)
            center_wavelength = (lower_wavelength + upper_wavelength) / 2
            full_width = upper_wavelength - lower_wavelength
            return center_wavelength, full_width
        else:
            print(f"Error reading wavelength settings on {self.portname}.")
            return None

    def set_power(self, power_level):
        """
        Set the power level of the laser for the device.
        The power level is in percents.
        :param power_level: Desired power level (in percent, range 0 - 1000).
        """
        module_address = self.FIANIUM_ADDRESS  # Use class constant for Fianium address
        
        if 0 <= power_level <= 100:
            power_setting = int(power_level * 10)  # Convert to tenths of a percent
            result = registerWriteU16(self.portname, module_address, 0x37, power_setting, -1)
        
            if result == 0:
                print(f"Power level set to {power_level / 10:.1f}% on port {self.portname}.")
            else:
                print(f"Error setting power level on {self.portname}. Error code: {result}")
        else:
            print("Power level must be between 0 and 100.")

    def get_power(self):
        """
        Get the current power level of the laser for the device.
        Returns the power level in percent.
        """
        module_address = self.FIANIUM_ADDRESS  # Hardcoded address for Fianium

        power_setting = registerReadU16(self.portname, module_address, 0x37, -1)

        if power_setting is not None:
            current_power = power_setting[1] / 10  # Convert to percent
            return current_power
        else:
            print(f"Error reading power level on {self.portname}.")
            return None

    def set_emission(self, emission_state):
        """
        Set the emission state of the laser for the device.
        The emission state can be 0 (off) or 3 (on).
        :param emission_state: Desired emission state (0 = Off, 3 = On).
        """
        module_address = self.FIANIUM_ADDRESS  # Use class constant for Fianium address
    
        if emission_state in [0, 3]:
            result = registerWriteU16(self.portname, module_address, 0x30, emission_state, -1)

            if result == 0:
                state_str = "On" if emission_state == 3 else "Off"
                print(f"Emission set to {state_str} on port {self.portname}.")
            else:
                print(f"Error setting emission state on {self.portname}. Error code: {result}")
        else:
            print("Emission state must be 0 (Off) or 3 (On).")

    def get_emission(self):
        """
        Get the current emission state of the laser for the device.
        Returns the emission state: 0 (off) or 3 (on).
        """
        module_address = self.FIANIUM_ADDRESS  # Use class constant for Fianium address

        emission_state = registerReadU16(self.portname, module_address, 0x30, -1)[1]

        if emission_state is not None:
            return emission_state
        else:
            print(f"Error reading emission state on {self.portname}.")
            return None
        
    def get_current_level(self):
        """
        Get the current level of the laser.
        Returns the current level in percentage.
        """
        module_address = self.FIANIUM_ADDRESS
        current_level = registerReadU16(self.portname, module_address, 0x38, -1)[1]

        if current_level is not None:
            return current_level / 10.0  # Convert to percent
        else:
            print(f"Error reading current level on {self.portname}.")
            return None

    def set_current_level(self, level):
        """
        Set the current level for the laser.
        :param level: Current level in percentage (0-100).
        """
        module_address = self.FIANIUM_ADDRESS
        
        if 0 <= level <= 100:
            result = registerWriteU16(self.portname, module_address, 0x38, int(level * 10), -1)

            if result == 0:
                print(f"Current level set to {level}% on {self.portname}.")
            else:
                print(f"Error setting current level on {self.portname}. Error code: {result}")
        else:
            print("Current level must be between 0 and 100 percent.")

    def get_nim_delay(self):
        """
        Get the NIM delay for the module.
        Returns the NIM delay value as an integer.
        """
        module_address = self.FIANIUM_ADDRESS
        nim_delay = registerReadU16(self.portname, module_address, 0x39, -1)[1]

        if nim_delay is not None:
            # Convert register value back to nanoseconds
            nim_delay_ns = nim_delay * 0.009
            return nim_delay_ns
        else:
            print(f"Error reading NIM delay on {self.portname}.")
            return None

    def set_nim_delay(self, delay_ns):
        """
        Set the NIM delay for the module.
        :param delay_ns: NIM delay in nanoseconds (0-9.2 ns).
        """
        # Convert nanoseconds to register value (9 ps steps)
        if 0 <= delay_ns <= 9.2:
            register_value = int(delay_ns / 0.009)  # Convert ns to register value
           # print(register_value,"register value")
            if 0 <= register_value <= 1023:  # Ensure it's within the register range
                module_address = self.FIANIUM_ADDRESS
                result = registerWriteU16(self.portname, module_address, 0x39, register_value, -1)

                if result == 0:
                    print(f"NIM delay set to {delay_ns} ns on {self.portname}.")
                else:
                    print(f"Error setting NIM delay on {self.portname}. Error code: {result}")
            else:
                print("Calculated register value is out of range (0-1023).")
        else:
            print("NIM delay must be between 0 and 9.2 ns.")

    def get_pulse_picker_ratio(self):
        """
        Get the pulse-picker ratio of the module.
        Returns the pulse-picker ratio as an integer.
        The pulse picker ratio is read as an 8-bit unsigned integer if the ratio is less than 256,
        otherwise it is read as a 16-bit unsigned integer.
        """
        module_address = self.FIANIUM_ADDRESS
        
        # First, try to read as an 8-bit unsigned integer
        pulse_picker_ratio = registerReadU8(self.portname, module_address, 0x34, -1)[1]
    
        if pulse_picker_ratio is not None:
            # If the ratio is less than 256, return the 8-bit value
            return pulse_picker_ratio
        else:
            # If reading as 8-bit failed, try reading as a 16-bit unsigned integer
            pulse_picker_ratio = registerReadU16(self.portname, module_address, 0x34, -1)[1]
    
            if pulse_picker_ratio is not None:
                return pulse_picker_ratio
            else:
                print(f"Error reading pulse-picker ratio on {self.portname}.")
                return None

    def set_pulse_picker_ratio(self, ratio):
        """
        Set the pulse-picker ratio for the module.
        :param ratio: Pulse-picker ratio value (integer).
        """
        if isinstance(ratio, int):
            module_address = self.FIANIUM_ADDRESS
            result = registerWriteU16(self.portname, module_address, 0x34, ratio, -1)

            if result == 0:
                print(f"Pulse-picker ratio set to {ratio} on {self.portname}.")
            else:
                print(f"Error setting pulse-picker ratio on {self.portname}. Error code: {result}")
        else:
            print("Pulse-picker ratio must be an integer.")
        
        
    def set_interlock(self, interlock):
        """
        Set the pulse-picker ratio for the module.
        :param ratio: Pulse-picker ratio value (integer).
        """
        if isinstance(interlock, int):
            module_address = self.FIANIUM_ADDRESS
            result = registerWriteU16(self.portname, module_address, 0x32, interlock, -1)

            if result == 0:
                print(f"Interlock {interlock} on {self.portname}.")
            else:
                print(f"Interlock set on {self.portname}. Error code: {result}")
        else:
            print("Interlock must be an integer.")
            
    def get_interlock_status(self):
        """
        Get the interlock status.
        
        Returns:
            tuple: (MSB, LSB) of interlock status, or None if there was an error.
        """
        module_address = self.FIANIUM_ADDRESS  # Assuming interlock is accessed on the FIANIUM address
        interlock_status = registerReadU8(self.portname, module_address, 0x32, -1)
        print(interlock_status)

        if interlock_status is not None:
            # Interpret the returned status bytes
            msb, lsb = interlock_status
            status_description = {}
    
            # Interpret LSB (status of interlock)
            if lsb == 0:
                status_description["status"] = "Interlock off (circuit open)"
            elif lsb == 1:
                status_description["status"] = "Waiting for interlock reset"
            elif lsb == 2:
                status_description["status"] = "Interlock is OK"
            else:
                status_description["status"] = "Unknown status"
    
            # Interpret MSB (source of the issue, if any)
            status_descriptions = {
                0: "No additional issue",
                1: "Front panel interlock / key switch off",
                2: "Door switch open",
                3: "External module interlock",
                4: "Application interlock",
                5: "Internal module interlock",
                6: "Interlock power failure",
                7: "Interlock disabled by light source",
                255: "Interlock circuit failure"
            }
            status_description["issue_source"] = status_descriptions.get(msb, "Unknown issue source")
    
            return status_description
        else:
            print(f"Error reading interlock status on {self.portname}.")
            return None
import time

def test_varia_module():
    # Create an instance of VariaModule with a test port (replace 'COM1' with actual port)
    varia = VariaModule(portname='COM7')
    
    # Scan for devices
    print("\n--- Test: Scanning for Devices ---")
    varia.scan_for_devices()
    
    # Test setting and getting the wavelength
    print("\n--- Test: Set and Get Wavelength ---")
    center_wavelength = 600  # in nm
    full_width = 50  # in nm
    varia.set_wavelength(center_wavelength, full_width)
    time.sleep(1)  # Wait for the operation to complete
    wavelength = varia.get_wavelength()
    print(f"Set wavelength to {center_wavelength} nm, {full_width} nm full width.")
    print(f"Got wavelength: {wavelength}")
    
    # Test setting and getting power
    print("\n--- Test: Set and Get Power ---")
    power_level = 50  # in percent
    varia.set_power(power_level)
    time.sleep(1)  # Wait for the operation to complete
    power = varia.get_power()
    print(f"Set power level to {power_level}%.")
    print(f"Got power level: {power}%")
    
    # Test setting and getting emission
    print("\n--- Test: Set and Get Emission ---")
    emission_state = 3  # On (use 0 for Off)
    varia.set_emission(emission_state)
    time.sleep(1)  # Wait for the operation to complete
    emission = varia.get_emission()
    print(f"Set emission to {'On' if emission_state == 3 else 'Off'}.")
    print(f"Got emission state: {'On' if emission == 3 else 'Off'}")
    
    # Test setting and getting current level
    print("\n--- Test: Set and Get Current Level ---")
    current_level = 50  # in percent
    varia.set_current_level(current_level)
    time.sleep(1)  # Wait for the operation to complete
    current = varia.get_current_level()
    print(f"Set current level to {current_level}%.")
    print(f"Got current level: {current}%")
    
    # Test setting and getting NIM delay
    print("\n--- Test: Set and Get NIM Delay ---")
    nim_delay = 0.5  # in ns
    varia.set_nim_delay(nim_delay)
    time.sleep(1)  # Wait for the operation to complete
    delay = varia.get_nim_delay()
    print(f"Set NIM delay to {nim_delay} ns.")
    print(f"Got NIM delay: {delay} ns")
    
    # Test setting and getting pulse picker ratio
    print("\n--- Test: Set and Get Pulse Picker Ratio ---")
    pulse_picker_ratio = 1  # Example value
    varia.set_pulse_picker_ratio(pulse_picker_ratio)
    time.sleep(1)  # Wait for the operation to complete
    ratio = varia.get_pulse_picker_ratio()
    print(f"Set pulse picker ratio to {pulse_picker_ratio}.")
    print(f"Got pulse picker ratio: {ratio}")

# Run the test
#test_varia_module()
#varia = VariaModule(portname='COM9')




