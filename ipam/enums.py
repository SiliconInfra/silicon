from enum import Enum


class ChoiceEnum(Enum):
	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)


class PrefixStatusChoices(ChoiceEnum):
	STATUS_CONTAINER = 'container'
	STATUS_ACTIVE = 'active'
	STATUS_RESERVED = 'reserved'
	STATUS_DEPRECATED = 'deprecated'


class IPAddressStatusChoices(ChoiceEnum):
	STATUS_ACTIVE = 'active'
	STATUS_RESERVED = 'reserved'
	STATUS_DEPRECATED = 'deprecated'
	STATUS_DHCP = 'dhcp'
	STATUS_SLAAC = 'slaac'


class VLANStatusChoices(ChoiceEnum):
	STATUS_ACTIVE = 'active'
	STATUS_RESERVED = 'reserved'
	STATUS_DEPRECATED = 'deprecated'


class ServiceProtocolChoices(ChoiceEnum):
	PROTOCOL_TCP = 'tcp'
	PROTOCOL_UDP = 'udp'
