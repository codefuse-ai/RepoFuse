"""
a -> b means a is imported by b
For the following dependency graph:

  a.py <---- b.py
    /         ^
   v          |
  d.py ----> c.py
    |
    v
  e.py

 x.py <---- y.py <---- z.py
"""