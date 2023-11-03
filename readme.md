# Introduction
This project uses a modified copy of [whisper streaming](https://github.com/ufal/whisper_streaming) for the server, 
and pyside6 for the client. The `socket` python library is used for communication between server and client.

# Main takeaways
- The application uses eng-to-ipa to convert transribed text to IPA characters.
It also checks against a list of IPA characters to find out what letter was spoken.

Here is an extract of the code

```
self.character_ipa_map = {
    "C": ["si"], "D": ["di"], "E": ['i'], 
    "F": ['ɛf'],"L": ['ɛl'],"O": ['oʊ'],
    "P": ['pi'],"T": ['ti'],"Z": ['zi', 'zæk', 'zek*','zɛk','zeee']
}
```

This was meant to deal with the scenarios when Whisper determines the user input as words instead of letters. However, it appears that Whisper may automatically "complete" the user's input by adding in additonal words behind, which in this case, the ipa conversion would not be able to solve.

Example: If the user says "C", Whisper may produce the result "see", or "see you".

Additonally, more IPA characters may be added. For example, Whisper may detect a spoken `L` as `Al`, in which case, adding in `"L": ['æl','ɛl']` would resolve the issue.

- During the eye acuity test, the application ignores the user input if no letters were detected (nothing from user input is in the list of IPA characters).

# Installation

## Install requirements
`pip install pyside6`

`pip install numpy`

`pip install pip install librosa`

`pip install eng-to-ipa`


## Run
Then run `app.py`