from pyhelios import Context, WeberPennTree, WPTType

context = Context()
wpt = WeberPennTree(context)

tree_id = wpt.buildTree(WPTType.LEMON)

print(f"tree_id: {tree_id}")

trunk_uuids = wpt.getTrunkUUIDs(tree_id)

print(f"trunk_uuids: {trunk_uuids}")

branch_uuids = wpt.getBranchUUIDs(tree_id)

print(f"branch_uuids: {branch_uuids}")

leaf_uuids = wpt.getLeafUUIDs(tree_id)

print(f"leaf_uuids: {leaf_uuids}")

all_uuids = wpt.getAllUUIDs(tree_id)

print(f"all_uuids: {all_uuids}")

wpt.setBranchRecursionLevel(3)

wpt.setTrunkSegmentResolution(3)

wpt.setBranchSegmentResolution(3)

wpt.setLeafSubdivisions(3, 3)

tree_id = wpt.buildTree(WPTType.PISTACHIO)

print(f"tree_id: {tree_id}")

trunk_uuids = wpt.getTrunkUUIDs(tree_id)

print(f"trunk_uuids: {trunk_uuids}")
