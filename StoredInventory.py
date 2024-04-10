from Assembly import Assembly
import copy

class InventoryItem:
    """ A class to hold wordy descriptions and quantity data about an assembly that is not stored inside the assembly object."""
    def __init__(self, assembly, quantity, description):
        self.assembly  = assembly
        self.quantity = quantity
        self.description = description

class StoredInventory:
    """Class contain the list of fuel inventory"""
    inventoryList = []
    def __init__(self, listOfAssemblies, listOfQuantities, listOfDescriptions):
        assert len(listOfAssemblies) == len(listOfQuantities)
        for a, q, d in zip (listOfAssemblies, listOfQuantities, listOfDescriptions):
            self.inventoryList.append(InventoryItem(a,q,d))

    def addInventoryItem(self, assembly, quantity, description):
        """ Add an assembly to the Inventory of stored fuel """
        self.inventoryList.append(InventoryItem(assembly,quantity,description))
        return len(self.inventoryList)-1

    def removeInventoryItem(self, index):
        """ Remove an assembly from the inventory """
        temp = self.inventoryList[index]
        temp.quantity -= 1
        if temp.quantity == 0:
            del self.inventoryList[index]
        return copy.deepcopy(temp.assembly)
