import data_wizard
from .models import Food_items, Other_items, User, Family

data_wizard.register(Food_items)
data_wizard.register(Other_items)
data_wizard.register(User)
data_wizard.register(Family)
