import data_wizard

from .models import Family, Food_items, Other_items, User

data_wizard.register(Food_items)
data_wizard.register(Other_items)
data_wizard.register(User)
data_wizard.register(Family)
