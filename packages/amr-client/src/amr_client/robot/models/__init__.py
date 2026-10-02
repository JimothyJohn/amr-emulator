"""Contains all the data models used in inputs/outputs"""

from .error import Error
from .get_action_definition import GetActionDefinition
from .get_action_definition_descriptions_item import GetActionDefinitionDescriptionsItem
from .get_action_definition_parameters_item import GetActionDefinitionParametersItem
from .get_action_definitions import GetActionDefinitions
from .get_action_definitions_descriptions_item import GetActionDefinitionsDescriptionsItem
from .get_action_definitions_parameters_item import GetActionDefinitionsParametersItem
from .get_cart import GetCart
from .get_cart_calibration import GetCartCalibration
from .get_cart_calibrations import GetCartCalibrations
from .get_cart_type import GetCartType
from .get_cart_types import GetCartTypes
from .get_carts import GetCarts
from .get_cert import GetCert
from .get_clear_site_data import GetClearSiteData
from .get_dashboard import GetDashboard
from .get_dashboard_widget import GetDashboardWidget
from .get_dashboard_widgets import GetDashboardWidgets
from .get_dashboards import GetDashboards
from .get_diagnostics import GetDiagnostics
from .get_distance_statistics import GetDistanceStatistics
from .get_docking_offset import GetDockingOffset
from .get_docking_offset_type import GetDockingOffsetType
from .get_docking_offset_types import GetDockingOffsetTypes
from .get_docking_offsets import GetDockingOffsets
from .get_docking_offsets_no_pos import GetDockingOffsetsNoPos
from .get_elevator import GetElevator
from .get_elevator_floor import GetElevatorFloor
from .get_elevator_floors import GetElevatorFloors
from .get_elevators import GetElevators
from .get_error_report import GetErrorReport
from .get_error_report_download import GetErrorReportDownload
from .get_error_reports import GetErrorReports
from .get_factory_reset import GetFactoryReset
from .get_footprint import GetFootprint
from .get_footprints import GetFootprints
from .get_group_action_definition import GetGroupActionDefinition
from .get_group_action_definition_descriptions_item import GetGroupActionDefinitionDescriptionsItem
from .get_group_action_definition_parameters_item import GetGroupActionDefinitionParametersItem
from .get_group_missions import GetGroupMissions
from .get_guided_move import GetGuidedMove
from .get_guided_move_waypoints import GetGuidedMoveWaypoints
from .get_helper_positions import GetHelperPositions
from .get_hook import GetHook
from .get_hook_brake import GetHookBrake
from .get_hook_brake_document import GetHookBrakeDocument
from .get_hook_gripper import GetHookGripper
from .get_hook_gripper_document import GetHookGripperDocument
from .get_hook_height import GetHookHeight
from .get_hook_height_document import GetHookHeightDocument
from .get_hook_software_interface import GetHookSoftwareInterface
from .get_hw_config_export import GetHwConfigExport
from .get_hw_config_import import GetHwConfigImport
from .get_io_module import GetIoModule
from .get_io_module_status import GetIoModuleStatus
from .get_io_modules import GetIoModules
from .get_map import GetMap
from .get_map_path_guides import GetMapPathGuides
from .get_map_paths import GetMapPaths
from .get_map_positions import GetMapPositions
from .get_map_record import GetMapRecord
from .get_map_upload import GetMapUpload
from .get_map_uploads import GetMapUploads
from .get_map_zone import GetMapZone
from .get_maps import GetMaps
from .get_me import GetMe
from .get_metrics import GetMetrics
from .get_mission import GetMission
from .get_mission_action import GetMissionAction
from .get_mission_actions import GetMissionActions
from .get_mission_definition import GetMissionDefinition
from .get_mission_group import GetMissionGroup
from .get_mission_groups import GetMissionGroups
from .get_mission_queue import GetMissionQueue
from .get_mission_queue_action import GetMissionQueueAction
from .get_mission_queue_action_parameters_item import GetMissionQueueActionParametersItem
from .get_mission_queue_actions import GetMissionQueueActions
from .get_mission_queue_actions_parameters_item import GetMissionQueueActionsParametersItem
from .get_mission_queues import GetMissionQueues
from .get_missions import GetMissions
from .get_modbu import GetModbu
from .get_modbu_registers_item import GetModbuRegistersItem
from .get_modbus import GetModbus
from .get_modbus_mission import GetModbusMission
from .get_modbus_missions import GetModbusMissions
from .get_modbus_registers_item import GetModbusRegistersItem
from .get_path import GetPath
from .get_path_guide import GetPathGuide
from .get_path_guide_options import GetPathGuideOptions
from .get_path_guide_options_goals_item import GetPathGuideOptionsGoalsItem
from .get_path_guide_options_starts_item import GetPathGuideOptionsStartsItem
from .get_path_guide_options_vias_item import GetPathGuideOptionsViasItem
from .get_path_guide_position import GetPathGuidePosition
from .get_path_guide_positions import GetPathGuidePositions
from .get_path_guides import GetPathGuides
from .get_path_guides_position import GetPathGuidesPosition
from .get_path_guides_positions import GetPathGuidesPositions
from .get_path_guides_precalc import GetPathGuidesPrecalc
from .get_paths import GetPaths
from .get_permission import GetPermission
from .get_permissions import GetPermissions
from .get_pos_docking_offsets import GetPosDockingOffsets
from .get_position import GetPosition
from .get_position_transition_list import GetPositionTransitionList
from .get_position_transition_list_from_session import GetPositionTransitionListFromSession
from .get_position_transition_lists import GetPositionTransitionLists
from .get_position_type import GetPositionType
from .get_position_types import GetPositionTypes
from .get_positions import GetPositions
from .get_protective_scan import GetProtectiveScan
from .get_register import GetRegister
from .get_registers import GetRegisters
from .get_remote_support import GetRemoteSupport
from .get_remote_support_log import GetRemoteSupportLog
from .get_robots import GetRobots
from .get_service_book import GetServiceBook
from .get_service_books import GetServiceBooks
from .get_session import GetSession
from .get_session_elevator_floors import GetSessionElevatorFloors
from .get_session_elevators import GetSessionElevators
from .get_session_export import GetSessionExport
from .get_session_import import GetSessionImport
from .get_session_maps import GetSessionMaps
from .get_session_missions import GetSessionMissions
from .get_sessions import GetSessions
from .get_setting import GetSetting
from .get_setting_advanced import GetSettingAdvanced
from .get_setting_advanced_constraints import GetSettingAdvancedConstraints
from .get_setting_constraints import GetSettingConstraints
from .get_setting_group import GetSettingGroup
from .get_setting_group_advanced_settings import GetSettingGroupAdvancedSettings
from .get_setting_group_settings import GetSettingGroupSettings
from .get_setting_groups import GetSettingGroups
from .get_settings import GetSettings
from .get_settings_advanced import GetSettingsAdvanced
from .get_setup_cameras import GetSetupCameras
from .get_setup_external_interface_serials import GetSetupExternalInterfaceSerials
from .get_setup_laser_serials import GetSetupLaserSerials
from .get_setup_mc_serials import GetSetupMcSerials
from .get_setup_serial_device import GetSetupSerialDevice
from .get_setup_serial_devices import GetSetupSerialDevices
from .get_sick_config import GetSickConfig
from .get_sick_config_download import GetSickConfigDownload
from .get_sick_config_supported_software_version import GetSickConfigSupportedSoftwareVersion
from .get_sick_configs import GetSickConfigs
from .get_software_backup import GetSoftwareBackup
from .get_software_backups import GetSoftwareBackups
from .get_software_log import GetSoftwareLog
from .get_software_logs import GetSoftwareLogs
from .get_software_robot_peripherals_status import GetSoftwareRobotPeripheralsStatus
from .get_software_system_status import GetSoftwareSystemStatus
from .get_software_upgrade import GetSoftwareUpgrade
from .get_software_upgrades import GetSoftwareUpgrades
from .get_sound import GetSound
from .get_sound_stream import GetSoundStream
from .get_sounds import GetSounds
from .get_status import GetStatus
from .get_status_errors_item import GetStatusErrorsItem
from .get_status_hook_data import GetStatusHookData
from .get_status_hook_data_angle import GetStatusHookDataAngle
from .get_status_hook_status import GetStatusHookStatus
from .get_status_hook_status_cart import GetStatusHookStatusCart
from .get_status_position import GetStatusPosition
from .get_status_user_prompt import GetStatusUserPrompt
from .get_status_velocity import GetStatusVelocity
from .get_swagger_doc import GetSwaggerDoc
from .get_system_info import GetSystemInfo
from .get_timezone import GetTimezone
from .get_user import GetUser
from .get_user_group import GetUserGroup
from .get_user_group_permission import GetUserGroupPermission
from .get_user_groups import GetUserGroups
from .get_user_me_group import GetUserMeGroup
from .get_user_me_permissions import GetUserMePermissions
from .get_users import GetUsers
from .get_users_auth import GetUsersAuth
from .get_wifi_api import GetWifiApi
from .get_wifi_connection import GetWifiConnection
from .get_wifi_connections import GetWifiConnections
from .get_wifi_network import GetWifiNetwork
from .get_wifi_networks import GetWifiNetworks
from .get_world_model import GetWorldModel
from .get_zone import GetZone
from .get_zone_action_definition import GetZoneActionDefinition
from .get_zone_action_definitions import GetZoneActionDefinitions
from .get_zone_actions import GetZoneActions
from .get_zone_polygon_item import GetZonePolygonItem
from .get_zones import GetZones
from .get_zones_definitions import GetZonesDefinitions
from .post_action_definition import PostActionDefinition
from .post_action_definition_parameters_item import PostActionDefinitionParametersItem
from .post_cart_calibrations import PostCartCalibrations
from .post_cart_types import PostCartTypes
from .post_carts import PostCarts
from .post_cert import PostCert
from .post_dashboard_widgets import PostDashboardWidgets
from .post_dashboards import PostDashboards
from .post_docking_offsets import PostDockingOffsets
from .post_elevator_floors import PostElevatorFloors
from .post_elevators import PostElevators
from .post_error_reports import PostErrorReports
from .post_factory_reset import PostFactoryReset
from .post_footprints import PostFootprints
from .post_hook_software_interface import PostHookSoftwareInterface
from .post_hw_config_import import PostHwConfigImport
from .post_io_module_status import PostIoModuleStatus
from .post_io_modules import PostIoModules
from .post_map_upload import PostMapUpload
from .post_map_uploads import PostMapUploads
from .post_maps import PostMaps
from .post_mission_actions import PostMissionActions
from .post_mission_actions_parameters_item import PostMissionActionsParametersItem
from .post_mission_groups import PostMissionGroups
from .post_mission_queues import PostMissionQueues
from .post_mission_queues_parameters_item import PostMissionQueuesParametersItem
from .post_missions import PostMissions
from .post_modbus_missions import PostModbusMissions
from .post_modbus_missions_parameters_item import PostModbusMissionsParametersItem
from .post_path_guide_positions import PostPathGuidePositions
from .post_path_guides import PostPathGuides
from .post_path_guides_positions import PostPathGuidesPositions
from .post_path_guides_precalc import PostPathGuidesPrecalc
from .post_paths import PostPaths
from .post_permissions import PostPermissions
from .post_position_transition_lists import PostPositionTransitionLists
from .post_positions import PostPositions
from .post_register import PostRegister
from .post_robots import PostRobots
from .post_robots_robots_item import PostRobotsRobotsItem
from .post_service_books import PostServiceBooks
from .post_session_import import PostSessionImport
from .post_sessions import PostSessions
from .post_sounds import PostSounds
from .post_timezone import PostTimezone
from .post_user_group_permission import PostUserGroupPermission
from .post_user_groups import PostUserGroups
from .post_users import PostUsers
from .post_wifi_connection import PostWifiConnection
from .post_wifi_connection_scan_freqs_item import PostWifiConnectionScanFreqsItem
from .post_wifi_connections import PostWifiConnections
from .post_wifi_connections_scan_freqs_item import PostWifiConnectionsScanFreqsItem
from .post_world_model import PostWorldModel
from .post_world_model_world_model_item import PostWorldModelWorldModelItem
from .post_zones import PostZones
from .post_zones_actions_item import PostZonesActionsItem
from .post_zones_polygon_item import PostZonesPolygonItem
from .put_cart import PutCart
from .put_cart_calibration import PutCartCalibration
from .put_cart_type import PutCartType
from .put_dashboard import PutDashboard
from .put_dashboard_widget import PutDashboardWidget
from .put_docking_offset import PutDockingOffset
from .put_elevator import PutElevator
from .put_elevator_floor import PutElevatorFloor
from .put_footprint import PutFootprint
from .put_guided_move import PutGuidedMove
from .put_hook_brake import PutHookBrake
from .put_hook_gripper import PutHookGripper
from .put_hook_height import PutHookHeight
from .put_io_module import PutIoModule
from .put_io_module_status import PutIoModuleStatus
from .put_map import PutMap
from .put_map_record import PutMapRecord
from .put_me import PutMe
from .put_mission import PutMission
from .put_mission_action import PutMissionAction
from .put_mission_action_parameters_item import PutMissionActionParametersItem
from .put_mission_group import PutMissionGroup
from .put_mission_queue import PutMissionQueue
from .put_modbus_mission import PutModbusMission
from .put_modbus_mission_parameters_item import PutModbusMissionParametersItem
from .put_path import PutPath
from .put_path_guide import PutPathGuide
from .put_path_guide_position import PutPathGuidePosition
from .put_path_guides_position import PutPathGuidesPosition
from .put_position import PutPosition
from .put_position_transition_list import PutPositionTransitionList
from .put_remote_support import PutRemoteSupport
from .put_session import PutSession
from .put_setting import PutSetting
from .put_setting_advanced import PutSettingAdvanced
from .put_setup_cameras import PutSetupCameras
from .put_setup_external_interface_serials import PutSetupExternalInterfaceSerials
from .put_setup_laser_serials import PutSetupLaserSerials
from .put_setup_mc_serials import PutSetupMcSerials
from .put_sound import PutSound
from .put_status import PutStatus
from .put_status_position import PutStatusPosition
from .put_user import PutUser
from .put_user_group import PutUserGroup
from .put_zone import PutZone
from .put_zone_actions_item import PutZoneActionsItem
from .put_zone_polygon_item import PutZonePolygonItem

