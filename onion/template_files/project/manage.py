#! /usr/bin/env python
#coding=utf-8

import os, sys
from onion.manage import main


path = os.path.dirname(os.path.abspath(__file__))
if not path in sys.path:
    sys.path.insert(0, path)


if __name__ == '__main__':
    main()
