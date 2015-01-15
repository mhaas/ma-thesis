# -*- coding: utf-8 -*-


# Code taken from http://code.activestate.com/recipes/391367-deprecated/
import warnings


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning,
                      stacklevel=2)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


# === Examples of use ===
@deprecated
def some_old_function(x, y):
    return x + y


class SomeClass:

    @deprecated
    def some_old_method(self, x, y):
        return x + y
