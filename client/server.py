import socket
import threading
import os
import shlex

count=0
list_peers=list()
list_idx=list()
list_rfc=list()
SERVER_PORT = 7734
    
    
class RFCRecord:
    def __init__(self, rfc_no = -1, rfc_title = 'None', peer_hostname ='None', peer_id =-1):
        self.rfc_no = rfc_no
        self.rfc_title = rfc_title
        self.peer_hostname = peer_hostname
        self.peer_id=peer_id

    def __str__(self):
        return str(self.rfc_no)+' '+str(self.rfc_title)+' '+str(self.peer_hostname)+' '+str(self.peer_id)



class PeerRecord:
    def __init__(self,peer_hostname='None',peer_postno=10000,peer_id=-1):
        self.peer_hostname=peer_hostname
        self.peer_postno=peer_postno
        self.peer_id=peer_id

    def __str__(self):
        return str(self.peer_hostname)+' '+str(self.peer_postno)+' '+str(self.peer_id)


def port_acquire(peer_id):
    for peer_record in list_peers:
        if peer_record.peer_id == peer_id:
            return peer_record.peer_postno 

def REGISTER(data, clientsocket):
    global count
    count = count+1
    rlist=shlex.split(data) 
    temp=list()
    a=list()
    b=list()
    rfc_list=str(data).rsplit(':',1)
    c=shlex.split(rfc_list[1])
    list_peers.insert(0,PeerRecord(rlist[3],rlist[5],count))
    for i,j in zip(c[::2],c[1::2]):
        list_idx.insert(0,RFCRecord(i,j,rlist[3],count))
    reply="CLIENT REGISTRATION SUCCESSFUL"
    clientsocket.send(reply)

def LIST_ALL(clientsocket):
    global status
    status=0
    global phrase
    phrase=''

    reply=list()
    if list_idx:
        for x in list_idx:
            peer_port = port_acquire(x.peer_id)
            reply.append(RFCRecord(x.rfc_no,x.rfc_title,x.peer_hostname,peer_port))
            status=200
            phrase='OK'        
    else:
        status=400
        phrase='BAD REQUEST'
    response="P2P-CI/1.0 "+str(status)+" "+str(phrase)+" - LIST_ALL"+"\n"
    for i in reply:
        reply_list=shlex.split(str(i))
        response=response+"File name: "+str(reply_list[1])+"_"+reply_list[0]+" HOST: "+reply_list[2]+" PORT: "+str(reply_list[3])+"\n"    
    clientsocket.send(response)

def LOOKUP(clientsocket, rlist):
    reply=list()
    flag=0
    for x in list_idx:
        if int(x.rfc_no)==int(rlist[1]):
            reply.append(RFCRecord(x.rfc_no,x.rfc_title,x.peer_hostname,x.peer_id))
            code=200
            phrase='OK'
            flag = 1
    
    if(flag==0):
        code=404
        phrase='FILE NOT FOUND'  
    response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+" - LOOKUP"+"\n"
    for i in reply:
        reply_list=shlex.split(str(i))
        response=response+"File found: "+str(reply_list[1])+"_"+reply_list[0]+" HOST: "+reply_list[2]+" CLIENT NUM: "+str(reply_list[3])+"\n"
    clientsocket.send(response)

def ADD(clientsocket, rlist, count, data):
    list_idx.insert(0,RFCRecord(rlist[1],rlist[8],rlist[4],count))
    code=200
    phrase='OK'
    a=data.splitlines()
    title=a[3].split(":")
    response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+" - ADD"+"\n"
    response=response+"File added: RFC_"+rlist[1]+" HOST: "+rlist[4]+" PORT: "+rlist[6]
    clientsocket.send(response)

def REMOVE(rlist, count):
    rfc_pos = 0
    phostname=rlist[4]
    peerport=rlist[6]
    rfc_title=rlist[8]
    for q in list_idx:
     if q.rfc_no==rlist[1] and q.peer_hostname==phostname and q.peer_id == count:
      del list_idx[rfc_pos]
    rfc_pos = rfc_pos + 1
    clientsocket.send("REMOVAL SUCCESS")
    
def EXIT(rlist, count):
    global peerhost
    templ=list()
    temil=list()
    phostname=rlist[3]
    peerport=rlist[5]
    for q in list_peers:
     if q.peer_postno==peerport:
      peerhost=q.peer_hostname
    idx2=[x for x,y in enumerate(list_idx) if y.peer_hostname==str(peerhost)]
    for i in sorted(idx2, reverse=True):
        del list_idx[i]
      
    idx=[x for x,y in enumerate(list_peers) if y.peer_postno==peerport]
    for i in idx:
        del list_peers[i]
    clientsocket.send("CLIENT CLOSED - SHUTDOWN SUCCESSFUL")


def req_processing(clientsocket, clientaddr):
    data = clientsocket.recv(1024)
    global count
    print "*"*37
    print "REQUEST FROM CLIENT: "
    print data
    print "*"*37
    rlist=shlex.split(data)
    if rlist[0] == 'REGISTER':
        REGISTER(data, clientsocket)

    elif rlist[0] == 'LISTALL':
        LIST_ALL(clientsocket)
    
    elif rlist[0] == 'LOOKUP':
        LOOKUP(clientsocket, rlist)
        
    elif rlist[0] == 'ADD':
        ADD(clientsocket, rlist, count, data)
        
    elif rlist[0] == 'EXIT':
        EXIT(rlist, count)
        
    elif rlist[0] == 'REMOVE':
        REMOVE(rlist, count)
    
if __name__=="__main__":
  
    HOST=socket.gethostname()
    PORT=SERVER_PORT
    IP = socket.gethostbyname(HOST)
    print "SERVER NAME - HOST NAME: "+HOST+" PORT:"+str(PORT)+" IP:"+IP
    serversocket = socket.socket()
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((HOST,PORT))
    serversocket.listen(5)
    print "SERVER ACTIVELY LISTENING FOR CONNECTIONS \n"
    while(1):  
        clientsocket, clientaddr = serversocket.accept()
        serverThread = threading.Thread(target=req_processing, args=(clientsocket,clientaddr))
        serverThread.start()
    serversocket.close()

    
