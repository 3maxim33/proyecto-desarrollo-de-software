import sys
import os



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from explore_exoplanets import load_catalog

def test_funcionamiento_catalogo():
    # funcion simple:
    assert load_catalog is not None
