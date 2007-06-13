"""
Helper library to ease emailing.
"""



import smtplib
import email
from email import Encoders
from email.Utils import formatdate
from email.Message import Message
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
import mimetypes

FROMEMAIL = 'ryan@acceleration.net'
SERVER = 'mail.acceleration.net'

def rawEmail(toList, msg, server=SERVER, fromEmail=FROMEMAIL):

    s = smtplib.SMTP(server)
    smtpresult = s.sendmail(fromEmail, toList, msg)

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Could not delivery mail to: %s

Server said: %s
%s

%s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException, errstr


def processTo(to):
    """
    helper function that processes a string or list of addresses.

    returns (list of addresses, comma-delimited string of addresses)
    
    The first is used for rawEmail, and the second is used when creating
    headers.
    """
    toList = []
    if type(to) is list:
        toList = to[:]
        to = ", ".join(to)
    else:
        toList = [to]

    return (toList, to)

def mail(to, subject, message, html=False, fromEmail=FROMEMAIL, server=SERVER):
    """
    Simplifies the emailing process, sending plaintext emails.

    to: accepts a list of emails or a single email.

    returns nothing, or throws an smtplib.SMTPException if there is a problem.
    """
    toList, to = processTo(to)

    htmlHeader = '\n'

    if html:
        htmlHeader = 'Content-Type: text/html; charset=ISO-8859-1\n\n'

    msg = '''To: %s
From: %s
Subject: %s
Date: %s
%s
%s
    ''' % (to, fromEmail, subject, formatdate(), htmlHeader, message)

    rawEmail(toList, msg, fromEmail=fromEmail, server=server)


def sms_me(subject, message):
    " sends an email to ryan's phone "
    mail('sms-ryan@acceleration.net', subject, message)

def emailHtml(to, subject, message):
    toList, to = processTo(to)
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = fromEmail
    msg['Date'] = formatdate()
    msg.preamble = 'You are not using a MIME-aware reader\n'
    msg.epilogue = ''

    #add the main message
    msg.attach(MIMEText(message))
    
    rawEmail(toList, msg.as_string())

def emailFile(to, subject, message, filePath, mimeType=None, fromEmail=FROMEMAIL, server=SERVER):
    """
    sends an email attachment to the given address or list of addesses.
    
    if the mimeType is not specified, it uses mimetypes.guess_type to determine it.
    """
    toList, to = processTo(to)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = fromEmail
    msg['Date'] = formatdate()
    msg.preamble = 'You are not using a MIME-aware reader\n'
    msg.epilogue = ''

    #add the main message
    msg.attach(MIMEText(message))
    
    if type(filePath) is list:
        for f in filePath:
            addFile(f, msg, mimeType)
    else:
        addFile(filePath, msg, mimeType)

    rawEmail(toList, msg.as_string(), server=server, fromEmail=fromEmail)

def addFile(filePath, message, mimeType=None):
    if mimeType is None:
        mimeType = mimetypes.guess_type(filePath)[0]
     
    maintype, subtype = mimeType.split('/', 1)

    def processFactory(mimeRunner, openMethod):
        def proc(path, subtype):
            fp = open(path, openMethod)
            fileMsg = mimeRunner(fp.read(), _subtype = subtype)
            fp.close()
            return fileMsg
        
        return proc
    
    messageMaker = {'text':processFactory(MIMEText, 'r'),
                    'image':processFactory(MIMEImage, 'rb'),
                    'audio':processFactory(MIMEAudio, 'rb')}
    
    
    
    fMsg = None
    if messageMaker.has_key(maintype):
        fMsg = messageMaker[maintype](filePath, subtype)
    else:
        fp = open(filePath, 'rb')
        fMsg = MIMEBase(maintype, subtype)
        fMsg.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        Encoders.encode_base64(fMsg)
        
    if fMsg is not None:
        fMsg.add_header('Content-Disposition', 'attachment', filename=filePath)        
        message.attach(fMsg)
            