__all__ = (
    "Error",
    "GetActionDefinition",
    "GetActionDefinitionDescriptionsItem",
    "GetActionDefinitionParametersItem",
    "GetActionDefinitions",
    "GetActionDefinitionsDescriptionsItem",
    "GetActionDefinitionsParametersItem",
    "GetCart",
    "GetCartCalibration",
    "GetCartCalibrations",
    "GetCarts",
    "GetCartType",
    "GetCartTypes",
    "GetCert",
    "GetClearSiteData",
    "GetDashboard",
    "GetDashboards",
    "GetDashboardWidget",
    "GetDashboardWidgets",
    "GetDiagnostics",
    "GetDistanceStatistics",
    "GetDockingOffset",
    "GetDockingOffsets",
    "GetDockingOffsetsNoPos",
    "GetDockingOffsetType",
    "GetDockingOffsetTypes",
    "GetElevator",
    "GetElevatorFloor",
    "GetElevatorFloors",
    "GetElevators",
    "GetErrorReport",
    "GetErrorReportDownload",
    "GetErrorReports",
    "GetFactoryReset",
    "GetFootprint",
    "GetFootprints",
    "GetGroupActionDefinition",
    "GetGroupActionDefinitionDescriptionsItem",
    "GetGroupActionDefinitionParametersItem",
    "GetGroupMissions",
    "GetGuidedMove",
    "GetGuidedMoveWaypoints",
    "GetHelperPositions",
    "GetHook",
    "GetHookBrake",
    "GetHookBrakeDocument",
    "GetHookGripper",
    "GetHookGripperDocument",
    "GetHookHeight",
    "GetHookHeightDocument",
    "GetHookSoftwareInterface",
    "GetHwConfigExport",
    "GetHwConfigImport",
    "GetIoModule",
    "GetIoModules",
    "GetIoModuleStatus",
    "GetMap",
    "GetMapPathGuides",
    "GetMapPaths",
    "GetMapPositions",
    "GetMapRecord",
    "GetMaps",
    "GetMapUpload",
    "GetMapUploads",
    "GetMapZone",
    "GetMe",
    "GetMetrics",
    "GetMission",
    "GetMissionAction",
    "GetMissionActions",
    "GetMissionDefinition",
    "GetMissionGroup",
    "GetMissionGroups",
    "GetMissionQueue",
    "GetMissionQueueAction",
    "GetMissionQueueActionParametersItem",
    "GetMissionQueueActions",
    "GetMissionQueueActionsParametersItem",
    "GetMissionQueues",
    "GetMissions",
    "GetModbu",
    "GetModbuRegistersItem",
    "GetModbus",
    "GetModbusMission",
    "GetModbusMissions",
    "GetModbusRegistersItem",
    "GetPath",
    "GetPathGuide",
    "GetPathGuideOptions",
    "GetPathGuideOptionsGoalsItem",
    "GetPathGuideOptionsStartsItem",
    "GetPathGuideOptionsViasItem",
    "GetPathGuidePosition",
    "GetPathGuidePositions",
    "GetPathGuides",
    "GetPathGuidesPosition",
    "GetPathGuidesPositions",
    "GetPathGuidesPrecalc",
    "GetPaths",
    "GetPermission",
    "GetPermissions",
    "GetPosDockingOffsets",
    "GetPosition",
    "GetPositions",
    "GetPositionTransitionList",
    "GetPositionTransitionListFromSession",
    "GetPositionTransitionLists",
    "GetPositionType",
    "GetPositionTypes",
    "GetProtectiveScan",
    "GetRegister",
    "GetRegisters",
    "GetRemoteSupport",
    "GetRemoteSupportLog",
    "GetRobots",
    "GetServiceBook",
    "GetServiceBooks",
    "GetSession",
    "GetSessionElevatorFloors",
    "GetSessionElevators",
    "GetSessionExport",
    "GetSessionImport",
    "GetSessionMaps",
    "GetSessionMissions",
    "GetSessions",
    "GetSetting",
    "GetSettingAdvanced",
    "GetSettingAdvancedConstraints",
    "GetSettingConstraints",
    "GetSettingGroup",
    "GetSettingGroupAdvancedSettings",
    "GetSettingGroups",
    "GetSettingGroupSettings",
    "GetSettings",
    "GetSettingsAdvanced",
    "GetSetupCameras",
    "GetSetupExternalInterfaceSerials",
    "GetSetupLaserSerials",
    "GetSetupMcSerials",
    "GetSetupSerialDevice",
    "GetSetupSerialDevices",
    "GetSickConfig",
    "GetSickConfigDownload",
    "GetSickConfigs",
    "GetSickConfigSupportedSoftwareVersion",
    "GetSoftwareBackup",
    "GetSoftwareBackups",
    "GetSoftwareLog",
    "GetSoftwareLogs",
    "GetSoftwareRobotPeripheralsStatus",
    "GetSoftwareSystemStatus",
    "GetSoftwareUpgrade",
    "GetSoftwareUpgrades",
    "GetSound",
    "GetSounds",
    "GetSoundStream",
    "GetStatus",
    "GetStatusErrorsItem",
    "GetStatusHookData",
    "GetStatusHookDataAngle",
    "GetStatusHookStatus",
    "GetStatusHookStatusCart",
    "GetStatusPosition",
    "GetStatusUserPrompt",
    "GetStatusVelocity",
    "GetSwaggerDoc",
    "GetSystemInfo",
    "GetTimezone",
    "GetUser",
    "GetUserGroup",
    "GetUserGroupPermission",
    "GetUserGroups",
    "GetUserMeGroup",
    "GetUserMePermissions",
    "GetUsers",
    "GetUsersAuth",
    "GetWifiApi",
    "GetWifiConnection",
    "GetWifiConnections",
    "GetWifiNetwork",
    "GetWifiNetworks",
    "GetWorldModel",
    "GetZone",
    "GetZoneActionDefinition",
    "GetZoneActionDefinitions",
    "GetZoneActions",
    "GetZonePolygonItem",
    "GetZones",
    "GetZonesDefinitions",
    "PostActionDefinition",
    "PostActionDefinitionParametersItem",
    "PostCartCalibrations",
    "PostCarts",
    "PostCartTypes",
    "PostCert",
    "PostDashboards",
    "PostDashboardWidgets",
    "PostDockingOffsets",
    "PostElevatorFloors",
    "PostElevators",
    "PostErrorReports",
    "PostFactoryReset",
    "PostFootprints",
    "PostHookSoftwareInterface",
    "PostHwConfigImport",
    "PostIoModules",
    "PostIoModuleStatus",
    "PostMaps",
    "PostMapUpload",
    "PostMapUploads",
    "PostMissionActions",
    "PostMissionActionsParametersItem",
    "PostMissionGroups",
    "PostMissionQueues",
    "PostMissionQueuesParametersItem",
    "PostMissions",
    "PostModbusMissions",
    "PostModbusMissionsParametersItem",
    "PostPathGuidePositions",
    "PostPathGuides",
    "PostPathGuidesPositions",
    "PostPathGuidesPrecalc",
    "PostPaths",
    "PostPermissions",
    "PostPositions",
    "PostPositionTransitionLists",
    "PostRegister",
    "PostRobots",
    "PostRobotsRobotsItem",
    "PostServiceBooks",
    "PostSessionImport",
    "PostSessions",
    "PostSounds",
    "PostTimezone",
    "PostUserGroupPermission",
    "PostUserGroups",
    "PostUsers",
    "PostWifiConnection",
    "PostWifiConnections",
    "PostWifiConnectionScanFreqsItem",
    "PostWifiConnectionsScanFreqsItem",
    "PostWorldModel",
    "PostWorldModelWorldModelItem",
    "PostZones",
    "PostZonesActionsItem",
    "PostZonesPolygonItem",
    "PutCart",
    "PutCartCalibration",
    "PutCartType",
    "PutDashboard",
    "PutDashboardWidget",
    "PutDockingOffset",
    "PutElevator",
    "PutElevatorFloor",
    "PutFootprint",
    "PutGuidedMove",
    "PutHookBrake",
    "PutHookGripper",
    "PutHookHeight",
    "PutIoModule",
    "PutIoModuleStatus",
    "PutMap",
    "PutMapRecord",
    "PutMe",
    "PutMission",
    "PutMissionAction",
    "PutMissionActionParametersItem",
    "PutMissionGroup",
    "PutMissionQueue",
    "PutModbusMission",
    "PutModbusMissionParametersItem",
    "PutPath",
    "PutPathGuide",
    "PutPathGuidePosition",
    "PutPathGuidesPosition",
    "PutPosition",
    "PutPositionTransitionList",
    "PutRemoteSupport",
    "PutSession",
    "PutSetting",
    "PutSettingAdvanced",
    "PutSetupCameras",
    "PutSetupExternalInterfaceSerials",
    "PutSetupLaserSerials",
    "PutSetupMcSerials",
    "PutSound",
    "PutStatus",
    "PutStatusPosition",
    "PutUser",
    "PutUserGroup",
    "PutZone",
    "PutZoneActionsItem",
    "PutZonePolygonItem",
)
