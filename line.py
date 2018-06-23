# -*- coding: utf-8 -*-

from LineAPI.linepy import *
from LineAPI.akad.ttypes import Message
from LineAPI.akad.ttypes import ContentType as Type
from gtts import gTTS
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from googletrans import Translator
from humanfriendly import format_timespan, format_size, format_number, format_length
import time, random, sys, json, codecs, threading, glob, re, string, os, requests, six, ast, pytz, urllib, urllib3, urllib.parse, traceback, atexit

client = LINE()
#client = LINE("")
clientMid = client.profile.mid
clientProfile = client.getProfile()
clientSettings = client.getSettings()
clientPoll = OEPoll(client)
botStart = time.time()

msg_dict = {}

settings = {
    "autoAdd": False,
    "autoJoin": False,
    "autoLeave": False,
    "autoRead": False,
    "autoRespon": False,
    "autoJoinTicket": False,
    "checkContact": False,
    "checkPost": False,
    "checkSticker": False,
    "changePictureProfile": False,
    "changeGroupPicture": [],
    "keyCommand": "",
    "myProfile": {
        "displayName": "",
        "coverId": "",
        "pictureStatus": "",
        "statusMessage": ""
    },
    "mimic": {
        "copy": False,
        "status": False,
        "target": {}
    },
    "setKey": False,
    "unsendMessage": False
}

read = {
    "ROM": {},
    "readPoint": {},
    "readMember": {},
    "readTime": {}
}

list_language = {
    "list_textToSpeech": {
        "id": "Indonesia",
        "zh" : "Chinese",
        "en" : "English",
        "ja" : "Japanese",
        "ko" : "Korean",
        "th" : "Thai",
    }
}

try:
    with open("Log_data.json","r",encoding="utf_8_sig") as f:
        msg_dict = json.loads(f.read())
except:
    print("Couldn't read Log data")
    
settings["myProfile"]["displayName"] = clientProfile.displayName
settings["myProfile"]["statusMessage"] = clientProfile.statusMessage
settings["myProfile"]["pictureStatus"] = clientProfile.pictureStatus
coverId = client.getProfileDetail()["result"]["objectId"]
settings["myProfile"]["coverId"] = coverId

def restartBot():
    print ("[ INFO ] BOT RESTART")
    python = sys.executable
    os.execl(python, python, *sys.argv)
    
def logError(text):
    client.log("[ ERROR ] {}".format(str(text)))
    tz = pytz.timezone("Asia/Jakarta")
    timeNow = datetime.now(tz=tz)
    timeHours = datetime.strftime(timeNow,"(%H:%M)")
    day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
    hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    inihari = datetime.now(tz=tz)
    hr = inihari.strftime('%A')
    bln = inihari.strftime('%m')
    for i in range(len(day)):
        if hr == day[i]: hasil = hari[i]
    for k in range(0, len(bulan)):
        if bln == str(k): bln = bulan[k-1]
    time = "{}, {} - {} - {} | {}".format(str(hasil), str(inihari.strftime('%d')), str(bln), str(inihari.strftime('%Y')), str(inihari.strftime('%H:%M:%S')))
    with open("logError.txt","a") as error:
        error.write("\n[ {} ] {}".format(str(time), text))

def cTime_to_datetime(unixtime):
    return datetime.fromtimestamp(int(str(unixtime)[:len(str(unixtime))-3]))
def dt_to_str(dt):
    return dt.strftime('%H:%M:%S')

def delete_log():
    ndt = datetime.now()
    for data in msg_dict:
        if (datetime.utcnow() - cTime_to_datetime(msg_dict[data]["createdTime"])) > timedelta(1):
            if "path" in msg_dict[data]:
                client.deleteFile(msg_dict[data]["path"])
            del msg_dict[data]
            
def sendMention(to, text="", mids=[]):
    arrData = ""
    arr = []
    mention = "@zeroxyuuki "
    if mids == []:
        raise Exception("Invalid mids")
    if "@!" in text:
        if text.count("@!") != len(mids):
            raise Exception("Invalid mids")
        texts = text.split("@!")
        textx = ""
        for mid in mids:
            textx += str(texts[mids.index(mid)])
            slen = len(textx)
            elen = len(textx) + 15
            arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mid}
            arr.append(arrData)
            textx += mention
        textx += str(texts[len(mids)])
    else:
        textx = ""
        slen = len(textx)
        elen = len(textx) + 15
        arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mids[0]}
        arr.append(arrData)
        textx += mention + str(text)
    client.sendMessage(to, textx, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)

def command(text):
    pesan = text.lower()
    if settings["setKey"] == True:
        if pesan.startswith(settings["keyCommand"]):
            cmd = pesan.replace(settings["keyCommand"],"")
        else:
            cmd = "Undefined command"
    else:
        cmd = text.lower()
    return cmd
    
