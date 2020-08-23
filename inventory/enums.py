from enum import Enum


class ChoiceEnum(Enum):
	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)


class CableTypes(ChoiceEnum):
	TYPE_CAT3 = 'cat3'
	TYPE_CAT5 = 'cat5'
	TYPE_CAT5E = 'cat5e'
	TYPE_CAT6 = 'cat6'
	TYPE_CAT6A = 'cat6a'
	TYPE_CAT7 = 'cat7'
	TYPE_DAC_ACTIVE = 'dac-active'
	TYPE_DAC_PASSIVE = 'dac-passive'
	TYPE_MRJ21_TRUNK = 'mrj21-trunk'
	TYPE_COAXIAL = 'coaxial'
	TYPE_MMF = 'mmf'
	TYPE_MMF_OM1 = 'mmf-om1'
	TYPE_MMF_OM2 = 'mmf-om2'
	TYPE_MMF_OM3 = 'mmf-om3'
	TYPE_MMF_OM4 = 'mmf-om4'
	TYPE_SMF = 'smf'
	TYPE_SMF_OS1 = 'smf-os1'
	TYPE_SMF_OS2 = 'smf-os2'
	TYPE_AOC = 'aoc'
	TYPE_POWER = 'power'


class CableStatus(ChoiceEnum):
	STATUS_CONNECTED = 'connected'
	STATUS_PLANNED = 'planned'
	STATUS_DECOMMISSIONING = 'decommissioning'


class CableLengthUnit(ChoiceEnum):
	UNIT_METER = 'm'
	UNIT_CENTIMETER = 'cm'
	UNIT_FOOT = 'ft'
	UNIT_INCH = 'in'


class DeviceFaceChoices(ChoiceEnum):
	FACE_FRONT = 'front'
	FACE_REAR = 'rear'


class DeviceStatusChoices(ChoiceEnum):
	STATUS_OFFLINE = 'offline'
	STATUS_ACTIVE = 'active'
	STATUS_PLANNED = 'planned'
	STATUS_STAGED = 'staged'
	STATUS_FAILED = 'failed'
	STATUS_INVENTORY = 'inventory'
	STATUS_DECOMMISSIONING = 'decommissioning'
