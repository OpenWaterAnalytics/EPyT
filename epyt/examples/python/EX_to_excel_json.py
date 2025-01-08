"""  Use/Save results in different formats/types and files.

   This example contains:
    Load a network.
    Run complete analysis.
    Display results in console.
    Create variables with the results:
        dict type.
        json obj as str type.
    Save results as:
        .json file: json obj, all results.
        .xlsx file: all results, each attribute in seperate sheet.
        .xlsx file: all results, in a single sheet.
        .xlsx file: selected results, each attribute in seperate sheet.
        .xlsx file: one selected result.
    Unload library.
    
"""
from epyt import epanet
# Load network 
d = epanet("Net1.inp")


# Run complete analysis 
comp_values = d.getComputedTimeSeries()

# Display all values
comp_values.disp()

""" -------------------  dict ---------------------------- """
# Create a dict type with all the values
to_dict_values = comp_values.to_dict()

""" -------------------  json ---------------------------- """
# Create a str with all the values in json format
to_json_values = comp_values.to_json()

# Create a .json file containing all the values
comp_values.to_json("to_json_values_example")

""" -------------------  excel ---------------------------- """
# Create a .xlsx excel file and save all the values of each attribute
# in seperate sheet
# comp_values.to_excel("to_excel_seperate_values_example")

# Create a .xlsx excel file and save all the values in a sheet
# comp_values.to_excel("to_excel_all_values_example", allValues=True)

# Create a .xlsx excel file and select multiple attributes to be 
# displayed in seperate sheets
selected_attributes = ["Pressure", "Flow", "LinkQuality"]
comp_values.to_excel(f"to_excel_{selected_attributes}_example",
                     attributes=selected_attributes)

# Create a .xlsx excel file and select a specific attribute to be displayed 
selected_attribute = "Pressure"
comp_values.to_excel(f"to_excel_{selected_attribute}_example",
                     attributes=selected_attribute)

# Retrieve node and link IDs from the network
nodeid = d.getNodeNameID()
linkid = d.getLinkNameID()

# Below are four example scenarios demonstrating how to use comp_values.to_excel()
# with different parameter configurations:

# 1) Scenario 1: Include both index and node/link IDs in the output.
comp_values.to_excel("case1", node_id_list=nodeid, link_id_list=linkid, both=True)

# 2) Scenario 2: Include only node/link IDs (no index).
comp_values.to_excel("case2", node_id_list=nodeid, link_id_list=linkid, both=False)

# 3) Scenario 3: Use the default settings (only index is included).
comp_values.to_excel("case3")

# 4) Scenario 4: Use the default settings but suppress the column headers.
comp_values.to_excel("case4", header=False)

# Unload library
d.unload()
