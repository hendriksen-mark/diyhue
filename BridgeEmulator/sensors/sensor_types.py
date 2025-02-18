sensorTypes = {}

# Daylight sensor
sensorTypes["PHDL00"] = {
    "Daylight": {
        "state": {"daylight": None, "lastupdated": "none"},
        "config": {"on": True, "configured": False, "sunriseoffset": 30, "sunsetoffset": -30},
        "static": {"manufacturername": "Signify Netherlands B.V.", "swversion": "1.0"}
    }
}

# Hue temperature, motion, and ambient light sensors
sensorTypes["SML001"] = {
    "ZLLTemperature": {
        "state": {"temperature": 2100, "lastupdated": "none"},
        "config": {"on": False, "battery": 100, "reachable": True, "alert": "none", "ledindication": False, "usertest": False, "pending": []},
        "static": {"swupdate": {"state": "noupdates", "lastinstall": "2021-03-16T21:16:40Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue temperature sensor", "swversion": "6.1.1.27575", "capabilities": {"certified": True, "primary": False}}
    },
    "ZLLPresence": {
        "state": {"lastupdated": "none", "presence": None},
        "config": {"on": False, "battery": 100, "reachable": True, "alert": "none", "ledindication": False, "usertest": False, "sensitivity": 2, "sensitivitymax": 2, "pending": []},
        "static": {"swupdate": {"state": "noupdates", "lastinstall": "2021-03-16T21:16:40Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue motion sensor", "swversion": "6.1.1.27575", "capabilities": {"certified": True, "primary": True}}
    },
    "ZLLLightLevel": {
        "state": {"dark": True, "daylight": False, "lightlevel": 6000, "lastupdated": "none"},
        "config": {"on": False, "battery": 100, "reachable": True, "alert": "none", "tholddark": 9346, "tholdoffset": 7000, "ledindication": False, "usertest": False, "pending": []},
        "static": {"swupdate": {"state": "noupdates", "lastinstall": "2021-03-16T21:16:40Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue ambient light sensor", "swversion": "6.1.1.27575", "capabilities": {"certified": True, "primary": False}}
    }
}

# Hue tap dial switch
sensorTypes["RDM002"] = {
    "ZLLSwitch": {
        "state": {"buttonevent": 3002, "lastupdated": "2023-05-13T09:34:38Z"},
        "config": {"on": True, "battery": 100, "reachable": True, "pending": []},
        "static": {"swupdate": {"state": "noupdates", "lastinstall": "2022-07-01T14:38:51Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue tap dial switch", "swversion": "2.59.25", "capabilities": {"certified": True, "primary": False, "inputs": [{"repeatintervals": [800], "events": [{"buttonevent": 1000, "eventtype": "initial_press"}, {"buttonevent": 1001, "eventtype": "repeat"}, {"buttonevent": 1002, "eventtype": "short_release"}, {"buttonevent": 1003, "eventtype": "long_release"}, {"buttonevent": 1010, "eventtype": "long_press"}]}, {"repeatintervals": [800], "events": [{"buttonevent": 2000, "eventtype": "initial_press"}, {"buttonevent": 2001, "eventtype": "repeat"}, {"buttonevent": 2002, "eventtype": "short_release"}, {"buttonevent": 2003, "eventtype": "long_release"}, {"buttonevent": 2010, "eventtype": "long_press"}]}, {"repeatintervals": [800], "events": [{"buttonevent": 3000, "eventtype": "initial_press"}, {"buttonevent": 3001, "eventtype": "repeat"}, {"buttonevent": 3002, "eventtype": "short_release"}, {"buttonevent": 3003, "eventtype": "long_release"}, {"buttonevent": 3010, "eventtype": "long_press"}]}, {"repeatintervals": [800], "events": [{"buttonevent": 4000, "eventtype": "initial_press"}, {"buttonevent": 4001, "eventtype": "repeat"}, {"buttonevent": 4002, "eventtype": "short_release"}, {"buttonevent": 4003, "eventtype": "long_release"}, {"buttonevent": 4010, "eventtype": "long_press"}]}]}}
    },
    "ZLLRelativeRotary": {
        "state": {"rotaryevent": 2, "expectedrotation": 90, "direction": "right", "expectedeventduration": 400, "lastupdated": "2023-05-13T09:34:38Z"},
        "config": {"on": True, "battery": 100, "reachable": True, "pending": []},
        "static": {"swupdate": {"state": "noupdates", "lastinstall": "2022-07-01T14:38:51Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue tap dial switch", "swversion": "2.59.25", "capabilities": {"certified": True, "primary": False, "inputs": [{"repeatintervals": [400], "events": [{"rotaryevent": 1, "eventtype": "start"}, {"rotaryevent": 2, "eventtype": "repeat"}]}]}}
    }
}

# Hue dimmer switch
sensorTypes["RWL021"] = {
    "ZLLSwitch": {
        "state": {"buttonevent": 4000, "lastupdated": "2022-11-13T09:34:38Z"},
        "config": {"on": True, "battery": None, "reachable": False, "pending": []},
        "static": {"swupdate": {"state": "noupdates", "lastinstall": "2022-11-13T09:32:55Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue dimmer switch", "diversityid": "6426c751-c093-499e-afb6-9f0c863ec819", "swversion": "2.44.0_hBB3C188", "capabilities": {"certified": True, "primary": True, "inputs": [{"repeatintervals": [800], "events": [{"buttonevent": 1000, "eventtype": "initial_press"}, {"buttonevent": 1001, "eventtype": "repeat"}, {"buttonevent": 1002, "eventtype": "short_release"}, {"buttonevent": 1003, "eventtype": "long_release"}, {"buttonevent": 1010, "eventtype": "long_press"}]}, {"repeatintervals": [800], "events": [{"buttonevent": 2000, "eventtype": "initial_press"}, {"buttonevent": 2001, "eventtype": "repeat"}, {"buttonevent": 2002, "eventtype": "short_release"}, {"buttonevent": 2003, "eventtype": "long_release"}, {"buttonevent": 2010, "eventtype": "long_press"}]}, {"repeatintervals": [800], "events": [{"buttonevent": 3000, "eventtype": "initial_press"}, {"buttonevent": 3001, "eventtype": "repeat"}, {"buttonevent": 3002, "eventtype": "short_release"}, {"buttonevent": 3003, "eventtype": "long_release"}, {"buttonevent": 3010, "eventtype": "long_press"}]}, {"repeatintervals": [800], "events": [{"buttonevent": 4000, "eventtype": "initial_press"}, {"buttonevent": 4001, "eventtype": "repeat"}, {"buttonevent": 4002, "eventtype": "short_release"}, {"buttonevent": 4003, "eventtype": "long_release"}, {"buttonevent": 4010, "eventtype": "long_press"}]}]}}
    }
}

# ZGPSwitch
sensorTypes["ZGPSWITCH"] = {
    "ZGPSwitch": {
        "state": {"buttonevent": 0, "lastupdated": "none"},
        "config": {"on": True, "battery": 100, "reachable": True},
        "static": {"manufacturername": "Signify Netherlands B.V.", "swversion": ""}
    }
}

# Aliases for other switches
sensorTypes["RWL020"] = sensorTypes["RWL021"]
sensorTypes["RWL022"] = sensorTypes["RWL021"]

# IKEA TRADFRI remote control
sensorTypes["TRADFRI remote control"] = {
    "ZHASwitch": {
        "state": {"buttonevent": 1002, "lastupdated": "none"},
        "config": {"alert": "none", "battery": 90, "on": True, "reachable": True},
        "static": {"swversion": "1.2.214", "manufacturername": "IKEA of Sweden"}
    }
}

# IKEA TRADFRI on/off switch
sensorTypes["TRADFRI on/off switch"] = sensorTypes["TRADFRI remote control"]

# IKEA TRADFRI wireless dimmer
sensorTypes["TRADFRI wireless dimmer"] = sensorTypes["TRADFRI remote control"]

sensorTypes["Remote Control N2"] = sensorTypes["TRADFRI remote control"]

# Fix Deconz types
# not used anymore?
# sensorTypes["RWL020"]["ZHASwitch"] = sensorTypes["RWL020"]["ZLLSwitch"]
# sensorTypes["RWL022"]["ZHASwitch"] = sensorTypes["RWL022"]["ZLLSwitch"]
# sensorTypes["SML001"]["ZHATemperature"] = sensorTypes["SML001"]["ZLLTemperature"]
# sensorTypes["SML001"]["ZHAPresence"] = sensorTypes["SML001"]["ZLLPresence"]
# sensorTypes["SML001"]["ZHALightLevel"] = sensorTypes["SML001"]["ZLLLightLevel"]
