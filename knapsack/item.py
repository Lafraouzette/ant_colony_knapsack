# knapsack/item.py
class Item:
    def __init__(self, id, weight, value):
        self.id = id
        self.weight = weight
        self.value = value

    def __repr__(self):
        return f"Item(id={self.id}, weight={self.weight}, value={self.value})"

    def __str__(self):
        return f"Objet {self.id}: poids={self.weight}, valeur={self.value}"