# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 11:42:45 2015

@author: Aaron Foss
"""

import pprint
import sys
#add directory with assist functions so that they can be loaded
if 'C:\\Users\\Aaron Foss\\Documents\\Python Scripts\\HW3' not in sys.path:
    sys.path.append('C:\\Users\\Aaron Foss\\Documents\\Python Scripts\\HW3')
from zipcode_functions import *
from street_functions import *
from openstreetmaps_mongo import *
from plotting_functions import *
#clean path again
sys.path.remove('C:\\Users\\Aaron Foss\\Documents\\Python Scripts\\HW3')

#change to reflect correct filenames
data_file = 'C:\\Users\\Aaron Foss\\Documents\\Python Scripts\\HW3\denver-boulder_colorado.osm'
json_file = 'C:\\Users\\Aaron Foss\\Documents\\Python Scripts\\HW3\denver-boulder_colorado.osm.json'

if __name__ == "__main__":

#####  BUILD SEGMENT  #################################################

    #map osm data to correct format    
    process_map(data_file, False, True)
    print '\n\n\n########### JSON processed ##################' 
    #import json to mongo    
    import_to_db(json_file)
    print '\n\n\n########### Imported to Mongo ##################'    
    
    #get db name
    db = get_db()
    
    #find unique zipcodes    
    unique_zips = get_zips(db)
    
    #audit zipcodes to determine if they conform to 80[xxx] of 80[xxx]-[xxxx]
    #collect change dictionary and unresolved types dictionary     
    zip_types, zips = audit_zips(unique_zips)
    
    #print zipcode changes
    print '\n\n\n########### Zips to Change ##################'    
    pprint.pprint(dict(zips))
    
    #print unresolvable types
    print '\n\n\n########### Unresolved Zips ##################'
    try:
        pprint.pprint(dict(zips_types))
    except:
        pass
    #sets pipeline so that we can query zipcodes with changes
    pipeline = [{'$match': {'address.postcode': {'$in' : zips.keys()}}},
                {'$project': {'address.postcode': 1}}]
    
    #pulls entries with zipcodes to fix  
    zips_to_change = aggregate(db,pipeline)
    
    #updates zipcodes and adds cities
    update_zips_db(zips,db)
    print '\n\n\n########### Zips Updated ##################'    
   
    #build list of unique streets
    unique_streets = way_streets(db)
    
    #audit streets to determine if they conform to unabbreviated standard
    #parse out housenumbers, units/suites and zipcodes
    #remove city and state from street entry
    #collect change dictionary and unresolved types dictionary     
    street_types, streets = audit_streets(unique_streets)
    
    #print changed street dictionary
    print '\n\n\n########### Streets to Change ##################'    
    pprint.pprint(dict(streets))

    #print unresolvable types    
    print '\n\n\n################# Unresolved Streets ##################'
    print '########### Repaired, but not Standard Type ###########'
    
    pprint.pprint(dict(street_types))
    
    #sets pipeline so that we can query streets with changes, 
    #then isolates address elements
    pipeline = [{'$match': {'address.street': {'$in' : streets.keys()}}},
                {'$project': {'address': 1}}]
    
    #selects entries with streetnames that will change so additional address
    #data (housenumber and postcode) can be validated
    entries_to_change = aggregate(db,pipeline)
    
    #validates/updates address to ([housenumber]+[unit/suite]) [street] [postcode]
    #adds a city matched to post code
    street_cleaner(entries_to_change, streets, db)
    print '\n\n\n########### Streets Updated ##################'    

#####  ANALYSIS SEGMENT  #################################################
    db = get_db()
     
    print '\n\n\n########### Begin Queries ##################'    
    print '################# Entries by City ##################'    
      
    #filters by postecode, then query to group by city 
    #and show ten largest by count of documents
    pipeline = [{'$match': {'address.postcode': {'$exists' : 1}}},
                {'$group': 
                    {'_id': {'city': '$address.city'},
                    'count': {'$sum':1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}]
    
    result = aggregate(db,pipeline)
    
    for res in result:
        print res['_id']['city'], res['count'] 
        
    print '\n\n\n########### Unique Users ##################'    
    
    #query to identify total number of unique contributors
    pipeline = [{'$match': {'created.uid': {'$exists' : 1}}},
                {'$group': 
                    {'_id': {'user': '$created.uid'}}},
                {'$group': 
                    {'_id' : 'null',
                     'count': {'$sum': 1}}}]
                
    result = aggregate(db,pipeline)
    print 'unique users: ',result.next()['count']
    
    print '\n\n\n########### Nodes and Ways ##################'    
    
    #query to pull summary info on numbers of nodes and ways
    pipeline = [{'$match': {'type': {'$exists' : 1}}},
                {'$group': 
                    {'_id': {'type': '$type'},
                    'count': {'$sum': 1}}}]
                
    result = aggregate(db,pipeline)
    
    for res in result:
        print res['_id']['type'], res['count']

    print '\n\n\n########### Aggregate Amenities ##################'
    
    #query to identify the top 10 amenties in aggregate
    pipeline = [{'$match': {'amenity': {'$exists' : 1}}},
                {'$group': {'_id': {'amenity': '$amenity'}, 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 100}]
                
    result = aggregate(db,pipeline)
    
    for res in result:
        print res['_id']['amenity'], res['count']
        
    print '\n\n\n########### Amenities by City ##################'
    
    #query to identify the top amentiy by city, uses compound grouping,
    #filtering, sorting and first aggregator
    pipeline = [{'$match': {'$and': [{'amenity': {'$exists' : 1},'address.city': {'$exists' : 1}}]}},
                {'$group': {'_id': {'city': '$address.city', 'amenity': '$amenity'}, 'count': {'$sum': 1}}},
                {'$match': {'count': {'$gt' : 1}}},               
                {'$sort': {'count': -1}},
                {'$group': {'_id': '$_id.city',
                'most_freq_amenity': {'$first': '$_id.amenity'},'count_amenity': {'$first': '$count'}}},
                {'$sort': {'count_amenity': -1}}]
                
    result = aggregate(db,pipeline)
    
    for res in result:
        print res['_id'], res['most_freq_amenity'], res['count_amenity']
        
    print '\n\n\n########### Frequency of Update ##################'
    
    #query to aggregate posts at a specific time and build a timeseries of activity
    pipeline = [{'$match': {'created.timestamp': {'$exists': 1}}},
                {'$group': {'_id': {'timestamp': '$created.timestamp'}, 'count': {'$sum': 1}}}]
                
    result = aggregate(db,pipeline)
   
    #plot timeseries of activity
    p = plot_update_frequency(result)
    p
    print '\n\n\n########### Plots of Graveyards added by Top Graveyard Editor ############'
    
    #query to identify top amenity adder of a specified amenity type, amenity can be changed
    amenity = 'grave_yard'
    pipeline = [{'$match': {'$and' : [{'created.user': {'$exists' : 1}, 'amenity' : amenity}]}},
                {'$match': {'pos': {'$exists' : 1}}},                
                {'$group': {'_id': {'user': '$created.user'}, 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 1}]
    
    top_adder = aggregate(db,pipeline)
    top_adder = top_adder.next()['_id']['user']
    
    #uses just discovered top adder and queries the locations of
    #the added amenities
    pipeline = [{'$match': {'created.user': str(top_adder)}},
                {'$match': {'amenity': amenity}},
                {'$match': {'pos': {'$exists' : 1}}}]
    
    result = aggregate(db,pipeline)
    
    #plots the results to identify clusters of geographic interest for this user
    #uses Basemap from mpl_toolkit
    plot_locations(result, amenity, top_adder)

    