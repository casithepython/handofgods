import main as db

class UserDoesNotExistException(Exception):
  pass

class User:
  def __init__(self, discord_id, name=None):
    self.discord_id = discord_id
    self.power = UserPower(self)
    if not db.user_discord_id_exists(discord_id):
      if name is None:
        raise UserDoesNotExistException()
      else:
        db.new_user(name, discord_id)
  
  def insert_attribute(self, attribute_id, value, start_turn, expiry_turn):
    db.insert_attribute(self.discord_id, attribute_id, value, start_turn, expiry_turn)
  
  def increase_attribute(self, attribute_id, value, expiry_turn):
    db.increase_attribute(self.discord_id, attribute_id, value, expiry_turn)
  
  def get_attribute(self, attribute_id):
    return db.get_attribute(self.discord_id, attribute_id)
  


class UserPower:
  def __init__(self, user):
    self.user = user
  
  def get(self):
    return db.get_power(self.user.discord_id)
  
  def add(self, amount):
    db.give_power(self.user.discord_id, amount)
  
  def spend(self, amount):
    return db.spend(self.user.discord_id, amount)
