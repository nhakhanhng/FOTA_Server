import ftplib
import time
import ssl

class MyFTP_TLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)  # this is the fix
        return conn, size

host = 'begvn.home'
port = 21
user = 'user1'
passwd = '123456'
acct = 'Normal'
ca_cert_path = '../../certs_keys/ca.crt' 
ssl_context = ssl.create_default_context(cafile=ca_cert_path)
# cert = open(ca_cert_path,'r')
# print(cert.read())

ftps = MyFTP_TLS(context=ssl_context)

ftps.set_debuglevel(1)

ftps.connect(host, port)

print(ftps.getwelcome())
print(ftps.sock)

# ftps.auth()

ftps.login(user, passwd, acct)

ftps.set_pasv(True)
ftps.prot_p()

print('Current directory:')
print(ftps.pwd())
files = ftps.nlst()
ftps.cwd("New")
files = ftps.nlst()
print(files)
for file in files:
    with open(file, 'wb') as f:
        ftps.retrbinary("RETR " + file, f.write, 1024)

# with open("file/upload.txt", "w") as f:
#     f.write("Time: " + time.ctime(int(time.time())))

with open("file/hello.txt", "rb") as f:
    ftps.storbinary("STOR " + "upload.txt", f)

ftps.quit()