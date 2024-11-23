from py3dbp import Packer, Bin, Item
from py3dbp.constants import RotationType

packer = Packer()

packer.add_bin(Bin('large-box', 8.0, 12.0, 5.5, 70.0))

packer.add_item(Item('Item 1', 4, 2, 2, 1))
packer.add_item(Item('Item 2', 4, 2, 2, 1))
packer.add_item(Item('Item 3', 4, 2, 2, 1))
packer.add_item(Item('Item 4', 8, 4, 2, 1))
packer.add_item(Item('Item 5', 8, 4, 2, 1))
packer.add_item(Item('Item 6', 8, 4, 2, 1))
packer.add_item(Item('Item 7', 8, 4, 2, 1))
packer.add_item(Item('Item 8', 8, 4, 2, 1))
packer.add_item(Item('Item 9', 8, 4, 2, 1))

packer.pack()

print("TOTAL BINS USED:", len(packer.bins))
for b in packer.bins:
    print(":", b.string())

    print("FITTED ITEMS:")
    for item in b.items:
        print("===> ", item.string())

    print("UNFITTED ITEMS:")
    for item in b.unfitted_items:
        print("===> ", item.string())
