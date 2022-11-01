from enum import Enum


class TopicsNames(Enum):
	EXIT_TOPIC = 'exit'
	NOTIFICATIONS_TOPIC = 'notifications'
	TELEGRAM_MESSAGES_TOPIC = 'telegram_messages'
	VK_MESSAGES_TOPIC = 'vk_messages'
	SOUND_TOPIC = 'sound'
	CONTACTS_TOPIC = 'contacts'