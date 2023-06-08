class ErrorMessages:
    def __init__(self):
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def clear_messages(self):
        self.messages.clear()