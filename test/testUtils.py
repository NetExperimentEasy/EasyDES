from EasyDES.utils import encode, decode
from copy import deepcopy
from EasyDES.communication.instruction import instructionBase

a = deepcopy(instructionBase)
a["ip"] = "10.12.0.3"
a["port"] = 5678

encode_a = encode(a)
print(encode_a)
decode_a = decode(encode_a)
print(decode_a)

