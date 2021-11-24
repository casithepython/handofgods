def get_tech_id(_):
  return 0
def get_player_id(_):
  return 1

class Attributes:
  DIVINE_INSPIRATION_RATE = 0
  AWAKE_REVELATION_RATE = 1
  ASLEEP_REVELATION_RATE = 2
  DIVINE_AVATAR_RATE = 3

def get_attribute(_, attribute):
  attributes = [0.1, 0.2, 0.3, 0.4123]
  return attributes[attribute]