def helpmessage():
    if settings['setKey'] == True:
        key = settings['keyCommand']
    else:
        key = ''
    helpMessage =   "| • -= ᴅᴡɪᴡiʀᴀɴᴀᴛʜᴀ ᴘʀᴏᴊᴇᴄᴛ =-" + "\n" + \
                    "| • " + key + "ʜᴇʟᴘ" + "\n" + \
                    "| • " + key + "sᴀʏʜᴇʟᴘ" + "\n" + \
                    "| • " + key + "ᴄʀᴇᴀᴛᴏʀ" + "\n" + \
                    "| • " + key + "ʀᴇsᴛᴀʀᴛʙᴏᴛ" + "\n" + \
                    "| • " + key + "sᴘᴇᴇᴅʙᴏᴛ" + "\n" + \
                    "| • " + key + "ᴜɴɪᴄᴏᴅᴇ" + "\n" + \
                    "| • " + key + "ʙᴏᴏᴍᴍᴇssᴀɢᴇ" + "\n" + \
                    "| • " + key + "ᴍᴇ" + "\n" + \
                    "| • " + key + "ᴍʏᴍɪᴅ" + "\n" + \
                    "| • " + key + "ᴍʏɴᴀᴍᴇ" + "\n" + \
                    "| • " + key + "ᴍʏʙɪᴏ" + "\n" + \
                    "| • " + key + "ᴍʏᴘɪᴄᴛᴜʀᴇ" + "\n" + \
                    "| • " + key + "ᴍʏᴠɪᴅᴇᴏᴘʀᴏғɪʟᴇ" + "\n" + \
                    "| • " + key + "ᴍʏᴄᴏᴠᴇʀ" + "\n" + \
                    "| • " + key + "sᴛᴀʟᴋᴍɪᴅ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "sᴛᴀʟᴋɴᴀᴍᴇ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "sᴛᴀʟᴋʙɪᴏ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "sᴛᴀʟᴋᴘɪᴄᴛᴜʀᴇ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "sᴛᴀʟᴋᴠɪᴅᴇᴏᴘʀᴏғɪʟᴇ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "sᴛᴀʟᴋᴄᴏᴠᴇʀ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "ᴜɴsᴇɴᴅᴄʜᴀᴛ [ ᴏɴ/ᴏғғ ]" + "\n" + \
                    "| • " + key + "ᴋɪᴄᴋ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "ɢʀᴏᴜᴘᴍᴇᴍʙᴇʀʟɪsᴛ" + "\n" + \
                    "| • " + key + "ɢʀᴏᴜᴘɪɴғᴏ" + "\n" + \
                    "| • " + key + "ᴍᴀᴄʀᴏ [ ᴏɴ/ᴏғғ ]" + "\n" + \
                    "| • " + key + "ᴍᴀᴄʀᴏʟɪsᴛ" + "\n" + \
                    "| • " + key + "ᴍᴀᴄʀᴏᴀᴅᴅ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "ᴍᴀᴄʀᴏᴅᴇʟ [ ᴍᴇɴᴛɪᴏɴ ]" + "\n" + \
                    "| • " + key + "ᴛᴀɢᴍᴇᴍʙᴇʀ" + "\n" + \
                    "| • " + key + "sᴘʏʙᴏᴛ [ ᴏɴ/ᴏғғ/ʀᴇsᴇᴛ ]" + "\n" + \
                    "| • " + key + "sᴄᴀɴ" + "\n" + \
                    "| • # ᴍᴀᴋᴇ ɪᴛ sɪᴍᴘʟᴇ"
    return helpMessage

def helptexttospeech():
    if settings['setKey'] == True:
        key = settings['keyCommand']
    else:
        key = ''
    helpTextToSpeech =  "| • -= ʜᴇʟᴘ ᴛᴇxᴛ ᴛᴏ sᴘᴇᴇᴄʜ =-" + "\n" + \
                        "| • " + key + "ɪᴅ : ɪɴᴅᴏɴᴇsɪᴀ" + "\n" + \
                        "| • " + key + "ᴇɴ : ᴇɴɢʟɪsʜ" + "\n" + \
                        "| • " + key + "ᴊᴀ : ᴊᴀᴘᴀɴᴇsᴇ" + "\n" + \
                        "| • " + key + "ᴋᴏ : ᴋᴏʀᴇᴀɴ" + "\n" + \
                        "| • " + key + "ᴛʜ : ᴛʜᴀɪʟᴀɴᴅ" + "\n" + \
                        "| • " + key + "ᴢʜ : ᴄʜɪɴᴀ" + "\n" + \
                        "ᴇxᴀᴍᴘʟᴇ : " + key + "/sᴀʏ-ɪᴅ ᴅᴡɪᴡɪʀᴀɴᴀᴛʜᴀ"
    return helpTextToSpeech

