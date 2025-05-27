from epyt import epanet



G = epanet("net2-cl2.inp")
G.loadMSXFile("net2-cl2.msx")
MSX_comp = G.getMSXComputedQualityNode()
G.exportMSXts(MSX_comp, "net2")
G.exportMSXstatistics("net2","summarynet2")


G.exportMSXts(
                MSX_comp,
                output_file="chlorine_subset.xlsx",
                selected_nodes=["10", "15"],
                selected_species=["CL2"]
            )


G.exportMSXts(
                MSX_comp,
                output_file="chlorine_subset1.xlsx",
                selected_nodes=[9, 14],
                selected_species=[0]
            )