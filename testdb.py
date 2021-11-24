def get_tech_id(_):
  return 0
def get_player_id(_):
  return 1

class Attributes:
  DIVINE_INSPIRATION_RATE = 0
  AWAKE_REVELATION_RATE = 1
  ASLEEP_REVELATION_RATE = 2
  DIVINE_AVATAR_RATE = 3
  DIVINE_INSPIRATION_COST = 4
  AWAKE_REVELATION_COST = 5
  ASLEEP_REVELATION_COST = 6
  DIVINE_AVATAR_COST = 7

def get_attribute(_, attribute):
  attributes = [0.1, 0.2, 0.3, 0.4123,
  5, 50, 20, 100]
  return attributes[attribute]

def get_tech_cost(_):
  return 1

def calculate_tech_cost(player_id, tech_id):
    base_cost = get_tech_cost(tech_id)
    player_cost_multiplier = get_research_cost_multiplier(player_id)
    return base_cost * player_cost_multiplier

def get_player_tech(_):
  return []

def get_research_cost_multiplier(_):
  return 1



def attempt_research(player_id, tech_id, method):
    if tech_id not in get_player_tech(player_id):
        if method == "divine_inspiration":
            attribute_rate = get_attribute(player_id, 6)
            attribute_cost = get_attribute(player_id, 7)
        elif method == "awake_revelation":
            attribute_rate = get_attribute(player_id, 8)
            attribute_cost = get_attribute(player_id, 9)
        elif method == "asleep_revelation":
            attribute_rate = get_attribute(player_id, 10)
            attribute_cost = get_attribute(player_id, 11)
        elif method == "divine_avatar":
            attribute_rate = get_attribute(player_id, 12)
            attribute_cost = get_attribute(player_id, 13)
        else:
            return False, "Invalid method"

        cost = calculate_tech_cost(player_id, tech_id)
        attempt_cost = attribute_cost * get_research_cost_multiplier(player_id)
        if spend_power(player_id, attempt_cost) and get_power(player_id) > cost:
            if random.random() <= attribute_rate:
                complete_research(player_id, tech_id)
                spend_power(player_id, cost)
                return True
            else:
                return False, "failed chance"
        else:
            return False, "Insufficient DP"
    else:
        return False, "already researched"