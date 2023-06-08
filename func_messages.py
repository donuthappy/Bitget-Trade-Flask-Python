def wait_message(message):
    print(' --- ⌛ ' + str(message) + '  ---')

def done_message(message):
    print(' --- ✅ ' + str(message) + '  ---')

def warning_message(message):
    print(' --- 🚨 ' + str(message) + '  ---')

def kill_message(message):
    print(' --- ❗ ' + str(message) + '  ---')
    print(' --- 💀 R.I.P BOT  💀 ---')

def info_message(message):
    print(' --- ℹ️  ' + str(message) + '  ---')

def success_message(message):
    print(' --- ⭐ ' + str(message) + '  ---')


"""


def send_message(self, message):
    if self.channel_id == None:
        return
    send(message, self.channel_id))

def send_message_to_admin(self, message):
    send(message, self.admin_id))

def add_message( message, message_type=0):
    messages.append([message, message_type])
"""