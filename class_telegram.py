from telegram import Bot
from asyncio import run

class push_notification:
    message_types = {
        "info": 0,
        "error": 1,
        "success": 2,
        "warning": 3
    }

    def __init__(self, bot_value) -> None:
        self.messages = []
        self.channel_id = None
        self.admin_id = "5969715910"
        self.bot_value = bot_value

    def add_token(self, token):
        self.bot = Bot(token)
  
    def send_notification(self):
        if self.channel_id == None:
            return
        
        messages = []
        match self.bot_value:
            case 0:
                success_messages = list(filter(lambda m: m[1] == 2, self.messages))
                info_and_warning_messages = list(filter(lambda m: m[1] == 0 or m[1] == 3, self.messages))
                info_and_warning_messages.pop(0)

                messages.append(self.messages[0])
                messages.extend(success_messages)
                if len(info_and_warning_messages) > 1:
                    messages.extend(info_and_warning_messages)
            case 2:
                success_messages = list(filter(lambda m: m[1] == 2, self.messages))
                if len(success_messages) > 0:
                    messages.append(self.messages[0])
                    messages.extend(success_messages)
            case 1:
                success_messages = list(filter(lambda m: m[1] == 2, self.messages))
                if len(success_messages) > 0:
                    messages.append(self.messages[0])
                    messages.extend(success_messages)
                    messages.extend(self.messages[len(self.messages)])
            case 3:
                error_and_warning_messages = list(filter(lambda m: m[1] == 1 or m[1] == 3, self.messages))
                if len(error_and_warning_messages) > 0:
                    messages.append(self.messages[0])
                    messages.extend(error_and_warning_messages)
                    
        msg = ""
        for message in messages:
            print(message[0])
            msg += message[0] + "\n\n"

        run(self.send(msg, self.channel_id))
        self.messages = []

    def send_message(self, message):
        if self.channel_id == None:
            return
        run(self.send(message, self.channel_id))

    def send_message_to_admin(self, message):
        run(self.send(message, self.admin_id))

    def add_message(self, message, message_type=0):
        self.messages.append([message, message_type])

    async def send(self, message, channel_id):
      await self.bot.send_message(chat_id=channel_id, text=str(message))