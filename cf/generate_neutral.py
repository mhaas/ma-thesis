#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools

def gen():
    det = ["laut der",
           "der",
           "innerhalb der",
           "nach der",
           "vor der",
           "während der",
           "bei der" ]
    adj = ["einzigen",
           "öffentlichen",
           "kanadischen",
           "gegenwärtigen",
           "mexikanischen",
           "spanischen",
           "diesjährigen"]
    nn = ["Herbstmesse",
          "Sonderkommission",
          "Podiumsdiskussion",
          "Fluggesellschaft",
          "Baugesellschaft",
          "Landwirtschaft"]

    for phrase in itertools.product(det, adj, nn):
        print " ".join(phrase)

if __name__ == "__main__":
    gen()
