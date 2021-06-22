pi = '3141592653589793238462643383'
alphabet = 'abcdefghijklmnopqrstuvwxyz'
new_alphabet = {}
for i in range(0,len(pi)-2):
	group = pi[i]+pi[i+1]+pi[i+2]
	#print(str(i+1)+': '+group)
	if group in new_alphabet.values():
		print('degenerated new alphabet')
		break
	else: new_alphabet[alphabet[i]] = group
print(new_alphabet)
print('\n')

#only letters contained in the string called alphabet
message = 'apple'
encryption = ''
for i in range(0,len(message)):
	encryption+=new_alphabet[message[i]]+','
print(encryption)
