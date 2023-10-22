

import requests
from phonemizer import phonemize
from phonemizer.separator import Separator


# phn is a list of 190 phonemized sentences

phn = phonemize(
    "ni hao",
    language='en-us',
    backend='espeak',
    separator=Separator(phone=None, word=' ', syllable='|'),
    strip=True,
    preserve_punctuation=True,
    njobs=1)
print (phn)

'''
import subprocess

input_text = "hello world"
command = f'echo "{input_text}" | phonemize'
output = subprocess.check_output(command, shell=True, text=True)
print(output)
'''
