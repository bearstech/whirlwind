def target_to_path(root, target):
    return "%s%s.wsp" % (root, "/".join(target.split(".")))
