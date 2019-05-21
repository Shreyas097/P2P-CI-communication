import socket
import threading
import os
import shlex
import sys
import platform


rfc_name=[]
file_names_array=[]
SERVER_PORT = 7734
EXIT_FLAG = False
OS = platform.system()


####################### Various functions defined #######################	
#**************DISPLAYING STATUS CODE INFORMATION FUNCTION**************#
def STATUS_CODES():
    print "*"*50
    print "New Operation"
    print "*"*50
    print "Following are the status codes expected for operations"
    print "200 - OK"
    print "400 - BAD REQUEST"
    print "404 - FILE NOT FOUND"
    print "505 - P2P-CI/1.0 VERSION NOT SUPPORTED"	
	

#**************PRINTING MENU FUNCTION**************#	
def PRINT_MENU():
    print "\n"
    print "Select from the List - Enter the corresponding number or name in smallcase (Eg: For Add, Enter '3' or 'add')"
    print "1. List - To list all available files"
    print "2. Lookup - To find a file in the directory"
    print "3. Add - To add info about a newly created local file to the server"
    print "4. Get - To get a file available at another peer"
    print "5. Remove - To remove a file from the directory"
    print "6. Exit - To close connection with the server"
	

#**************USER INPUT FUNCTION**************#	
def USER_INPUT():
    print "Enter Host name of the Centralised Server:"
    server_name=raw_input()
    serverPort = SERVER_PORT
    message = "REGISTER P2P-CI/1.0 Host: "+HOST+" Port: "+str(PORT)+"\n"
    SERVER_RESPONSE(message,server_name,serverPort)
    temp_rfc_number = list()
    temp_rfc_name = list()
    temp_rfc_number, temp_rfc_name=CREATE_LIST()
    print "Informing the server about the locally available files "+str(temp_rfc_number)
    for i in range(len(temp_rfc_number)):
        message = "ADD"+" "+str(temp_rfc_number[i])+" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+temp_rfc_name[i]
        SERVER_RESPONSE(message,server_name,serverPort)
    
    while(1):
	
        STATUS_CODES()
		
        PRINT_MENU()

        choice = raw_input()

        if choice == "1" or choice == "list":
            LIST_ALL(server_name, serverPort)
            
        elif choice == "2" or choice == "lookup":
            LOOKUP(server_name, serverPort)

        elif choice == "3" or choice == "add":
            ADD(server_name, serverPort)
                
        elif choice == "4" or choice == "get":
            GET(server_name, serverPort)

        elif choice == "5" or choice == "remove":
            REMOVE(server_name, serverPort)			

        elif choice == "6" or choice == "exit":
            EXIT(server_name, serverPort)

    return  
	

#**************CREATING LIST FUNCTION**************#	
def CREATE_LIST():
    global file_names_array
    path_name = os.getcwd()
    file_list = os.listdir(path_name)
    temp_rfc_number = list()
    temp_rfc_name = list()
    for i in file_list:
        files = i.split(".")
        if files[1] == "txt":
            doc_name = str(files[0])
            file_names_array.append(doc_name)
            files1 = doc_name.split("_")
            temp_rfc_name.append(files1[0])
            temp_rfc_number.append(int(files1[1]))
    return temp_rfc_number,temp_rfc_name	
	

#**************LIST_ALL FUNCTION**************#	
def LIST_ALL(server_name, serverPort):
    message="LISTALL P2P-CI/1.0"+"\n"+"Host: "+HOST+"\n"+" Port: "+str(PORT)
    SERVER_RESPONSE(message,server_name,serverPort)
	

#**************LOOKUP FUNCTION**************#
def LOOKUP(server_name, serverPort):
    print "Enter RFC number to be looked up for:"
    rfc_number = int(raw_input())
    print "Enter RFC name to be looked up for:"
    rfc_name=raw_input()
    message="LOOKUP"+" "+str(rfc_number)+" P2P-CI/1.0"+"\n"+"Host: "+HOST+"\n"+"Port: "+str(PORT)+"\n"+"Title:"+rfc_name
    SERVER_RESPONSE(message,server_name,serverPort)
	
	
#**************ADD FUNCTION**************#	
def ADD(server_name, serverPort):
    print "Enter RFC number to be added:"
    rfc_number=raw_input()
    print "Enter RFC name to be added:"
    rfc_name=raw_input()
    path_name = os.getcwd()
    file_list = os.listdir(path_name)
    for i in file_list:
        files = i.split(".")
        if files[1] == "txt":
            str_files = str(files[0])
            files1 = str_files.split("_")
            doc_name = str_files
            if files1[1] == rfc_number:
                file_names_array.append(doc_name)
    message="ADD "+rfc_number+" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+rfc_name
    SERVER_RESPONSE(message,server_name,serverPort)
	
	
