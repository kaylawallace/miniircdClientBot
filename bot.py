import socket
import select
import errno
import sys
import datetime
from random import randrange

# HEADER_LENGTH = 10

# Change this IP if you need to run outwith the virtual machines
IP = "10.0.42.17"
PORT = 6667
bot_uname = "ProBot"
bot_nickname = "ProBot"
bot_realname = "ProBot"
channel = "test"
msg = ""

# connect to the socket using the IP and Port set above 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# function to initialise the bot 
def botInit():
	# encode the bots username to utf-8
	uname = bot_uname.encode("utf-8")

	# send the connection message to the server in the format hexchat uses 
	init_botmsg = "NICK " + \
		bot_nickname + "\r\n" + \
		"USER " + bot_uname + " " + \
		bot_realname + " " + \
		socket.gethostbyname(socket.gethostname()) + " " + \
		":realname\r\n"
	# encode the connection message to utf-8 and send to the server 
	init_botmsg = f"{init_botmsg}".encode("utf-8")
	client_socket.send(init_botmsg)

	# join the channel set above by sending a message to the server (encoded in utf-8) in the format hexchat uses 
	join = ("JOIN #" + channel + "\r\n")
	join = f"{join}".encode("utf-8")
	client_socket.send(join)

# function to recieve messages 
# return: msgReceived - the message received from this function
def recvMsg():
	while True:
		try:
			msgReceived = client_socket.recv(1024)
			# print error message and stop running if the connection is closed by the server
			if not len(msgReceived):
				print("connection closed by server")
				sys.exit()

			# decode the message recieved with utf-8
			msgReceived = msgReceived.decode("utf-8")
			print("Message Received: ", msgReceived)
			# call function that deals with the different responses of the bot  
			botReplies(msgReceived)
			break
		# deal with IO errors and stop running the program if one occurs 
		except IOError as e:
				if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
					print("Reading Error", str(e))
					sys.exit()
				continue
		# deal with any other exceptions and stop running the program if one occurs 
		except Exception as e:
				print("General Error",str(e))
				sys.exit()
				pass

# function that sends a message 
# param: msgToSend - variable holding the message to be sent 
# param: dest - destination for the message to be sent to 
def sendMsg(msgToSend, dest = None):
	# if the message doesn't include a destination, then set it to the channel declared at the top of the code 
	if (dest == None):
		dest = "#" + channel
	# if the message is not blank, send it to the destination in the correct format (the hexchat format)
	if (msgToSend != ""):
		msgToSend = ("PRIVMSG " + dest + \
			" :" + msgToSend + "\r\n")
		print("Sending: " + msgToSend)
		# encode with utf-8 and send to the server
		msgToSend = msgToSend.encode("utf-8")
		client_socket.send(msgToSend)

# function that deals with the different replies the bot can send 
# param: recievedMsg - the message recieved from recvMsg()
def botReplies(receivedMsg):
	#initialise the finalParse variable which will hold the command sent to the bot by the client 
	finalParse = ''
	# split the received message appropriately so it can be dealt with 
	test = receivedMsg.split(" ")
	if (test[0][0] == ":"):

		test2 = receivedMsg.split(":",2)
		nick = test2[1].split("!",1)[0]

		if (test[1] == "PRIVMSG"):
			if (test[2] == nick):
				print("nickname")
			if (test[2] == "#" + channel):				
				finalParsing = test[3].split("\r\n", 1)[0]
				finalParse = finalParsing[1:]	

	# if the command sent by the client is '!day', respond with what day of the week it is 
	if (finalParse == "!day"):
		# get the date and time adn format it to only include the day of the week 
		todayDate = datetime.datetime.now()
		today = todayDate.strftime("%A")
		# set replyMsg to be the day of the week and send this 
		replyMsg = "Today is a " + today
		sendMsg(replyMsg)
		# continue to recieve messages after sending a response to the command 
		recvMsg()
	# if the command is a private message directed to the bot, respond with a fun fact 
	elif (test[1] == "PRIVMSG" and test[2] == "ProBot"):
		try:
			# open the plain text file containing all the fun facts as read only and encode it using utf-8
			myfile = open(r"fun-facts.txt","r", encoding="utf-8")
			# read in each line of the text file 
			lines = myfile.readlines()
			# generate a random number from 0 to 14 (15 possibilities)
			randomNum = randrange(14)
			# set replyMsg to a random line in the file which will be a random fact
			replyMsg = lines[randomNum]
			# respond via a private channel to the client who sent the command 
			# (hence why the nickname is passed into the sendMsg function)
			sendMsg(replyMsg, nick)
			# continue to recieve messages after sending a response to the command 
			recvMsg()
		# except any IO errors 
		except IOError:
			print("IO error")
		# except any other errors
		except Exception as e:
			print("ERROR") 

		# close the file as it is not being used anymore 
		myfile.close()  		
	# if the command sent by the client is '!time', respond with the current time 
	elif (finalParse == "!time"):
		# get the current date and time and format it to just the time 
		time = datetime.datetime.now()
		timeNow = time.strftime("%H:%M:%S")
		# set replyMsg to the current time and send this
		replyMsg = "The current time is " + timeNow
		sendMsg(replyMsg)
		# continue to receive messages after sending a response to the command 
		recvMsg()
	# if none of the above options are valid , continue to receive messages 
	else:
		recvMsg()

# main function calling initial methods 
def main():
	botInit()
	recvMsg()


if __name__ == '__main__':
	main()