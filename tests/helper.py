try:
    helper_loaded
except NameError:
    import sys
    sys.path.append('../plugin/python/')
    helper_loaded = True
