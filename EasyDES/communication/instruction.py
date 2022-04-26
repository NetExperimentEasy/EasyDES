from copy import deepcopy
# Please do not use dict directly , deepcopy it

instructionBase = {
    "ip": str,
    "port": int,
    "type":"instructionBase"
}

# Extend instrusition
# register reuqire
registerInstruction = {
    "w_ip": str,    # worker's ip
    "w_port": int,  # worker's port
    "type": "registerInstruction"
}

# register reply
registeredReplyInstruction = {
    "w_ip": str,    # worker's ip
    "c_ip": str,    # controller's ip
    "c_port": int,  # controller's port
    "type": "registeredReplyInstruction"
}

# mission_start all/one's uuid
# controller to worker , if all , start all mission, if uuid, start uuid mission
missionStartInstruction = {
    "uuid": "all",
    "type": "missionStartInstruction"
}

# mission started reply
startedReplyInstruction = {
    "uuid": None,   # spectial mission uuid
    "type": "startedReplyInstruction"
}