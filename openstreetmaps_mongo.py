# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 13:46:59 2015

@author: Aaron Foss
"""

import json
import codecs
import re

#get mongo database
def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.openstreetmaps
    return db

#aggregate function for mongo queries
def aggregate(db, pipeline):
    result = db.denver_boulder.aggregate(pipeline)
    return result

#add denver_boulder line data from json
def insert_data(data, db):
    
    db.denver_boulder.insert(data)

    pass

#imports json documents iteratively from a file
def import_to_db(json_file):
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.openstreetmaps

    with open(json_file) as f:
        for line in f:
           data = json.loads(line)
           insert_data(data, db)

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#formats xml element to new data model
def shape_element(element):
    node = {}
    # builds our data structure
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        for item in element.iter('tag'):
            k = item.get('k')
            k = problemchars.sub("",k)
            
            if k in ['addr:housenumber','addr:postcode','addr:street']:
                #checks before building a new address dictionary
                if 'address' not in node.keys():
                    node['address'] = {}
                new = re.sub('addr:', '', k)
                node['address'][new] = item.get('v') 
            elif k in 'amenity':
                node[k] = item.get('v')
        if element.tag == 'way':
            #builds a new node ref list
            node['node_refs'] = []
            for item in element.iter('nd'):
                node['node_refs'].append(item.get('ref'))
        for k in element.keys():
            if k in CREATED:
                #checks before building a new address dictionary
                if 'created' not in node.keys():
                    node['created'] = {}
                node['created'][k] = element.get(k)
            elif k in 'lat':
                if 'pos' not in node.keys():
                    node['pos'] = [None,None]
                node['pos'][0] = float(element.get(k))
            elif k in 'lon':
                if 'pos' not in node.keys():
                    node['pos'] = [None,None]
                node['pos'][1] = float(element.get(k))
            else:
                node[k] = element.get(k)
               
        return node
    else:
        return None

#small argument added for memory constrained parsing,
#additionally cleans element tree
def process_map(file_in, pretty = False, small = True):
    import lxml.etree as ET
    file_out = "{0}.json".format(file_in)
    data = []
    context = ET.iterparse(file_in, events=('start','end'))
    _, root = context.next()
    with codecs.open(file_out, "w") as fo:
        for event, element in context:
            if event == "end":
                
                el = shape_element(element)
                root.clear()
                if el:
                    data.append(el)

                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
            
            
            if small:
                data = []
    return data



           