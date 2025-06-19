import data_wizard
from .models import food_items, other_items, user, family

data_wizard.register(food_items)
data_wizard.register(other_items)
data_wizard.register(user)
data_wizard.register(family)
