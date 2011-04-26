#!/usr/bin/python

import hashlib


class Trial:
	test = "apples mangoes, trees"
	def dohash(self, myinput):
		m = hashlib.sha1()
		print m.digest_size
		print m.block_size
		m.update(myinput)
		print m.hexdigest()
		msub = m.hexdigest()[:6]
		print msub
mytrial = Trial()
mytrial.dohash("hellu")
		
