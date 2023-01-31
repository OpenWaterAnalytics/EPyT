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
comp_values.to_excel("to_excel_seperate_values_example")

# Create a .xlsx excel file and save all the values in a sheet
comp_values.to_excel("to_excel_all_values_example", allValues=True)

# Create a .xlsx excel file and select multiple attributes to be 
# displayed in seperate sheets
selected_attributes = ["Pressure", "Flow", "LinkQuality"]
comp_values.to_excel(f"to_excel_{selected_attributes}_example",
                     attributes=selected_attributes)

# Create a .xlsx excel file and select a specific attribute to be displayed 
selected_attribute = "Pressure"
comp_values.to_excel(f"to_excel_{selected_attribute}_example",
                     attributes=selected_attribute)

# Unload library
d.unload()
