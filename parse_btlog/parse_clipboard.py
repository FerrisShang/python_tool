import os
from time import sleep
import pyperclip
import parse_protocol

if __name__ == '__main__':
  print(
    '''
On Windows, no additional modules are needed.
On Mac, the pyobjc module is used, falling back to the pbcopy and pbpaste cli
  commands. (These commands should come with OS X.).
On Linux, install xclip or xsel via package manager. For example, in Debian:
  sudo apt-get install xclip
  sudo apt-get install xsel
-----------------------------------
  ''')

  old_stream = None
  while True:
    clip_str = pyperclip.paste()
    try:
      stream = bytearray.fromhex(clip_str)
    except:
      stream = None
    if stream is not None and len(stream) > 0 and stream != old_stream:
      print('*'*64 + '\n' + parse_protocol.UnpackStream(stream).to_string())
      old_stream = stream
    sleep(0.5)