def clientBot(op):
    try:
        if op.type == 0:
            print ("[ 0 ] END OF OPERATION")
            return

        if op.type == 5:
            print ("[ 5 ] NOTIFIED ADD CONTACT")
            if settings["autoAdd"] == True:
                client.findAndAddContactsByMid(op.param1)
            sendMention(op.param1, "Hello @!, Thanks for add me :3")

        if op.type == 13:
            print ("[ 13 ] NOTIFIED INVITE INTO GROUP")
            if clientMid in op.param3:
                if settings["autoJoin"] == True:
                    client.acceptGroupInvitation(op.param1)
                sendMention(op.param1, "Hello @!, Thank You for invite :3")

        if op.type in [22, 24]:
            print ("[ 22 And 24 ] NOTIFIED INVITE INTO ROOM & NOTIFIED LEAVE ROOM")
            if settings["autoLeave"] == True:
                sendMention(op.param1, "Hei @!,why invited me ?")
                client.leaveRoom(op.param1)

        if op.type == 25:
            try:
                print ("[ 25 ] SEND MESSAGE")
                msg = op.message
                text = msg.text
                msg_id = msg.id
                receiver = msg.to
                sender = msg._from
                setKey = settings["keyCommand"].title()
                if settings["setKey"] == False:
                    setKey = ''
                if msg.toType == 0 or msg.toType == 1 or msg.toType == 2:
                    if msg.toType == 0:
                        if sender != client.profile.mid:
                            to = sender
                        else:
                            to = receiver
                    elif msg.toType == 1:
                        to = receiver
                    elif msg.toType == 2:
                        to = receiver
                    if msg.contentType == 0:
                        if text is None:
                            return
                        else:
                            cmd = command(text)
                            if cmd == "help":
                                helpMessage = helpmessage()
                                client.sendMessage(to, str(helpMessage))
                            elif cmd == "sayhelp":
                                helpTextToSpeech = helptexttospeech()
                                client.sendMessage(to, str(helpTextToSpeech))
                            elif cmd.startswith("changekey:"):
                                sep = text.split(" ")
                                key = text.replace(sep[0] + " ","")
                                if " " in key:
                                    client.sendMessage(to, "Key can not use spaces")
                                else:
                                    settings["keyCommand"] = str(key).lower()
                                    client.sendMessage(to, "Successfully changed the key command to [ {} ]".format(str(key).lower()))
                            elif cmd == "speedbot":
                                start = time.time()
                                client.sendMessage(to, "ᴄᴏɴɴᴇᴄᴛɪɴɢ . . .")
                                elapsed_time = time.time() - start
                                client.sendMessage(to, "\sᴇɴᴅɪɴɢ ᴍᴇssᴀɢᴇs {}/s".format(str(elapsed_time)))
                            elif cmd == "restartbot":
                                client.sendMessage(to, "ᴅᴏɴᴇ . . .")
                                restartBot()
                            elif cmd == "creator":
                                try:
                                    ret_ = "| • -= ᴀʙᴏᴜᴛ ʙᴏᴛ =-"
                                    ret_ += "\n| • ᴀᴜᴛʜᴏʀ : ᴅᴡɪᴡɪʀᴀɴᴀᴛʜᴀ_"
                                    ret_ += "\n| • ᴄʟɪᴇɴᴛ sᴇʀᴠᴇʀ : x.x.x.x.x"
                                    ret_ += "\n| • ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ : http://line.me/ti/p/_59r6yG7J8"
                                    client.sendMessage(to, str(ret_))
                                except Exception as e:
                                    client.sendMessage(msg.to, str(e))
                            elif cmd == "unicode":
                                client.sendMessage(to, "7.I.8.J.9.K.0.A.1.B.2.D.3.")