#**************GET FUNCTION**************#
#Get function to send request and receive file from other clients		
def GET(server_name, serverPort):
    print "Enter RFC number to get: "
    rfc_number = int(raw_input())
    print "Enter RFC name to get:"
    rfc_name = raw_input()
    print "Enter peer hostname which contains the file: "
    peer_name = raw_input()
    print "Enter Peer port number which contains the file: "
    peer_port = int(raw_input()) 
    message = "GET RFC " +str(rfc_number)+ " " +"P2P-CI/1.0\n"+"Host: "+peer_name+"\n"+"OS: "+str(OS)
    file_name = rfc_name+"_"+str(rfc_number)
    send_socket=socket.socket()
    peer_ip=socket.gethostbyname(peer_name)
    send_socket.connect((peer_ip,peer_port))
    print "\n"+peer_name+" with IP "+peer_ip+" client connected at port "+str(peer_port)+"\n"
    send_socket.send(message)
	
    response=send_socket.recv(1024)
    reply=shlex.split(response)
    path_name=os.getcwd()
    os.chdir(path_name)
    file_name=file_name+".txt"
    if str(reply[1])=='200':
        file1=open(file_name,'wb')
        while True:
            q=send_socket.recv(1024)
            if q:
                file1.write(q)
                break
            else:
                file1.close()
                print "File "+file_name+" received successfully from peer "+peer_name+" with IP "+peer_ip+" from port "+str(peer_port)
                break
        send_socket.close()
        status = True
    else:
        print "File Not Found"
        send_socket.close()
        status = False

    if status == True:
        file_add = file_name.split(".")
        file_names_array.insert(0,str(file_add[0]))
        print file_names_array
        message="ADD"+" "+ str(rfc_number) +" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+rfc_name
        SERVER_RESPONSE(message,server_name,serverPort)


#Get functions for receiving request from other clients to share available file info	
def CLIENT_LISTEN():

    listen_socket = socket.socket()
    listen_host = socket.gethostname()
    listen_port = PORT
    listen_socket.bind((listen_host,listen_port))
    listen_socket.listen(5)

    listen_thread = threading.current_thread()
    while(EXIT_FLAG == False):

        (peer_socket,peer_addr)=listen_socket.accept()
        print "Connected to", peer_addr
        thread_listen=threading.Thread(target=RFC_GET_RECEIVE_REQUEST,args=("listenThread",peer_socket))
        thread_listen.start()
        thread_listen.join()
    listen_socket.close()
    return	
	
def RFC_GET_RECEIVE_REQUEST(name, sock):
    message_in=sock.recv(1024)
    print message_in
    request=shlex.split(message_in)
    rfc_number = int(request[2])
    file_found = 0
    print "Files available: "
    print file_names_array
    for i in file_names_array:
        t = i.split("_")
        if int(t[1])==rfc_number:
            print "Requested file found at client"
            file_found=1
            file_name=str(i)+".txt"

    if file_found==1:
        file_response="P2P-CI/1.0 200 OK"+"\n"
        sock.send(file_response)
        with open(file_name,'r') as f:
            bytesToSend = f.read(1024)
            sock.send(bytesToSend)
            while bytesToSend != "":
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
    else:
        print "404 File not found"
        file_response="P2P-CI/1.0 404 FILE NOT FOUND"+"\n"
        sock.send(file_response)
        
    sock.close()


#**************REMOVE FUNCTION**************#	
def REMOVE(server_name, serverPort):
    print "Enter RFC number to be removed:"
    rfc_number = int(raw_input())
    print "Enter RFC name to be removed:"
    rfc_name = raw_input()
    str_file_name = rfc_name+"_"+str(rfc_number)+".txt"
    os.remove(str_file_name)
    message = "REMOVE"+" "+str(rfc_number)+" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+rfc_name
    SERVER_RESPONSE(message, server_name, serverPort)


#**************EXIT FUNCTION**************#	
def EXIT(server_name, serverPort):
    message = "EXIT P2P-CI/1.0 Host: "+HOST+" Port: "+str(PORT)
    SERVER_RESPONSE(message, server_name, serverPort)
    global EXIT_FLAG
    EXIT_FLAG = True



#**************SERVER RESPONSE FUNCTION**************#   
def SERVER_RESPONSE(message, server_name, serverPort):
    sock = socket.socket()
    sock.connect((server_name,serverPort))
    sock.send(message)
    reply = sock.recv(16384)
    print "\n"
    print "-"*40
    print "Response received from Server:"
    print reply
    print "-"*40
    print "\n"
    sock.close()



####################### Main #######################
if __name__== "__main__":

    global HOST
    global PORT
    global IP

    HOST = ''
    PORT = 0
    IP = ''
    HOST = socket.gethostname()
    IP = socket.gethostbyname(HOST)
    print "Enter your upload port number:"
    PORT = int(raw_input())
    print "Client Name is - Host Name: "+HOST+" Port:"+str(PORT)+" IP:"+IP
    try:
        thread_begin = threading.Thread(target=CLIENT_LISTEN)
        thread_begin.daemon = True
        thread_begin.start()
		
        USER_INPUT()
        
        while(EXIT_FLAG == False):
            pass  
        sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(0)
