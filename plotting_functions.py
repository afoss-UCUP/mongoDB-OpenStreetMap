# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 20:42:36 2015

@author: Aaron Foss
"""

def plot_update_frequency(result):    
    import pandas as pd
    import numpy
    
    #turns query results into timeseries of chnages
    d = []
    v = []
    for res in result:
        d.append(pd.Timestamp(res['_id']['timestamp']).to_datetime())
        v.append(res['count'])       
        
    ts = pd.DataFrame(v, index = d, columns = ['changes'])
    ts = ts.resample('W', how='sum')
    ts.index.names = ['date']

    import ggplot
    #plots timeseries of changes       
    p = ggplot.ggplot(ts, ggplot.aes(x = ts.index, y=ts['changes'])) +\
            ggplot.geom_point(color = 'blue') +\
            ggplot.xlab('Period') +\
            ggplot.ylab('Changes') +\
            ggplot.geom_smooth() +\
            ggplot.ylim(low = 0) +\
            ggplot.scale_x_date(breaks = ggplot.date_breaks("12 months"),  labels = ggplot.date_format('%Y-%m')) +\
            ggplot.ggtitle('OpenStreetMaps Denver-Boulder\nChanges per Week')
    return p

def plot_locations(result,amenity,top): 
    import pandas as pd
    import numpy
        
    lat = []
    lon = []
    for res in result:
        lat.append(res['pos'][0])
        lon.append(res['pos'][1])       
    
    geo = pd.DataFrame(lat, columns = ['lat'])
    geo['lon'] = lon
    
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
     
    my_map = Basemap(projection='merc', lat_0=geo.median()[0], lon_0=geo.median()[1],
        resolution = 'h', area_thresh = .1,
        llcrnrlon=geo.min()[1]-.1, llcrnrlat=geo.min()[0]-.1,
        urcrnrlon=geo.max()[1]+.1, urcrnrlat=geo.max()[0]+.1)
     
    my_map.drawrivers()
    my_map.drawcounties()
    my_map.fillcontinents(color='tan')
    my_map.drawmapboundary()
    my_map.drawcoastlines()
   
    x,y = my_map(lon, lat)
    my_map.plot(x,y, 'bo', markersize=2)
    
    title = 'Map Showing %s Added by \"%s\"\nThe Top %s Editor' % (str(amenity).title(),str(top),str(amenity).title())
    plt.title(title)
    p = plt.show()
    
    return p