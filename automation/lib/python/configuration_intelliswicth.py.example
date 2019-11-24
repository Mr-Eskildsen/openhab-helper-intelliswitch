# -*- coding: utf-8 -*-
LOG_PREFIX = "org.openhab.jsr223.jython"

admin_email = "admin_email@some_domain.com"

openhabHost = "localhost"
openhabPort = "8080"# "8443"



intelliswitch_configuration = {
    'LOGGING_LEVEL': 'DEBUG',
	#'LOCATION' : {'latitude':10, 'longitude': 50 },
	'MANAGERS' : [
        {'name': 'LightManager',
		'description': 'Automatic light schedule for livingroom',
		'RULES': [
			{'name': 'AutoLightSchedule-1', 'description': '', 'type': 'schedule', 
			'SCHEDULES': [ 
				{'begin':'16:10', 'end':'16:50'}, 
				{'begin':'17:00', 'end':'17:40'}, 
				{'begin':'18:10', 'end':'18:50'}, 
				{'begin':'19:10', 'end':'19:50'}, 
				{'begin':'20:10', 'end':'20:50'}, 
				{'begin':'21:10', 'end':'21:50'}, 
				{'begin':'22:10', 'end':'22:50'},
				{'begin':'23:10', 'end':'23:50'},
				{'begin': '0:10', 'end': '0:50'} ],
			'CONDITIONS': [
				{'type':'item', 'name':'switchLightScheduleTest'},
				{'type':'check', 'name':'ActiveNight'}],
			'OUTPUTS': [
				{'type':'item', 'name':'switchLightLivingroomTest1'}]
			},
			
			{'name': 'AutoLightSchedule-3', 'description': 'Automatic light schedule for office', 'type': 'schedule', 
			'SCHEDULES': [ 
				{'begin':'16:40', 'end':'17:25'}, 
				{'begin':'17:40', 'end':'18:25'}, 
				{'begin':'18:40', 'end':'17:25'}, 
				{'begin':'19:40', 'end':'20:25'}, 
				{'begin':'20:40', 'end':'21:25'}, 
				{'begin':'21:40', 'end':'22:25'}, 
				{'begin':'22:40', 'end':'23:25'},
				{'begin':'23:40', 'end': '0:25'},
				{'begin': '0:40', 'end': '1:25'} ],
			'CONDITIONS': [
				{'type':'item', 'name':'switchLightScheduleTest'},
				{'type':'check', 'name':'ActiveNight'}],
			'OUTPUTS': [
				{'type':'item', 'name':'switchLightOfficeTest1'}]
			},
			#StateTriggerRule("Light_Carport_Doors", ["sensorEntranceDoor1", "sensorBackentranceDoor1"], [SwitchOutput("switchLightDriveway",0, 30)], [ActiveNightCondition()])
			{'name': 'Light_Carport_Doors', 'description': 'Turnon light when opening front or backdoor', 'type': 'trigger', 
			'TRIGGERS': [ 
				"sensorEntranceDoor1", 
				"sensorBackentranceDoor1"],
			'CONDITIONS': [
				{'type':'check', 'name':'ActiveNight'}],
			'OUTPUTS': [
				{'type':'item', 'name':'switchLightDriveway', 'delay':0, 'timeout':30 }]
			},
			#mySwitchManager.Add(IntelliSwitch_StateRule("Light_BackyardDoor", ["sensorBackyardDoor"], [SwitchOutput("switchLightSmallSpot",0, 60),  SwitchOutput("switchLightDriveway",0, 10)], [ActiveNightCondition()]))
			{'name': 'Light_BackyardDoor', 'description': 'Turn on light in backyard when opening door to backyard at night', 'type': 'trigger', 
			'TRIGGERS': [ 
				"sensorBackyardDoor"],
			'CONDITIONS': [
				{'type':'check', 'name':'ActiveNight'}],
			'OUTPUTS': [
				#[SwitchOutput("switchLightSmallSpot",0, 60),  SwitchOutput("switchLightDriveway",0, 10)]
				{'type':'item', 'name':'switchLightSmallSpot', 'delay':0, 'timeout':60 },
				{'type':'item', 'name':'switchLightDriveway', 'delay':0, 'timeout':10 }]
			},
			{'name': 'Light TestRule-1', 'description': 'Test Rule', 'type': 'trigger', 
			'TRIGGERS': [ 
				"switchTestTrigger"],
			'CONDITIONS': [
				{'type':'item', 'name':'switchTestCondition'}],
			'OUTPUTS': [
				{'type':'item', 'name':'switchTestOutput', 'delay':0, 'timeout':5 }]
			},
			{'name': 'Light TestRule-2', 'description': 'Test Rule (Active Night)', 'type': 'trigger', 
			'TRIGGERS': [ 
				"switchTestTrigger2"],
			'CONDITIONS': [
				{'type':'item', 'name':'switchTestCondition2'},
				{'type':'check', 'name':'ActiveNight'}],
			'OUTPUTS': [
				{'type':'item', 'name':'switchTestOutput', 'delay':0, 'timeout':20 },
				{'type':'item', 'name':'switchTestOutput2', 'delay':0, 'timeout':5 }]
			}			
		]}
	]
}

		
		