# Pembatas Script #
                            elif cmd == "crash":
                                client.sendContact(to, "u1f41296217e740650e0448b96851a3e2',")
                            elif cmd == "me":
                                sendMention(to, "@!", [sender])
                                client.sendContact(to, sender)
                            elif cmd == "mymid":
                                client.sendMessage(to, "| • -= ᴍ ɪ ᴅ =-\n{}".format(sender))
                            elif cmd == "myname":
                                contact = client.getContact(sender)
                                client.sendMessage(to, "| • -= ᴅɪsᴘʟᴀʏ ɴᴀᴍᴇ =-\n{}".format(contact.displayName))
                            elif cmd == "mybio":
                                contact = client.getContact(sender)
                                client.sendMessage(to, "| • -= sᴛᴀᴛᴜs ᴍᴇssᴀɢᴇ =-\n{}".format(contact.statusMessage))
                            elif cmd == "mypicture":
                                contact = client.getContact(sender)
                                client.sendImageWithURL(to,"http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
                            elif cmd == "myvideoprofile":
                                contact = client.getContact(sender)
                                client.sendVideoWithURL(to,"http://dl.profile.line-cdn.net/{}/vp".format(contact.pictureStatus))
                            elif cmd == "mycover":
                                channel = client.getProfileCoverURL(sender)          
                                path = str(channel)
                                client.sendImageWithURL(to, path)
                            elif cmd == "unsendchat on":
                                settings["unsendMessage"] = True
                                client.sendMessage(to, "ᴜɴsᴇɴᴅ ᴍᴇssᴀɢᴇ ᴏɴ")
                            elif cmd == "unsendchat off":
                                settings["unsendMessage"] = False
                                client.sendMessage(to, "ᴜɴsᴇɴᴅ ᴍᴇssᴀɢᴇ ᴏғғ")
                            elif cmd.startswith("stalkmid "):
                                if 'MENTION' in msg.contentMetadata.keys()!= None:
                                    names = re.findall(r'@(\w+)', text)
                                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                    mentionees = mention['MENTIONEES']
                                    lists = []
                                    for mention in mentionees:
                                        if mention["M"] not in lists:
                                            lists.append(mention["M"])
                                    ret_ = "| • -= ᴍ ɪ ᴅ ᴜsᴇʀ =-"
                                    for ls in lists:
                                        ret_ += "\n{}".format(str(ls))
                                    client.sendMessage(to, str(ret_))
                            elif cmd.startswith("stalkname "):
                                if 'MENTION' in msg.contentMetadata.keys()!= None:
                                    names = re.findall(r'@(\w+)', text)
                                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                    mentionees = mention['MENTIONEES']
                                    lists = []
                                    for mention in mentionees:
                                        if mention["M"] not in lists:
                                            lists.append(mention["M"])
                                    for ls in lists:
                                        contact = client.getContact(ls)
                                        client.sendMessage(to, "| • -= ᴅɪsᴘʟᴀʏ ɴᴀᴍᴇ =-\n{}".format(str(contact.displayName)))
                            elif cmd.startswith("stalkbio "):
                                if 'MENTION' in msg.contentMetadata.keys()!= None:
                                    names = re.findall(r'@(\w+)', text)
                                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                    mentionees = mention['MENTIONEES']
                                    lists = []
                                    for mention in mentionees:
                                        if mention["M"] not in lists:
                                            lists.append(mention["M"])
                                    for ls in lists:
                                        contact = client.getContact(ls)
                                        client.sendMessage(to, "| • -= sᴛᴀᴛᴜs ᴍᴇssᴀɢᴇ =-\n{}".format(str(contact.statusMessage)))
                            elif cmd.startswith("stalkpicture"):
                                if 'MENTION' in msg.contentMetadata.keys()!= None:
                                    names = re.findall(r'@(\w+)', text)
                                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                    mentionees = mention['MENTIONEES']
                                    lists = []
                                    for mention in mentionees:
                                        if mention["M"] not in lists:
                                            lists.append(mention["M"])
                                    for ls in lists:
                                        contact = client.getContact(ls)
                                        path = "http://dl.profile.line.naver.jp/{}".format(contact.pictureStatus)
                                        client.sendImageWithURL(to, str(path))
                            elif cmd.startswith("stalkvideoprofile "):
                                if 'MENTION' in msg.contentMetadata.keys()!= None:
                                    names = re.findall(r'@(\w+)', text)
                                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                    mentionees = mention['MENTIONEES']
                                    lists = []
                                    for mention in mentionees:
                                        if mention["M"] not in lists:
                                            lists.append(mention["M"])
                                    for ls in lists:
                                        contact = client.getContact(ls)
                                        path = "http://dl.profile.line.naver.jp/{}/vp".format(contact.pictureStatus)
                                        client.sendVideoWithURL(to, str(path))
                            elif cmd.startswith("stalkcover "):
                                if client != None:
                                    if 'MENTION' in msg.contentMetadata.keys()!= None:
                                        names = re.findall(r'@(\w+)', text)
                                        mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                        mentionees = mention['MENTIONEES']
                                        lists = []
                                        for mention in mentionees:
                                            if mention["M"] not in lists:
                                                lists.append(mention["M"])
                                        for ls in lists:
                                            channel = client.getProfileCoverURL(ls)
                                            path = str(channel)
                                            client.sendImageWithURL(to, str(path))
# Pembatas Script #
                            elif cmd == 'groupinfo':
                                group = client.getGroup(to)
                                try:
                                    gCreator = group.creator.displayName
                                except:
                                    gCreator = "ɴoᴛ ғoᴜɴᴅ"
                                if group.invitee is None:
                                    gPending = "0"
                                else:
                                    gPending = str(len(group.invitee))
                                if group.preventedJoinByTicket == True:
                                    gQr = "ᴄʟᴏsᴇ"
                                    gTicket = "ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
                                else:
                                    gQr = "ᴏᴘᴇɴ"
                                    gTicket = "https://line.me/R/ti/g/{}".format(str(client.reissueGroupTicket(group.id)))
                                path = "http://dl.profile.line-cdn.net/" + group.pictureStatus
                                ret_ = "| • -= ɢʀᴏᴜᴘ ɪɴғᴏ =-"
                                ret_ += "\n| • ɢʀᴏᴜᴘ ɴᴀᴍᴇ : {}".format(str(group.name))
                                ret_ += "\n| • ɢʀᴏᴜᴘ ɪᴅ : {}".format(group.id)
                                ret_ += "\n| • ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ : {}".format(str(gCreator))
                                ret_ += "\n| • ᴍᴇᴍʙᴇʀ : {}".format(str(len(group.members)))
                                ret_ += "\n| • ᴘᴇɴᴅɪɴɢ : {}".format(gPending)
                                ret_ += "\n| • ɢʀᴏᴜᴘ ᴛɪᴄᴋᴇᴛ : {}".format(gTicket)
                                client.sendMessage(to, str(ret_))
                                client.sendImageWithURL(to, path)
                            elif cmd == 'groupmemberlist':
                                if msg.toType == 2:
                                    group = client.getGroup(to)
                                    ret_ = "| • -= ᴍᴇᴍʙᴇʀ ʟɪsᴛ =-"
                                    no = 0 + 1
                                    for mem in group.members:
                                        ret_ += "\n| • {}. {}".format(str(no), str(mem.displayName))
                                        no += 1
                                    ret_ += "\n| • ᴛᴏᴛᴀʟ {} ᴍᴇᴍʙᴇʀ".format(str(len(group.members)))
                                    client.sendMessage(to, str(ret_))
# Pembatas Script #
                            elif cmd == 'tagmember':
                                group = client.getGroup(msg.to)
                                nama = [contact.mid for contact in group.members]
                                k = len(nama)//100
                                for a in range(k+1):
                                    txt = u''
                                    s=0
                                    b=[]
                                    for i in group.members[a*100 : (a+1)*100]:
                                        b.append({"S":str(s), "E" :str(s+6), "M":i.mid})
                                        s += 7
                                        txt += u'@Zero \n'
                                    client.sendMessage(to, text=txt, contentMetadata={u'MENTION': json.dumps({'MENTIONEES':b})}, contentType=0)
                                    client.sendMessage(to, "ᴛᴏᴛᴀʟ {} ᴍᴇɴᴛɪᴏɴ".format(str(len(nama))))  
                            elif cmd == "spybot on":
                                tz = pytz.timezone("Asia/Makassar")
                                timeNow = datetime.now(tz=tz)
                                day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
                                hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                                bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                                hr = timeNow.strftime("%A")
                                bln = timeNow.strftime("%m")
                                for i in range(len(day)):
                                    if hr == day[i]: hasil = hari[i]
                                for k in range(0, len(bulan)):
                                    if bln == str(k): bln = bulan[k-1]
                                readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nᴛɪᴍᴇ : - " + timeNow.strftime('%H:%M:%S') + " -"
                                if receiver in read['readPoint']:
                                    try:
                                        del read['readPoint'][receiver]
                                        del read['readMember'][receiver]
                                        del read['readTime'][receiver]
                                    except:
                                        pass
                                    read['readPoint'][receiver] = msg_id
                                    read['readMember'][receiver] = ""
                                    read['readTime'][receiver] = readTime
                                    read['ROM'][receiver] = {}
                                    client.sendMessage(receiver,"sᴘʏ-ʙᴏᴛ ᴏɴ")
                                else:
                                    try:
                                        del read['readPoint'][receiver]
                                        del read['readMember'][receiver]
                                        del read['readTime'][receiver]
                                    except:
                                        pass
                                    read['readPoint'][receiver] = msg_id
                                    read['readMember'][receiver] = ""
                                    read['readTime'][receiver] = readTime
                                    read['ROM'][receiver] = {}
                                    client.sendMessage(receiver,"sᴇᴛ ʀᴇᴀᴅɪɴɢ ᴘᴏɪɴᴛ : \n" + readTime)
                            elif cmd == "spybot off":
                                tz = pytz.timezone("Asia/Makassar")
                                timeNow = datetime.now(tz=tz)
                                day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
                                hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                                bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                                hr = timeNow.strftime("%A")
                                bln = timeNow.strftime("%m")
                                for i in range(len(day)):
                                    if hr == day[i]: hasil = hari[i]
                                for k in range(0, len(bulan)):
                                    if bln == str(k): bln = bulan[k-1]
                                readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nᴛɪᴍᴇ : - " + timeNow.strftime('%H:%M:%S') + " -"
                                if receiver not in read['readPoint']:
                                    client.sendMessage(receiver,"sᴘʏ-ʙᴏᴛ ᴏғғ")
                                else:
                                    try:
                                        del read['readPoint'][receiver]
                                        del read['readMember'][receiver]
                                        del read['readTime'][receiver]
                                    except:
                                        pass
                                    client.sendMessage(receiver,"ᴅᴇʟᴇᴛᴇ ʀᴇᴀᴅɪɴɢ ᴘᴏɪɴᴛ : \n" + readTime)
        
                            elif cmd == "spybot reset":
                                tz = pytz.timezone("Asia/Makassar")
                                timeNow = datetime.now(tz=tz)
                                day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
                                hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                                bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                                hr = timeNow.strftime("%A")
                                bln = timeNow.strftime("%m")
                                for i in range(len(day)):
                                    if hr == day[i]: hasil = hari[i]
                                for k in range(0, len(bulan)):
                                    if bln == str(k): bln = bulan[k-1]
                                readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nᴛɪᴍᴇ : : - " + timeNow.strftime('%H:%M:%S') + " -"
                                if msg.to in read["readPoint"]:
                                    try:
                                        del read["readPoint"][msg.to]
                                        del read["readMember"][msg.to]
                                        del read["readTime"][msg.to]
                                        del read["ROM"][msg.to]
                                    except:
                                        pass
                                    read['readPoint'][receiver] = msg_id
                                    read['readMember'][receiver] = ""
                                    read['readTime'][receiver] = readTime
                                    read['ROM'][receiver] = {}
                                    client.sendMessage(msg.to, "ʀᴇsᴇᴛ ʀᴇᴀᴅɪɴɢ ᴘᴏɪɴᴛ : \n" + readTime)
                                else:
                                    client.sendMessage(msg.to, "sᴘʏ-ʙᴏᴛ ᴄᴀɴ'ᴛ ʀᴇsᴇᴛ, ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ sᴘʏ-ʙᴏᴛ")
                                    
                            elif cmd == "scan":
                                tz = pytz.timezone("Asia/Makassar")
                                timeNow = datetime.now(tz=tz)
                                day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
                                hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                                bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                                hr = timeNow.strftime("%A")
                                bln = timeNow.strftime("%m")
                                for i in range(len(day)):
                                    if hr == day[i]: hasil = hari[i]
                                for k in range(0, len(bulan)):
                                    if bln == str(k): bln = bulan[k-1]
                                readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nᴛɪᴍᴇ : - " + timeNow.strftime('%H:%M:%S') + " -"
                                if receiver in read['readPoint']:
                                    if read["ROM"][receiver].items() == []:
                                        client.sendMessage(receiver,"sɪʟᴇɴᴛ ʀᴇᴀᴅᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ")
                                    else:
                                        chiya = []
                                        for rom in read["ROM"][receiver].items():
                                            chiya.append(rom[1])
                                        cmem = client.getContacts(chiya) 
                                        zx = ""
                                        zxc = ""
                                        zx2 = []
                                        xpesan = '| • -= ʀ ᴇ ᴀ ᴅ ᴇ ʀ =-\n'
                                    for x in range(len(cmem)):
                                        xname = str(cmem[x].displayName)
                                        pesan = ''
                                        pesan2 = pesan+"@c\n"
                                        xlen = str(len(zxc)+len(xpesan))
                                        xlen2 = str(len(zxc)+len(pesan2)+len(xpesan)-1)
                                        zx = {'S':xlen, 'E':xlen2, 'M':cmem[x].mid}
                                        zx2.append(zx)
                                        zxc += pesan2
                                    text = xpesan+ zxc + "\n" + readTime
                                    try:
                                        client.sendMessage(receiver, text, contentMetadata={'MENTION':str('{"MENTIONEES":'+json.dumps(zx2).replace(' ','')+'}')}, contentType=0)
                                    except Exception as error:
                                        print (error)
                                    pass
                                else:
                                    client.sendMessage(receiver,"sᴘʏ-ʙᴏᴛ ᴏɴ")
                            elif cmd.startswith("macroadd"):
                                targets = []
                                key = eval(msg.contentMetadata["MENTION"])
                                key["MENTIONEES"][0]["M"]
                                for x in key["MENTIONEES"]:
                                    targets.append(x["M"])
                                for target in targets:
                                    try:
                                        settings["mimic"]["target"][target] = True
                                        client.sendMessage(msg.to,"ᴛᴀʀɢᴇᴛ ᴀᴅᴅᴇᴅ!")
                                        break
                                    except:
                                        client.sendMessage(msg.to,"ᴇʀʀᴏʀ!")
                                        break
                            elif cmd.startswith("macrodel"):
                                targets = []
                                key = eval(msg.contentMetadata["MENTION"])
                                key["MENTIONEES"][0]["M"]
                                for x in key["MENTIONEES"]:
                                    targets.append(x["M"])
                                for target in targets:
                                    try:
                                        del settings["mimic"]["target"][target]
                                        client.sendMessage(msg.to,"ᴛᴀʀɢᴇᴛ ᴅᴇʟᴇᴛᴇᴅ!")
                                        break
                                    except:
                                        client.sendMessage(msg.to,"ᴇʀʀᴏʀ!")
                                        break
                                    
                            elif cmd == "macrolist":
                                if settings["mimic"]["target"] == {}:
                                    client.sendMessage(msg.to,"ɴᴏ ᴛᴀʀɢᴇᴛ")
                                else:
                                    mc = "| • -= ᴍᴀᴄʀᴏ ʟɪsᴛ =-"
                                    for mi_d in settings["mimic"]["target"]:
                                        mc += "\n| • "+client.getContact(mi_d).displayName
                                    client.sendMessage(msg.to,mc)
                                
                            elif cmd.startswith("macro"):
                                sep = text.split(" ")
                                mic = text.replace(sep[0] + " ","")
                                if mic == "on":
                                    if settings["mimic"]["status"] == False:
                                        settings["mimic"]["status"] = True
                                        client.sendMessage(msg.to,"ᴍᴀᴄʀᴏ ᴍᴇssᴀɢᴇ ᴏɴ")
                                elif mic == "off":
                                    if settings["mimic"]["status"] == True:
                                        settings["mimic"]["status"] = False
                                        client.sendMessage(msg.to,"ᴍᴀᴄʀᴏ ᴍᴇssᴀɢᴇ ᴏғғ")
# Pembatas Script #           
                            elif cmd.startswith("/say-"):
                                sep = text.split("-")
                                sep = sep[1].split(" ")
                                lang = sep[0]
                                say = text.replace("/say-" + lang + " ","")
                                if lang not in list_language["list_textToSpeech"]:
                                    return client.sendMessage(to, "ʟᴀɴɢᴜᴀɢᴇ ɴoᴛ ғoᴜɴᴅ")
                                tts = gTTS(text=say, lang=lang)
                                tts.save("texttospeech.mp3")
                                client.sendAudio(to,"texttospeech.mp3")
# Pembatas Script #
                    elif msg.contentType == 16:
                        if settings["checkPost"] == True:
                            try:
                                ret_ = "Details Post"
                                if msg.contentMetadata["serviceType"] == "GB":
                                    contact = client.getContact(sender)
                                    auth = "\nAuthor : {}".format(str(contact.displayName))
                                else:
                                    auth = "\nAuthor : {}".format(str(msg.contentMetadata["serviceName"]))
                                purl = "\nURL : {}".format(str(msg.contentMetadata["postEndUrl"]).replace("line://","https://line.me/R/"))
                                ret_ += auth
                                ret_ += purl
                                if "mediaOid" in msg.contentMetadata:
                                    object_ = msg.contentMetadata["mediaOid"].replace("svc=myhome|sid=h|","")
                                    if msg.contentMetadata["mediaType"] == "V":
                                        if msg.contentMetadata["serviceType"] == "GB":
                                            ourl = "\nObject URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(msg.contentMetadata["mediaOid"]))
                                            murl = "\nMedia URL : https://obs-us.line-apps.com/myhome/h/download.nhn?{}".format(str(msg.contentMetadata["mediaOid"]))
                                        else:
                                            ourl = "\nObject URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(object_))
                                            murl = "\nMedia URL : https://obs-us.line-apps.com/myhome/h/download.nhn?{}".format(str(object_))
                                        ret_ += murl
                                    else:
                                        if msg.contentMetadata["serviceType"] == "GB":
                                            ourl = "\nObject URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(msg.contentMetadata["mediaOid"]))
                                        else:
                                            ourl = "\nObject URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(object_))
                                    ret_ += ourl
                                if "stickerId" in msg.contentMetadata:
                                    stck = "\nSticker : https://line.me/R/shop/detail/{}".format(str(msg.contentMetadata["packageId"]))
                                    ret_ += stck
                                if "text" in msg.contentMetadata:
                                    text = "\nFont : {}".format(str(msg.contentMetadata["text"]))
                                    ret_ += text
                                ret_ += "\nFinish"
                                client.sendMessage(to, str(ret_))
                            except:
                                client.sendMessage(to, "Post invalid")
            except Exception as error:
                logError(error)
                traceback.print_tb(error.__traceback__)
                
        if op.type == 26:
            try:
                print ("[ 26 ] RECIEVE MESSAGE")
                msg = op.message
                text = msg.text
                msg_id = msg.id
                receiver = msg.to
                sender = msg._from
                if msg.toType == 0 or msg.toType == 1 or msg.toType == 2:
                    if msg.toType == 0:
                        if sender != client.profile.mid:
                            to = sender
                        else:
                            to = receiver
                    elif msg.toType == 1:
                        to = receiver
                    elif msg.toType == 2:
                        to = receiver
                    if settings["autoRead"] == True:
                        client.sendChatChecked(to, msg_id)
                    if to in read["readPoint"]:
                        if sender not in read["ROM"][to]:
                            read["ROM"][to][sender] = True
                    if sender in settings["mimic"]["target"] and settings["mimic"]["status"] == True and settings["mimic"]["target"][sender] == True:
                        text = msg.text
                        if text is not None:
                            client.sendMessage(msg.to,text)
                    if settings["unsendMessage"] == True:
                        try:
                            msg = op.message
                            if msg.toType == 0:
                                client.log("[{} : {}]".format(str(msg._from), str(msg.text)))
                            else:
                                client.log("[{} : {}]".format(str(msg.to), str(msg.text)))
                                msg_dict[msg.id] = {"text": msg.text, "from": msg._from, "createdTime": msg.createdTime, "contentType": msg.contentType, "contentMetadata": msg.contentMetadata}
                        except Exception as error:
                            logError(error)
                    if msg.contentType == 0:
                        if text is None:
                            return
                        if "/ti/g/" in msg.text.lower():
                            if settings["autoJoinTicket"] == True:
                                link_re = re.compile('(?:line\:\/|line\.me\/R)\/ti\/g\/([a-zA-Z0-9_-]+)?')
                                links = link_re.findall(text)
                                n_links = []
                                for l in links:
                                    if l not in n_links:
                                        n_links.append(l)
                                for ticket_id in n_links:
                                    group = client.findGroupByTicket(ticket_id)
                                    client.acceptGroupInvitationByTicket(group.id,ticket_id)
                                    client.sendMessage(to, "sᴜᴄᴄᴇᴇs! %s" % str(group.name))
                        if 'MENTION' in msg.contentMetadata.keys()!= None:
                            names = re.findall(r'@(\w+)', text)
                            mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                            mentionees = mention['MENTIONEES']
                            lists = []
                            for mention in mentionees:
                                if clientMid in mention["M"]:
                                    if settings["autoRespon"] == True:
                                        sendMention(sender, "Hei @!,Don't Tag Me!", [sender])
                                    break
            except Exception as error:
                logError(error)
                traceback.print_tb(error.__traceback__)
        if op.type == 65:
            print ("[ 65 ] NOTIFIED DESTROY MESSAGE")
            if settings["unsendMessage"] == True:
                try:
                    at = op.param1
                    msg_id = op.param2
                    if msg_id in msg_dict:
                        if msg_dict[msg_id]["from"]:
                            contact = client.getContact(msg_dict[msg_id]["from"])
                            if contact.displayNameOverridden != None:
                                name_ = contact.displayNameOverridden
                            else:
                                name_ = contact.displayName
                                ret_ = "sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴄᴀɴᴄᴇʟʟᴇᴅ."
                                ret_ += "\nsᴇɴᴅᴇʀ : @!"
                                ret_ += "\nsᴇɴᴅ ᴀᴛ : {}".format(str(dt_to_str(cTime_to_datetime(msg_dict[msg_id]["createdTime"]))))
                                ret_ += "\nᴛʏᴘᴇ : {}".format(str(Type._VALUES_TO_NAMES[msg_dict[msg_id]["contentType"]]))
                                ret_ += "\nᴛᴇxᴛ : {}".format(str(msg_dict[msg_id]["text"]))
                                sendMention(at, str(ret_), [contact.mid])
                            del msg_dict[msg_id]
                        else:
                            client.sendMessage(at,"sᴇɴᴛᴍᴇssᴀɢᴇ ᴄᴀɴᴄᴇʟʟᴇᴅ, ʙᴜᴛ ɪ ᴅɪᴅɴ'ᴛ ʜᴀᴠᴇ ʟᴏɢ ᴅᴀᴛᴀ.\nsᴏʀʀʏ > <")
                except Exception as error:
                    logError(error)
                    traceback.print_tb(error.__traceback__)
                
        if op.type == 55:
            print ("[ 55 ] NOTIFIED READ MESSAGE")
            try:
                if op.param1 in read['readPoint']:
                    if op.param2 in read['readMember'][op.param1]:
                        pass
                    else:
                        read['readMember'][op.param1] += op.param2
                    read['ROM'][op.param1][op.param2] = op.param2
                else:
                   pass
            except Exception as error:
                logError(error)
                traceback.print_tb(error.__traceback__)
    except Exception as error:
        logError(error)
        traceback.print_tb(error.__traceback__)

while True:
    try:
        delete_log()
        ops = clientPoll.singleTrace(count=50)
        if ops is not None:
            for op in ops:
                clientBot(op)
                clientPoll.setRevision(op.revision)
    except Exception as error:
        logError(error)
        
def atend():
    print("Saving")
    with open("Log_data.json","w",encoding='utf8') as f:
        json.dump(msg_dict, f, ensure_ascii=False, indent=4,separators=(',', ': '))
    print("BYE")
atexit.register(atend)
