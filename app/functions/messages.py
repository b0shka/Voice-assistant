from common.config import *
from common.states import states
from domain.data_class.Contact import Contact
from domain.data_class.Message import Message
from domain.enum_class.Errors import Errors
from domain.enum_class.Services import Services
from database.database_sqlite import DatabaseSQLite
from utils.logging import logger
from utils.speech.yandex_synthesis import synthesis_text


class Messages:

	def __init__(self) -> None:
		self.db = DatabaseSQLite()


	def say_error(self, error: Errors) -> None:
		synthesis_text(error.value)


	def get_contact_by_from_id(self, id: int, service: Services) -> Contact | Errors:
		try:
			for contact in states.CONTACTS:
				if service == Services.TELEGRAM:
					if contact.telegram_id == id:
						return contact
				
				elif service == Services.VK:
					if contact.vk_id == id:
						return contact

			return Errors.NOT_FOUND_CONTACT_BY_FROM_ID
		except Exception as e:
			match service:
				case Services.TELEGRAM:
					return Errors.GET_CONTACT_BY_TELEGRAM_ID
				case Services.VK:
					return Errors.GET_CONTACT_BY_VK_ID

			logger.error(e)


	def new_telegram_message(self, message: dict) -> None:
		'''Обработка полученного нового сообщения из Телеграм'''

		try:
			# тут будет ошибка, если сообщение отправлено не от человека, а от канала или чата
			from_id = int(message['from_id']['user_id'])
			
			match self.get_contact_by_from_id(from_id, Services.TELEGRAM):
				case Errors.GET_CONTACT_BY_TELEGRAM_ID:
					self.say_error(contact)
					
				case Errors.NOT_FOUND_CONTACT_BY_FROM_ID:
					pass # сообщение не от контакта или от канала/чата

				case Contact(contact):
					if not states.MUTE:
						answer = f'У вас новое сообщение в Телеграм от контакта {contact.first_name}'
						if contact.last_name:
							answer += f' {contact.last_name}'
						synthesis_text(answer)

					new_message = Message(
						text = message['message'],
						contact_id = contact.id,
						first_name = contact.first_name,
						last_name = contact.last_name
					)

					states.NOTIFICATIONS.telegram_messages.append(new_message)
					error = self.db.add_telegram_message(new_message)
					if isinstance(error, Errors):
						self.say_error(error)

		except Exception as e:
			self.say_error(Errors.PROCESSING_NEW_TELEGRAM_MESSAGE)
			logger.error(e)


	def new_vk_message(self, event) -> None:
		'''Обработка полученного нового сообщения из ВКонтакте'''

		try:
			if event.from_user:
				contact = self.get_contact_by_from_id(event.user_id, Services.VK)

				match contact:
					case Errors.GET_CONTACT_BY_VK_ID:
						self.say_error(contact)
						
					case Errors.NOT_FOUND_CONTACT_BY_FROM_ID:
						pass
						#match self.get_user_data_by_id(event.user_id):
						#	case contact if isinstance(contact, Errors):
						#		synthesis_text(contact.value)

						#	case user if isinstance(user, dict):
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

						#		error = self.db.add_vk_message(new_message)
						#		if isinstance(error, Errors):
						#			synthesis_text(error.value)

					case contact if isinstance(contact, Contact):
						if not states.MUTE:
							answer = f'У вас новое сообщение в Вконтакте от контакта {contact.first_name}'
							if contact.last_name:
								answer += f' {contact.last_name}'
							synthesis_text(answer)

						new_message = Message(
							text = event.text,
							contact_id = contact.id,
							first_name = contact.first_name,
							last_name = contact.last_name
						)

						states.NOTIFICATIONS.vk_messages.append(new_message)
						error = self.db.add_vk_message(new_message)
						if isinstance(error, Errors):
							self.say_error(error)

			elif event.from_chat:
				synthesis_text('У вас новое сообщение в беседе')

		except Exception as e:
			self.say_error(Errors.PROCESSING_NEW_VK_MESSAGE)
			logger.error(e)
