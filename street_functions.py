# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:41:39 2015

@author: Aaron Foss
"""


#list of acceptable street suffixes
expected = ["Street", "East","Row","Highway", "Run", "North", "South", "West", "Avenue", "Boulevard","Broadway", "Drive", "Court", "Circle", "Plaza", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Point", "Terrace", "Loop", "Mall", "Crescent" ]

#dictionary of common fixes to street names
mapping = { "St": "Street",
            "St.": "Street",
            "st": "Street",
            "st.": "Street",            
            "Rd": "Road",
            "Rd.": "Road",
            "rd": "Road",
            "rd.": "Road",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "ave": "Avenue",
            "ave.": "Avenue",
            "Av" : "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "blvd": "Boulevard",
            "blvd.": "Boulevard",
            "Dr": "Drive",
            "Dr.": "Drive",
            "dr": "Drive",
            "dr.": "Drive",
            "Ct": "Court",
            "Ct.": "Court",
            "ct": "Court",
            "ct.": "Court",
            "Cir": "Circle",
            "Pkwy": "Parkway",
            "Pky": "Parkway",
            "Pl": "Place",
            "Streer": "Street",
            "Strret": "Street",
            "Mainstreet": "Main Street",
            "S": "South",            
            "S.": "South",
            "N": "North",            
            "N.": "North",
            "W": "West",            
            "W.": "West",
            "w.": "West",
            "w": "West",
            "E": "East",            
            "E.": "East",
            "CO": "Colorado",
            "Ln" : "Lane",
            "Ste" : "Suite",
            "Ste" : "Suite",
            "Suit" : "Suite",
            'Mt.': 'Mount',
            'US': 'United States',
            'STreet' : 'Street',
            'Jr' : 'Junior',
            }

#dictionary of one-off repairs to street names
one_off_ways = {
                "Colfax": "Colfax Avenue",
                u'E 88th': 'East 88th Street',
                "Elm": "Elm Avenue",
                'Sheridan Boulevard B' : 'Sheridan Boulevard',
                'East Colfax' : 'East Colfax Avenue',
                "East Elm": "East Elm Avenue",
                "Main": "Main Street",
                "East Bromley Lane (152nd Avenue)": "East Bromley Lane",
                "Baseline" : "Baseline Road",
                "Baselin" : "Baseline Road",
                "Copper Canyon" : "Copper Canyon Road",
                "E Orchard Rd Bike Lane WB" : "East Orchard Road Bike Lane",
                'Hwy 74' : 'Highway 74',
                'Hwy 73' : 'Highway 73',
                'CO HWY 8' : 'State Highway 8',
                'Colorado SH 2' : 'State Highway 2',
                'Colorado SR 2' : 'State Road 2',
                'SR 2' : 'State Road 2',
                'Santa Fe Drive, Unit #850': 'Santa Fe Drive Unit 850',
                'Via Appia': 'Via Appia Way',
                'Arapahoe': 'Arapahoe Road',
                'Boulder': 'Boulder Street',
                'Caria': 'Caria Drive',
                'Centennial': 'Centennial Road',
                'Cherryvale': 'Cherryvale Road',
                'Etna': 'Etna Court',
                'Grant': 'Grant Street',
                '128th Ave MUP': '128th Avenue',
                'Newland': 'Newland Street',
                'Pennsylvania': 'Pennsylvania Street',
                'Tennyson': 'Tennyson Street',
                'Arapahoe Roadaddr': 'Arapahoe Road',
                'Tilden': 'Tilden Street',
                'Valmont': 'Valmont Road',
                'Via Varra': 'Via Varra Road',
                'Walnut': 'Walnut Street',
                'Sheridan Boulevard 5B' : 'Sheridan Boulevard Unit 5B',
                'Lamar' : 'Lamar Street',
                'Leetsdale' : 'Leetsdale Drive',
                'Coal Mine' : 'Coal Mine Avenue',
                'Osage': 'Osage Street',
                'West Ute': 'West Ute Avenue',
                'Wadsworth': 'Wadsworth Boulevard',
                'Lincoln': 'Lincoln Street',
                'West 120 Avenue': 'West 120th Avenue',
                
                }

#checks against common types, if not found adds 'type' to a dictionary
def audit_street_type(street_types, street_name):
    import re
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

#matches streets to known one off problems for unresolvables
def update_one_offs(name, mapping):
    name = name.strip()    
    try:
       name = mapping[name]
    except:
       pass
    return name

#function to identify and strip addresses and unit numbers
def id_address(name):
    import re
    address = ''    
    try:
        int(name)
        address = name
        name = ''
        pass
    except:
        m = re.search(r'([0-9]+)\-(.){1,2}\b|(#[0-9]+)|^([0-9]+\b)',name)
        while m:
            pattern = m.group()        
            name = re.sub(pattern,'',name)
            name = name
            new_address = m.group()
            address = address + " " +new_address
            m = re.search(r'([0-9]+)\-(.){1,2}\b|(#[0-9]+)|([0-9]+\b)',name)
       
        address = re.sub('#','Unit ',address)
        address = re.sub("  |-", " ",address) 
    return name, address

#function to grab suite numbers and add to an additional address variable that gets
# concatenated with the housenumber
def get_suite(name,i):
    import zipcode_functions
    name[i] = name[i].upper()
    additional_address = zipcode_functions.reassemble_name(name[i-1:i+1])
    name = name[:i-1] + name[i+1:]
    return name, additional_address               

#removes elements with the city and state in the name list    
def remove_city_state(name, state_name):
    if name == []:
        pass
    elif name[len(name)-1] == state_name:
        name = name[:len(name)-2]
    else:
        pass
    return name    
    
#update name maps over abbrieviated and other name issues to new names
#additionally separates Unit/Suit/Building information so that it can
#be more appropriately added to the street address
def update_name(name, mapping):
    import re
    import zipcode_functions
    name = re.sub('(\.)|(,)','',name)    
    name = re.findall(r'(\S+)',name)
    additional_address = ''
    
    for i in range(0,len(name)):
        
        m = re.search(r'^([a-z]|_)*$', name[i])
        if m:
            name[i] = name[i].title()
        del m
        if i > 0:
            m = re.search('Unit$|Suite$|Building$',name[i-1])
            if m:
                name, additional_address = get_suite(name,i)                
                break
            else:
                pass
        try:
            name[i] = mapping[name[i]]
        except:
            pass
    name = remove_city_state(name,'Colorado')
    new = zipcode_functions.reassemble_name(name)
      
    return new, additional_address
    
#audits street data, builds dictionary of existing streets, 
#then, if necessary adds a new street name, postcode information
#and additional addresses; simultaneously builds a list of unresolvable
#street names for additional digging        
def audit_streets(street_list):
    import re
    import collections
    import zipcode_functions
    street_types = collections.defaultdict(set)
    street_names = {}
    for street in street_list:
        if street != '' and len(street)>3:
           new = update_one_offs(street, one_off_ways)
           new = re.sub(':|;|,|\.',' ', new)             
           new, additional_address = update_name(new.strip(), mapping)
           new, zips = zipcode_functions.id_zipcode(new.strip())        
           new, address = id_address(new.strip())
            
           if new != street:        
                street_names[street] = {}
                street_names[street]['street'] = new.strip()
                if zips != '':
                    street_names[street]['postcode'] = zips.strip()
                if address != '' or additional_address != "":
                    new_address = address.strip() + ' ' + additional_address.strip()
                    street_names[street]['housenumber'] = new_address.strip() 
                
           audit_street_type(street_types, new)
            
        
    return street_types, street_names

#function to grab unique streets
def way_streets(db):    
    result = db.denver_boulder.distinct("address.street")
    return result
  
#function to update address entries with new street, housenumbers and zipcodes
def update_streets_db(old_street, street, houseno, zipcode, db):
        db.denver_boulder.update_many({'address.street' : old_street},{'$set': {'address.street': street,'address.housenumber': houseno, 'address.zipcode' : zipcode}})
        pass

#function to iteratively check address data and pass to update function    
def street_cleaner(entries_to_change, streets,db):
    import re
    for entry in entries_to_change:
        old_street = entry['address']['street']
        new_street = streets[old_street]['street']
        try:
            old_houseno = entry['address']['housenumber']
        except:
            old_houseno = ''
        try:
            new_houseno = old_houseno+' '+streets[old_street]['housenumber']
        except:
            new_houseno = old_houseno+' '+''
        try:
            old_zip = entry['address']['postcode']
        except:
            old_zip = ''
        try:
            if old_zip == '':        
                new_zip = old_zip+' '+streets[old_street]['postcode']
            else:
                new_zip = old_zip
        except:
            new_zip = old_zip+' '+''
        
        new_street = re.sub(str(old_zip.strip()), '', new_street.strip())
        new_street = re.sub(str(new_zip.strip()), '', new_street.strip())
        
        if old_street != new_street:
            update_streets_db(old_street,new_street.strip(),new_houseno.strip(), new_zip.strip(),db)      
 
