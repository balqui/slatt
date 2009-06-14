#! /usr/bin/python

from sys import stdin

tradSN = {
	'age-younger-than-20': '10119',
	'age-between-20-and-29': '10129',
	'age-between-30-and-39': '10139',
	'age-between-40-and-49': '10149',
	'Low-wife-education': '10201',
	'Near-low-wife-education': '10202',
	'Near-high-wife-education': '10203',
	'High-wife-education': '10204',
	'Low-husband-education': '10301',
	'Near-low-husband-education': '10302',
	'Near-high-husband-education': '10303',
	'High-husband-education': '10304',
	'No-children-so-far': '10400',
	'1-child-so-far': '10401',
	'2-children-so-far': '10402',
	'3-children-so-far': '10403',
	'4-children-so-far': '10404',
	'5-or-6-children-so-far': '10456',
	'7-to-9-children-so-far': '10479',
	'10-or-more-children-so-far': '10416',
	'Wife-religion-not-islam': '10500',
	'Wife-religion-islam': '10501',
	'Wife-is-now-working': '10600',
	'Husband-occupation-1': '10701',
	'Husband-occupation-2': '10702',
	'Husband-occupation-3': '10703',
	'Husband-occupation-4': '10704',
	'Low-standard-of-living': '10801',
	'Near-low-standard-of-living': '10802',
	'Near-high-standard-of-living': '10803',
	'High-standard-of-living': '10804',
	'Good-exposure-to-media': '10900',
	'No-contraceptive-method': '11000',
	'Long-term-contraceptive-method': '11001',
	'Short-term-contraceptive-method': '11002'
        }

if __name__=="__main__":

        for line in stdin:
                for string in line.split():
                        if string.strip() in tradSN.keys():
                                print tradSN[string.strip()],
                        else:
                                print string,
                print

