#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
bursts.py

should work as 
	import bursts
	[list of bursts] = bursts.bursts(docs2date, date2countC=backgroundcounts, resolution='week', doc2relevance={},  burstdetector='kleinberg', normalise=True, bg_smooth=True)
where
doc2date: is a dictionary from document id to a datetime (or date) object
doc2relevance: is a dictionary from document id to a relevance score. Can be empty, then the bursts are not weighted by document relevance
date2countC: date2counts of the collection for background smoothing and/or normalisation. Not implemented yet.
resolution: \in [day, week, month, year]
burstdetector: \in [kleinberg, default] The default detector is my implementation. Kleinberg has a lot of parameters and might not work without careful tuning
normalise: \in [True, False] Normalise with a background collection 
bg_smooth= \in [True, False] Smooth with a background collection. Avoiding empty bins/dates, unless the background collection doesn't have anything either 

Created by Maria-Hendrike Peetz on 2011-10-07.
FL-21-Nov-2012	do not use just 'print', but print >> stderr for mod_wsgi
FL-18-Nov-2012	print only in DEBUG mode
FL-21-Jan-2013	circumvent exception in defaultdetector() for empty range
FL-04-Apr-2013
"""

from sys import stderr
import sys
import os
import collections
import numpy
import irutils
import datetime
import math

from django.conf import settings


class Burst(list):
	def __init__(self, s, m):
		self.mean = m
		self.std = s
		self.peakdates = []
		self.date2cut = {}



def __normaliseRelevance(doc2relevance):
	sumrelevance = max([abs(i) for i in doc2relevance.itervalues()])
	for d, r in doc2relevance.iteritems():
		doc2relevance[d] =  1-(r/sumrelevance)
	return doc2relevance


def __normalise(date2count, date2countC):
	for date, v in date2countC.iteritems():
		try:
			date2count[date] /= float(v)
		except ZeroDivisionError:
			date2count[date] = 0
	return date2count



def __movingAverage(values, p=2):
	p = p+1
	newvalues = []
	for i,k in enumerate(values):
		begin = i-int(p/2)
		end = i+int(p/2)+1
		if begin<0:
			begin = 0
		if end>len(values):
			end = len(values)-1
		newvalues.append( sum(values[begin:end])/p)
	return newvalues

def __KNN(doc2date):
	# KNN?
	return doc2date

def __background_smoothing(date2count, date2countC, lamda=0.9):
	for date, v in date2countC.iteritems():
		date2count[date] = lamda*date2count.get(date, 0) +  (1-lamda)*v
	return date2count



def __buildListDates(begindate, enddate):
	datelist = range(int(begindate), int(enddate)+1)
	return datelist	



def getDate(i, resolution, mindate):
	if resolution == 'day':
		return mindate + datetime.timedelta(days=i)
	elif resolution == 'week':
		return mindate + datetime.timedelta(weeks=i)
	elif resolution == 'month':
		m = mindate.month+i
		year = int(mindate.year + m/12)
		while m > 12:
			m = m -12
		
		date = datetime.date(year, m, mindate.day)
	#	print >> stderr, mindate, date, i
		return date
	elif resolution == 'year':
		date = datetime.date(mindate.year+i, mindate.month, mindate.day)
		return date
	elif resolution == 'hours':
		return mindate + datetime.timedelta(hours=i)
	elif resolution == 'halfday':
		return mindate + datetime.timedelta(hours=i/12)
	


def resolveDate(date, begindate, resolution):
	diff = date-begindate
	if resolution == 'day':
		return diff.days + diff.seconds/(3600.*24.)
	elif resolution == 'week':
		return resolveDate(date, begindate, 'day')/7.
	elif resolution == 'month':
		return (date.month - begindate.month) + (date.year - begindate.year)*12 + diff.days/30
	elif resolution == 'year':
		return (date.year - begindate.year) + (date.month - begindate.month)/12. + diff.days/365
	elif resolution == 'hours':
		return diff.seconds/3600.0 + diff.days*24
	elif resolution == 'halfday':	
		return  diff.seconds/(3600.*12.) + diff.days*2


def unresolve(bursts, doc2date, resolution, mindate):
	for burst in bursts:
		newpeaks = set([])
		for d in burst:
			newpeaks.add(doc2date[d])
		burst.peakdates = 	newpeaks
	return bursts


def resolve(doc2date, doc2relevance, date2countC, resolution):
	doc2date_new = {}
	# Create default relevance:
	if len(doc2relevance) == 0:
		for d in doc2date:
			doc2relevance[d] = 1.0
	
	# find minimum date:
	dates = set(doc2date.values() + date2countC.keys())
	mindate =  min(dates)
	date2countC_new = collections.defaultdict(lambda: 0)
	date2count = collections.defaultdict(lambda: 0)
	date2docs = collections.defaultdict(lambda: [])
	for docid, date in doc2date.iteritems():
	#	print >> stderr, date, int(resolveDate(date, mindate, resolution))
		newdate = int(resolveDate(date, mindate, resolution))
		doc2date_new[docid] = newdate
		date2count[newdate] += doc2relevance[docid]
		date2docs[newdate].append(docid)
	for date, c in date2countC.iteritems():
		date2countC_new[int(resolveDate(date, mindate, resolution))] += c
#	print >> stderr, "date2countC_new.values():", date2countC_new.values()
	m = max(date2countC_new.values())
	for k in date2countC_new:
		date2countC_new[k] /= float(m)
	return doc2date_new, date2count, date2countC_new, mindate, date2docs



def resolveDate(date, begindate, resolution):
	diff = date-begindate
	if resolution == 'day':
		return diff.days + diff.seconds/(3600.*24.)
	elif resolution == 'week':
		return resolveDate(date, begindate, 'day')/7.
	elif resolution == 'month':
		return (date.month - begindate.month) + (date.year - begindate.year)*12 + (date.day - begindate.day)/30
	elif resolution == 'year':
		return (date.year - begindate.year) + (date.month - begindate.month)/12. + (date.day - begindate.day)/30
	elif resolution == 'hours':
		return diff.seconds/3600.0 + diff.days*24
	elif resolution == 'halfday':	
		return  diff.seconds/(3600.*12.) + diff.days*2
	 



def dates2intervals(dates2counts, doc2date, resolution='day'):
	interval2docs = {}
	xes = []
	previous = min(dates2counts.iterkeys())
	date2docs = collections.defaultdict(lambda: [])
	for doc,date in doc2date.iteritems():
		date2docs[date].append(doc)
	interval2docs[0] = date2docs[0]
	datelist = sorted(dates2counts.keys())
	datelist.append(max(datelist)+1)
	for i, date in enumerate(datelist[:-1]):
		interval2docs[len(xes)] = date2docs[date]
		counts = dates2counts[date]
	#	print >> stderr, date, hours(datelist[i+1]-date, resolution)/float(counts), counts
		xes.append(hours(datelist[i+1]-date, resolution)/float(counts))
	return xes, interval2docs, date2docs

def tau(l,j, n, gamma):
	if l>=j:
		return 0.0
	else:
		return (j-l) * gamma * math.log(n+1) #+ 1) - math.log(1)

def f(j, x, alphas):
	a = alphas[j]
	#return x/a
	# print >> stderr, a, x, a*x, math.exp(-a*x)
	# if (a*x)>1:
	# 	return -math.log(a*math.exp(-1))
	b = -math.log(a*math.exp(-a*x))
	# print >> stderr, min(b, -0.002)
	if b>0:
		return -2
	return b


def kleinberg(dates2counts, doc2date, levels, gamma, s, resolution):
	xes, interval2docs, date2docs = dates2intervals(dates2counts, doc2date, resolution)
	summe = sum(xes)
	n= len(xes)
	#T = numpy.mean(dates2counts.values())
	#init = n/
	alphas = [n * s**i for i in range(levels)]
	#print >> stderr, alphas
	#alphas = [n * s**i for i in range(levels)]
	#print >> stderr, alphas

	states = [0 for i in range(n+1)]
	paths = [[0 for i in range(levels)] for i in range(n)]
	lnfs = [[0,0]]+[[f(j, 1/xes[i], alphas) for j in range(levels)] for i in range(n)]
	Cells = [[0 for i in range(levels)] for i in range(n+1)]
	# first cell:
	Cells[0] = [float('inf') for i in range(levels)]
	Cells[0][0] = 0
	for i in range(1, n+1):
		previous = Cells[i-1]
		current =  Cells[i]
		paths[i-1] = [0,0]
		#m = min(previous)
		#for li in range(levels):
		B = lnfs[i][0] + previous[0]
		A = lnfs[i][1] + previous[0] + tau(0,1, n, gamma)
		if A>B:
			paths[i-1][0] = 1
			Cells[i][0] = A
		else:
			Cells[i][0] = B
		Cells[i][1] = lnfs[i][1] + previous[0]
			# if (lnfs[i][li] + previous[1]) > (lnfs[i][li] + previous[0] + tau(0,li, n, gamma)):
			# 	q = 1
			# else:
			# 	q=0
			# B = l
			# q = 0
			# for j in range(0,levels-1):
			# 	tmpD = lnfs[i][li] + previous[j] + tau(j,li, n, gamma)
			# 	print >> stderr, tmpD, d, j, li, lnfs[i][li], previous[j], previous[levels-1],tau( j,li, n, gamma)
			# 	if (tmpD <= d and j>li):
			# 		d = tmpD
			# 		q = li
			# 	else:
			# 		d = tmpD
		# 		print >> stderr, q
		#Cells[i][li] = d
		#paths[i][li] = q
    
	#print >> stderr, paths
	# compute the last cells path, starting point for going back
	d = min(lnfs[-1])
	q = lnfs[-1].index(d)
	
	# going back
	# build up the path backwards and then reverse				
	states[-1] = Cells[i].index(min(Cells[i]))
	for it in range(len(paths)-1, 0, -1):
		nextit = it +1
		currentit = it
		states[currentit] = paths[currentit][states[nextit]]
	#states[0] = 1
	# for i, v in enumerate(xes):
	# 	print >> stderr, v, states[i], paths[i-1]
	if settings.DEBUG == True:
		for c in lnfs:
			print >> stderr, c
	
	
	bursts = []
	currentburst = []
	#print >> stderr, states
	#print >> stderr, xes
	#print >> stderr, paths
	for i,state in enumerate(states[1:-1]):
		#print >> stderr, i, state
		if len(currentburst) > 0 and state < 1:
			bursts.append([])
			bursts[-1].extend(currentburst)
			currentburst = []			
		elif state>0:
			currentburst.extend(interval2docs[i])
			
	if len(currentburst) > 0 and state>0:
		bursts.append(currentburst)
#	print >> stderr, bursts
	burstr =[]
	for b in bursts:
		dates = []
		dates2countsb = {}
		for d in b:
			dates2countsb[doc2date[d]] = dates2countsb.get(doc2date[d], 0)+1
		enddate = max(dates2countsb.iterkeys())
		begindate = min(dates2countsb.iterkeys())
		for date in __buildListDates(begindate, enddate):
			dates.append(dates2countsb.get(date, 0))
		mean = numpy.mean(dates)
		std = numpy.std(dates)
		burst = Burst(std, mean)
		burst.extend(b)
		burst.peakdates = dates2countsb.keys()
		burstr.append(burst)
	bursthist = [[] for d in range(max(dates2counts.keys())) ]
	for burst in burstr:
		for p in burst.peakdates:
			bursthist[p].append(1)
	
	# print >> stderr, "#spike!\t",
	# print >> stderr, "\t".join([str(len(i)) for i in bursthist])
	# print >> stderr, resolution, "\t",
	# print >> stderr, "\t".join([str(i) for i in range(len(bursthist))])
	
	return burstr, {}

def bursts(doc2date, doc2relevance = {}, date2countC={}, resolution='week', burstdetector='default', mov_avg=False, normalise=True, bg_smooth=True):
	if settings.DEBUG == True:
		print >> stderr, "lexicon/burstsdetector/bursts()"

	#1. resolution of doc2date and date2countC. Binning of dates, by relevance
#	print >> stderr, "resolve"
	doc2index, index2count, index2countC, mindate, date2docs = resolve(doc2date, doc2relevance, date2countC, resolution)

	#2. Normalise
	if normalise:
	#	print >> stderr, "normalise"
		index2count = __normalise(index2count, index2countC)

	#3. smooth
	if bg_smooth:
		if  len(doc2relevance) == 0:
		#	print >> stderr, "smooth"
			index2count = __background_smoothing(index2count, index2countC)
		else:
			if settings.DEBUG == True:
				print >> stderr, "Cannot do background smoothing."

	#4. Burst detector
	if burstdetector == 'kleinberg':
		bursts, limit = kleinberg(index2count, doc2index, 2, 0.05, 2, len(date2docs[i]))
	else:
		bursts, limit = defaultdetector(index2count, doc2index)

	# 5. translate bindates back to dates
	bdays = []
	dates2cut = {}
	for burst in bursts:
		bdays.extend(burst.peakdates)
		
	bursts = unresolve(bursts, doc2date, resolution, mindate)
	countsNbursts = {}
	# print >> stderr, burst.peakdates
	for i, c in index2count.iteritems():
		date = getDate(i,resolution, mindate)
		if i in bdays:
		#	if settings.DEBUG == True:
		#		print >> stderr, date
			countsNbursts[date] = (c, 1, i, limit.get(i, None), len(date2docs[i]), date2docs[i])
		else:
			countsNbursts[date] = (c, 0, i, limit.get(i, None), len(date2docs[i]), date2docs[i])

	return countsNbursts, bursts


def defaultdetector(date2count, doc2date):
#	print >> stderr, "defaultdetector()"

	#print >> stderr, date2count
	date2docs = collections.defaultdict(lambda: [])
	for doc, index in doc2date.iteritems():
		date2docs[index].append(doc)
		
	burstsfound = {}
	values = []
# >> FL 24-Jan-2013
	try:	# handle ValueError exception: min() arg is an empty sequence
		for d in range(min(date2count.iterkeys()), max(date2count.iterkeys())+1):
			values.append(date2count.get(float(d), 0))
	except ValueError:
		pass
# <<

	mean = numpy.mean(values)
	std = numpy.std(values)

	blist = []
	limit = {}
	#print >> stderr, values
	for i,v in enumerate(values):
		limit[i] = 2*std
		if v >=(mean + 2*std): 
			blist.append("P")
		elif v >= (mean + std):
			blist.append("I")
		else:
			blist.append("0")
	## Identify the bursts
	# print >> stderr, values, blist
	#print >> stderr, blist
	for i, v in enumerate(blist):
		if v=='P':
			burstsfound[i] = [i]
	for k in burstsfound:
		kbef = k -1
		while kbef>=0 and blist[kbef] in ('I', 'P'):
			burstsfound[k].append(kbef)
			kbef -= 1
		kaf = k+1
		while kaf<len(blist) and blist[kaf] in ('I', 'P'):
			burstsfound[k].append(kaf)
			kaf += 1
	## Merge the bursts
	
	for b, days in burstsfound.items():
		vlist = []
		for d, value in enumerate(values):
			if d in days:
				vlist.append(value)
			else:
				vlist.append(0)
		maxday = vlist.index(max(vlist))
		del burstsfound[b]
		burstsfound[maxday] = days
	# make the bursts resultsets
	burstsr = []
	for m, burst in burstsfound.iteritems():
		minburst = min(burstsfound)
		bval = __finddistribution(values, burst)
		m= numpy.mean(bval)
		s= numpy.std(bval)
		b = Burst(s, m)
		for v in burst:
			if blist[v] == 'P':
					b.extend(date2docs[v])
					b.peakdates.append(v)
			else:
					b.extend(date2docs[v])	
			b.date2cut[v] = limit[v]			
		burstsr.append(b)
	return burstsr, limit
	


def __finddistribution(values, burst):
	dist = [b for b in burst]
	emin = min(burst)
	emax = max(burst)
	v=values[emax]
	nemax = min([emax + 1, len(values)-1])
	v1 = values[nemax]
	while v > v1 and not v1==0:
		dist.append(nemax)
		nemax += 1
		if nemax >= len(values): break
		v = v1
		v1 = values[nemax]

	v=values[emin]
	nemin = emin - 1
	v1 = values[nemin]
	while v > v1 and not v1==0:
		dist.append(nemin)
		nemin -= 1
		if nemin < 0: break
		v = v1
		v1 = values[nemin]
	return [values[i] for i in dist]			

	


def main():
	rankedfile = sys.argv[1]
	query2docs, query2docsrel = irutils.rankedList2Set(irutils.readInQrels(rankedfile, 10))
	query2docs_tmp, query2docsrel_tmp = irutils.rankedList2Set(irutils.readInQrels(rankedfile, 100))	
	
	for q, docs2date in query2docs.items()[:3]:
		if settings.DEBUG == True:
			print >> stderr, 10*"*", q, 10*"*"
		#bursts(docs2date, {}, 'week')
		# just to debug background corpu s normalisation
		backgroundcounts = collections.defaultdict(lambda: 0)
		for d, date in query2docs_tmp[q].iteritems():
			backgroundcounts[date] += 1
		#print >> stderr, backgroundcounts
		a, b =  bursts(docs2date, date2countC=backgroundcounts, resolution='week', doc2relevance={},  burstdetector='default', normalise=True, bg_smooth=False)
		if settings.DEBUG == True:
			print >> stderr, a
		# vals = []
		# for k, v in a.iteritems():
		# 	vals.append(v[0])
		# print >> stderr, sum(vals)
		# a, b =  bursts(docs2date, date2countC=backgroundcounts, resolution='month', doc2relevance={},  burstdetector='default', normalise=True, bg_smooth=False)
		# vals = []
		# for k, v in a.iteritems():
		# 	vals.append(v[0])
		# print >> stderr, sum(vals)
		

if __name__ == '__main__':
	main()

	