'''
{
	'name': 'AutoLightSchedule-2',
	'description': '',
	'rules': [
		{'name': 'lm2-rule1', 'description': '', 'type': 'trigger', 'triggers': '', 'conditions': '', 'output': ''},
		{'name': 'lm2-rule2', 'description': '', 'type': 'schedule', 'schedules': '', 'conditions': '', 'output': ''}
	]
}	
'''	

'''
	mySwitchManager.Add(ScheduleRule("AutoLightSchedule-1", [TimeInterval("16:10", "16:50"), TimeInterval("17:00", "17:40"), TimeInterval("18:10", "18:50"), TimeInterval("19:10", "19:50"), TimeInterval("20:10", "20:50"), TimeInterval("21:10", "21:50"), TimeInterval("22:10", "22:50"), TimeInterval("23:10", "23:50"), TimeInterval("0:10", "0:50") ], ["switchLightLivingroomTest1"], ["switchLightScheduleTest", ActiveNightCondition()]))
	mySwitchManager.Add(ScheduleRule("AutoLightSchedule-2", [TimeInterval("16:40", "17:25"), TimeInterval("17:40", "18:25"), TimeInterval("18:40", "19:25"), TimeInterval("19:40", "20:25"), TimeInterval("20:40", "21:25"), TimeInterval("21:40", "22:25"), TimeInterval("22:40", "23:25"), TimeInterval("23:40", "00:25"), TimeInterval("0:40", "1:25") ], ["switchLightOfficeTest1"], ["switchLightScheduleTest", ActiveNightCondition()]))
	
	mySwitchManager.Add(ScheduleRule("OutdoorChristmaslight-1", [TimeInterval("15:00", "23:00")], ["switchPlugTerrace"], [ActiveNightCondition()]))
	

	# ##########################
	#
	# Convinience
	#
	# ##########################
	mySwitchManager.Add(StateTriggerRule("Light_Carport_Doors", ["sensorEntranceDoor1", "sensorBackentranceDoor1"], [SwitchOutput("switchLightDriveway",0, 30)], [ActiveNightCondition()]))

	
	mySwitchManager.Add(IntelliSwitch_StateRule("Light_ClockCabinet", ["switchLightLivingroom1"], ["clockCabinetLight"], [ActiveNightCondition()]))

	mySwitchManager.Add(IntelliSwitch_StateRule("Light_Terrace", ["sensorLivingroomDoor1"], [SwitchOutput("switchLightTerrace",0, 300)], [ActiveNightCondition()]))


	# ##########################
	#
	# Security (Light & Cameras)
	#
	# ##########################

	#Backyard door light
	mySwitchManager.Add(IntelliSwitch_StateRule("Light_BackyardDoor", ["sensorBackyardDoor"], [SwitchOutput("switchLightSmallSpot",0, 60),  SwitchOutput("switchLightDriveway",0, 10)], [ActiveNightCondition()]))

	#TODO:: Change to a OneShoot trigger when it because available
	mySwitchManager.Add(IntelliSwitch_StateRule("Zoneminder_StartRecDriveway", ["Alarm_Zone_Outdoor_Carport", "sensorEntranceDoor1", "sensorBackentranceDoor1"], [SwitchOutput("zmMonitor2_ForceAlarm", 0, 120)]))

	mySwitchManager.Add(IntelliSwitch_StateRule("Zoneminder_StartRecBackyard", ["Alarm_Zone_Outdoor_Backyard"], [SwitchOutput("zmMonitor1_ForceAlarm", 0, 120), SwitchOutput("zmMonitor2_ForceAlarm", 0, 120), SwitchOutput("zmMonitor3_ForceAlarm", 0, 120)]))
	mySwitchManager.Add(IntelliSwitch_StateRule("Zoneminder_StartRecTerrace", ["Alarm_Zone_Outdoor_Terrace"], [SwitchOutput("zmMonitor3_ForceAlarm", 0, 120)]))


	# ##########################
	#
	# Alarm
	#
	# ##########################
	mySwitchManager.Add(IntelliSwitch_StateRule("Alarm_Zone_Terrace", ["Alarm_Zone_Outdoor_Terrace"], [SwitchOutput("switchLightSmallSpot",0, 120)], []))
	mySwitchManager.Add(IntelliSwitch_StateRule("Alarm_Zone_Backyard", ["Alarm_Zone_Outdoor_Backyard"], [SwitchOutput("switchLightDriveway",0, 300), SwitchOutput("switchLightSmallSpot",0, 300), SwitchOutput("switchLightLargeSpot",0, 300)], []))
	mySwitchManager.Add(IntelliSwitch_StateRule("Alarm_Zone_Carport", ["Alarm_Zone_Outdoor_Carport"], [SwitchOutput("switchLightSmallSpot",0, 120),SwitchOutput("switchLightLargeSpot",0, 120)], []))


	# ##########################
	#
	# Test
	#
	# ##########################
	mySwitchManager.Add(IntelliSwitch_StateRule("Test_Rule", ["switchTestInput"], [SwitchOutput("switchTestOutput",0, 20)], []))
'''
'''
intelliswitch_configuration = {
    'LOGGING_LEVEL': 'DEBUG',
	'MANAGERS' : [
        {
            'name': 'LightManager-1',
			'description': '',
			'rules': {
				{'name': '', 'description': '', 'type': 'trigger', 'triggers': '', 'conditions': '', 'output': ''},
				{'name': '', 'description': '', 'type': 'schedule', 'schedules': '', 'conditions': '', 'output': ''}
			}
		},
		{
            'name': 'LightManager-2',
			'description': '',
			'rules': {
				{'name': '', 'description': '', 'type': 'trigger', 'triggers': '', 'conditions': '', 'output': ''},
				{'name': '', 'description': '', 'type': 'schedule', 'schedules': '', 'conditions': '', 'output': ''}
			}
		}
	] 
}
'''
'''
idealarm_configuration = {
    #'ALARM_TEST_MODE': True,
	'ALARM_TEST_MODE': False,
    'LOGGING_LEVEL': 'DEBUG',
    'NAG_INTERVAL_MINUTES': 6,
    'ALARM_ZONES': [
        {
            'name': 'House Perimeter',
            'armingModeItem': 'Z1_Arming_Mode',
            'statusItem': 'Z1_Status',
            'alertDevices': ['Z1_Sirens'],
            'sensors': [
				{'name': 'switchIdeAlarmTrigger1', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True},
				{'name': 'switchIdeAlarmTrigger2', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True},
                {'name': 'sensorOfficeWindow1', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': False},
                {'name': 'sensorEntranceDoor1', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': False},
				{'name': 'sensorBackentranceDoor1', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': False}
            ],
            'armAwayToggleSwitch': 'Toggle_Z1_Armed_Away',
            'armHomeToggleSwitch': 'Toggle_Z1_Armed_Home',
            'mainZone': True,
            'canArmWithTrippedSensors': False,
			'autoReset': True
        }
		,
        {
            'name': 'Outdoor Perimeter',
            'armingModeItem': 'Z2_Arming_Mode',
            'statusItem': 'Z2_Status',
            'alertDevices': ['Z2_Sirens'],
            'sensors': [
				{'name': 'switchIdeAlarmTrigger2', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True}
#                {'name': 'Door_2_Lock', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True},
#                {'name': 'Window_Room_1', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True},
#                {'name': 'Window_Room_2', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True},
#                {'name': 'Window_Bathroom_2', 'sensorClass': 'A', 'nag': True, 'nagTimeoutMins': 4, 'armWarn': True, 'enabled': True},
#                {'name': 'MD_Bathroom_2', 'sensorClass': 'B', 'nag': False, 'nagTimeoutMins': 4, 'armWarn': False, 'enabled': False}
            ],
            'armAwayToggleSwitch': 'Toggle_Z2_Armed_Away',
            'armHomeToggleSwitch': 'Toggle_Z2_Armed_Home',
            'mainZone': False,
            'canArmWithTrippedSensors': True,
			'autoReset': False
        }
    ] 
}
'''
