class User:
    def __init__(self, username, password,id=None,isAdmin=None,location_lat=None,location_long=None) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.isAdmin = isAdmin
        self.location_lat = location_lat
        self.location_long = location_long
class FoodItemOnMenu:
    def __init__(self,id, title,price) -> None:
        self.title = title
        self.price = price
        self.id = id 