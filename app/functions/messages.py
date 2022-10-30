from common.config import *
from common.errors import *
from common.notifications import *
from common.states import states
from domain.Message import Message
from utils.logging import logger
from database.database_sqlite import DatabaseSQLite
from utils.speech.yandex_synthesis import synthesis_text


class Messages:

	def __init__(self):
		self.db = DatabaseSQLite()


	def get_contact_by_from_id(self, id: int, service: str):
		try:
			for contact in states.get_contacts():
				if service == TELEGRAM_MESSAGES_NOTIFICATION:
					if contact.telegram_id == id:
						return contact
				
				elif service == VK_MESSAGES_NOTIFICATION:
					if contact.vk_id == id:
						return contact

			return 0
		except Exception as e:
			logger.error(e)
			return -1


	def new_telegram_message(self, message: dict):
		'''
			Обработка полученного нового сообщения из Телеграм
		'''
		try:
			# тут будет ошибка, если сообщение отправлено не от человека, а от канала или чата
			from_id = int(message['from_id']['user_id'])
			
			match self.get_contact_by_from_id(from_id, TELEGRAM_MESSAGES_NOTIFICATION):
				case -1:
					logger.error(ERROR_GET_CONTACT_BY_TELEGRAM_ID)

				case 0:
					pass 
					# сообщение не от контакта или от канала/чата

				case contact if type(contact) == tuple:
					if not states.get_mute_state():
						answer = f'У вас новое сообщение в Телеграм от контакта {contact[1]}'
						if contact[2]:
							answer += f' {contact[2]}'
						synthesis_text(answer)

					new_message = Message(
						text = message['message'],
						contact_id = contact.id,
						first_name = contact.first_name,
						last_name = contact.last_name
					)

					states.change_notifications(
						TELEGRAM_MESSAGES_NOTIFICATION, 
						new_message
					)

					result = self.db.add_telegram_message(new_message)
					if result == 0:
						logger.error(ERROR_ADD_TELEGRAM_MESSAGE)

		except Exception as e:
			logger.error(e)


	def new_vk_message(self, event):
		'''
			Обработка полученного нового сообщения из ВКонтакте
		'''
		try:
			if event.from_user:
				match self.get_contact_by_from_id(event.user_id, VK_MESSAGES_NOTIFICATION):
					case -1:
						logger.error(ERROR_GET_CONTACT_BY_VK_ID)

					case 0:
						pass
						#match self.get_user_data_by_id(event.user_id):
						#	case 0:
						#		logger.error(FAILED_GET_USER_DATA_BY_ID)
						#	case -1:
						#		logger.error(ERROR_GET_USER_DATA_BY_ID)

						#	case user if type(user) == dict:
						#		print(user)
						#		if not states.get_mute_state():
						#			answer = f'У вас новое сообщение в Вконтакте от пользователя {user["first_name"]}'
						#			if user["last_name"]:
						#				answer += f' {user["last_name"]}'
						#			synthesis_text(answer)

						#		new_message = Message(
						#			text = event.text, 
						#			from_id = event.user_id,
						#			first_name = user['first_name'],
						#			last_name = user['last_name']
						#		)

						#		states.change_notifications(
						#			VK_MESSAGES_NOTIFICATION, 
						#			new_message
						#		)

						#		result = self.db.add_vk_message(new_message)
						#		if result == 0:
						#			logger.error(ERROR_ADD_VK_MESSAGE)

					case contact if type(contact) == tuple:
						if not states.get_mute_state():
							answer = f'У вас новое сообщение в Вконтакте от контакта {contact[1]}'
							if contact[2]:
								answer += f' {contact[2]}'
							synthesis_text(answer)

						new_message = Message(
							text = event.text,
							contact_id = contact.id,
							first_name = contact.first_name,
							last_name = contact.last_name
						)

						states.change_notifications(
							VK_MESSAGES_NOTIFICATION, 
							new_message
						)

						result = self.db.add_vk_message(new_message)
						if result == 0:
							logger.error(ERROR_ADD_VK_MESSAGE)

			elif event.from_chat:
				synthesis_text('У вас новое сообщение в беседе')

		except Exception as e:
			logger.error(e)
