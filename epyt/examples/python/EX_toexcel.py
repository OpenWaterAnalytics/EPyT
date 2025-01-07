from epyt import epanet

d = epanet("Net1.inp")
x = d.getComputedTimeSeries()

nodeid = d.getNodeNameID()
linkid = d.getLinkNameID()

x.to_excel("case1",node_id_list = nodeid, link_id_list = linkid, both = True) #index and ids
x.to_excel("case2",node_id_list = nodeid, link_id_list = linkid, both = False) #only id
x.to_excel("case3") #default case only index
x.to_excel("case4",header = False) #default case without headers
d.unload()