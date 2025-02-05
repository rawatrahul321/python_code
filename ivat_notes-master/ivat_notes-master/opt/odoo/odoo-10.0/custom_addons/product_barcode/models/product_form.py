# -*- coding: utf-8 -*-
from odoo import api, models
import math
import re
from random import randint
import random


class ProductAutoBarcode(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        res = super(ProductAutoBarcode, self).create(vals)
        ean = generate_ean(str(res.id))
        duplicate = self.env['product.product'].search([('barcode','=',ean)])
        print "Product Product Id: =",res.id
        if duplicate:
            print "Duplicate",duplicate
            print "EAN:=",ean
            val = randint(100,999)
            val1 = ean[-3:].strip().replace(" ","")
            print ("RAndom",str(random.randint(111111111,999999999)))
            ean = ean.rstrip(val1) + str(random.randint(111111111,999999999))
            print "VAl1 :=",val1
            print "NEW EAN        @ :=",ean
            res.barcode = ean
        else:
            res.barcode = ean
        return res


def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


def generate_ean(ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
