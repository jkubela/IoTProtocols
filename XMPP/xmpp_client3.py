import sleekxmpp

xmpp = None

def main():
	global xmpp

	xmpp = sleekxmpp.ClientXMPP('bob@localhost', 'root')
	xmpp.add_event_handler("session_start", start)
	xmpp.add_event_handler("message", message)
	xmpp.register_plugin('xep_0030')
	xmpp.register_plugin('xep_0199')
	xmpp.connect()
	xmpp.process(block=True)

def start(event):
	xmpp.send_presence()
	xmpp.get_roster()
	xmpp.send_message(mto='alice@localhost', mbody='test', mtype='chat')

def message(msg):
	print('Got a message')
        xmpp.send_message(mto='alice@localhost', mbody='test', mtype='chat')

if __name__ == '__main__':
	main()
