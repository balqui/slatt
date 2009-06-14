#! /usr/bin/python

from sys import stdin

# code 10410 obsolete, remains just in case for compatibility

tradNS = {
	'10500': 'Wife-religion-not-islam',
	'10501': 'Wife-religion-islam    ',
	'10119': 'age-younger-than-20  ',
	'10129': 'age-between-20-and-29',
	'10900': 'Good-exposure-to-media',
	'10139': 'age-between-30-and-39',
	'10400': 'No-children-so-far        ',
	'10401': '1-child-so-far            ',
	'10402': '2-children-so-far         ',
	'10403': '3-children-so-far         ',
	'10404': '4-children-so-far         ',
	'10149': 'age-between-40-and-49',
	'10410': '10-or-more-children-so-far',
	'10416': '10-or-more-children-so-far',
	'10801': 'Low-standard-of-living      ',
	'10802': 'Near-low-standard-of-living ',
	'10803': 'Near-high-standard-of-living',
	'10804': 'High-standard-of-living     ',
	'10301': 'Low-husband-education      ',
	'10302': 'Near-low-husband-education ',
	'10303': 'Near-high-husband-education',
	'10304': 'High-husband-education     ',
	'10701': 'Husband-occupation-1',
	'10702': 'Husband-occupation-2',
	'10703': 'Husband-occupation-3',
	'10704': 'Husband-occupation-4',
	'10456': '5-or-6-children-so-far    ',
	'10201': 'Low-wife-education      ',
	'10202': 'Near-low-wife-education ',
	'10203': 'Near-high-wife-education',
	'10204': 'High-wife-education     ',
	'10600': 'Wife-is-now-working',
	'10479': '7-to-9-children-so-far    ',
	'11000': 'No-contraceptive-method        ',
	'11001': 'Long-term-contraceptive-method ',
	'11002': 'Short-term-contraceptive-method'
        }

if __name__=="__main__":
        for line in stdin:
                for strcod in line.split():
                        if strcod in tradNS.keys():
                                print tradNS[strcod],
                        else:
                                print strcod,
                print

