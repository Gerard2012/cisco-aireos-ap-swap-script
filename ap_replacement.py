##############################################################################################
# Global Variables & Config
##############################################################################################

#floor = input('Floor >> ')
cdp_before = input('Pre swap CDP capture >> ')
cdp_after = input('Post swap CDP capture >> ')
crt_script = input('CRT Script File Name: ')
start_num = int(input('Unknown APs starting number >> '))

ap_location = 'New York'
ap_group = 'NY-1221-Group'
crt_output_file = f"C:\Gerards Dump\SecureCRT\Scripts\{crt_script}.vbs"



new_ap_cdp = []
new_ap_cdp_dict = {}
old_ap_cdp = []
old_ap_cdp_dict = {}
ap_dict = {}


##############################################################################################
# Functions
##############################################################################################

def old_ap():

	"""
	Takes the output of 'show ap cdp neighbors all' before the APs have been swapped
	and parses this into 'AP: switch/port' items and appends to old_ap_cdp_dict{}.

	"""

	with open(cdp_before, 'r+') as f:
		lines = f.readlines()
		for line in lines:
			if not line.startswith('AP') and 'Ethernet' in line:
				line = line.split()
				old_ap_cdp.append(line)

	for elem in old_ap_cdp:
		del elem[1]
		elem[1:] = [' '.join(elem[1:])]
		old_ap_cdp_dict[elem[0]] = elem[1]


##############################################################################################

def new_ap():

	"""
	Takes the output of 'show ap cdp neighbors all' after the APs have been swapped,
	filters out new APs registered with default AP name (ie AP+MAC or AP0000.0000.0000)
	and parses this into 'AP: switch/port' items and appends to new_ap_cdp_dict{}.

	"""

	with open(cdp_after, 'r+') as f:
		lines = f.readlines()
		for line in lines:
			if line.startswith('AP'):
				line = line.split()
				new_ap_cdp.append(line)

	for elem in new_ap_cdp:
		del elem[1]
		elem[1:] = [' '.join(elem[1:])]
		new_ap_cdp_dict[elem[0]] = elem[1]


##############################################################################################

def sorted_ap():

	"""
	Compares values in new_ap_cdp_dict{} with vlaues in old_ap_cdp_dict{}.
	If a match is found then the old_ap_cdp_dict{} key (the AP name) is combined with the 
	new_ap_cdp_dict{} value (CDP switch/port info) and this new key/value pair is appended to 
	ap_dict{}.

	"""

	n = start_num

	for i in new_ap_cdp_dict:
		for i2 in old_ap_cdp_dict:
			if new_ap_cdp_dict[i] == old_ap_cdp_dict[i2]:
				ap_dict[i] = i2

	## If no match is found (ie the AP is not patched to the same switch/port as any AP in the pre-swap CDP capture)
	## then the AP is assigned a placeholder AP name. 
	## This placeholder name can be specified when the script is run.
	for i in new_ap_cdp_dict:
		if new_ap_cdp_dict[i] not in old_ap_cdp_dict.values():
			ap_dict[i] = f'NY-1221-AP-X' + str(n)
			n += 1

	## Outputs details of match to terminal.
	print('\n')
	print('Number of APs = ', len(ap_dict))
	print('\n')
	print('NEW AP NAME        \t::\t OLD AP NAME')
	print('===================================================')

	for i in ap_dict:
		print(i, '\t::\t', ap_dict[i])

	print('\n')


##############################################################################################

def crt_commands():

	"""
	Writes the AireOS CLI commands to the SecureCRT .vbs file to reconfigure the new APs.

	"""

	for i in ap_dict:
		new_ap_name = i
		old_ap_name = ap_dict[i]
		with open(crt_output_file, 'a+') as f:
			f.write(f"""
\tcrt.Screen.Send "config ap name {old_ap_name} {new_ap_name}" & chr(13)
\tcrt.Screen.WaitForString "er) >"
\tcrt.Screen.Send "config ap location '{ap_location}' {old_ap_name}" & chr(13)
\tcrt.Screen.WaitForString "er) >"
\tcrt.Screen.Send "config ap primary-base NJ-3CP-01-DC-WLC-1A {old_ap_name} 10.192.223.21" & chr(13)
\tcrt.Screen.WaitForString "er) >"
\tcrt.Screen.Send "config ap secondary-base NJ-3CP-01-DC-WLC-1B {old_ap_name} 10.192.223.23" & chr(13)
\tcrt.Screen.WaitForString "er) >"
\tcrt.Screen.Send "config ap group-name '{ap_group}' {old_ap_name}" & chr(13)
\tcrt.Screen.WaitForString "continue? (y/n)"
\tcrt.Screen.Send "y"
\tcrt.Screen.WaitForString "er) >"\n
		""")


##############################################################################################

def main():

	"""
	Runs the above functions consecutively.

	"""

	new_ap()
	old_ap()
	sorted_ap()

	## Creates the SecureCRT .vbs file and writes the headers/footers to the file
	## while also calling crt_commands() to write the CLI commands to the file.
	with open(crt_output_file, 'w+') as f:
		f.write("""#$language = \"VBScript\"
#$interface = \"1.0\"

crt.Screen.Synchronous = True

Sub Main
	""")

	crt_commands()

	with open(crt_output_file, 'a+') as f:
		f.write("""
End Sub
""")


##############################################################################################
# Run
##############################################################################################

if __name__ == '__main__':

	main()