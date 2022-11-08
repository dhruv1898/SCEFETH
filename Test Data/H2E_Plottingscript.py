#from cmath import NaN
from cProfile import label
from cmath import nan
#from datetime import datetime
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import decimal as D


showgatewayplot = False
#####################################################################################################
#Read CSV files, assign columns and convert epoch time to datetime format (conversion of time only for Enddevices)

#Enddevice 1
dfe1 = pd.read_csv("E1/H2E/datalog_18_.csv",sep=':',header=None,engine="python")
dfe1.columns=['Time','Sendreceiveidentifier','Enddevice','Habitat_IP', 'Message','Packetnumber']
# dfe1 = dfe1.dropna(subset=['Packetnumber']).reset_index(drop=True)

#Enddevice 2
dfe2 = pd.read_csv("E2/H2E/datalog_4_.csv",sep=':',header=None,engine="python")
dfe2.columns=['Time','Sendreceiveidentifier','Enddevice','Habitat_IP', 'Message','Packetnumber']
# dfe2 = dfe2.dropna(subset=['Packetnumber']).reset_index(drop=True)


#Enddevice 3
dfe3 = pd.read_csv("E3/H2E/datalog_5_.csv",sep=':',header=None,engine="python")
dfe3.columns=['Time','Sendreceiveidentifier','Enddevice','Habitat_IP', 'Message','Packetnumber']
dfe3 = dfe3.dropna(subset=['Packetnumber']).reset_index(drop=True)

#Enddevice 4
dfe4 = pd.read_csv("E4/H2E/datalog_7_.csv",sep=':',header=None,engine="python")
dfe4.columns=['Time','Sendreceiveidentifier','Enddevice','Habitat_IP', 'Message','Packetnumber']
dfe4 = dfe4.dropna(subset=['Packetnumber']).reset_index(drop=True)


#Habitat
dfh = pd.read_csv("H/H2E/Multihop_data_(@H)_H2E_#5#.csv",sep='/',header=None)
dfh.columns=['Time','GatewayIP','Enddevice','Message','Packetnumber']
dfh = dfh.dropna(subset=['Packetnumber']).reset_index(drop=True)

#Gateway 3
dfg3 = pd.read_csv("G3/H2E/Multihop_data_(@G)_H2E_#4#.csv",sep='/',header=None)
dfg3.columns=['Time','Enddevice','Habitat_IP','Message','Packetnumber','H2G_G2E_Identifier']
# dfg3 = dfg3.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 4
# dfg4 = pd.read_csv("G4/H2E/Multihop_data_(@G)_H2E_#4#.csv",sep='/',header=None)
# dfg4.columns=['Time','Enddevice','Habitat_IP','Message','Packetnumber','H2G_G2E_Identifier']
# dfg4 = dfg4.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 5
dfg5 = pd.read_csv("G5/H2E/Multihop_data_(@G)_H2E_#5#.csv",sep='/',header=None)
dfg5.columns=['Time','Enddevice','Habitat_IP','Message','Packetnumber','H2G_G2E_Identifier']
# dfg5 = dfg5.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)
# print(dfg5.head())

#Gateway 6
dfg6 = pd.read_csv("G6/H2E/Multihop_data_(@G)_H2E_#4#.csv",sep='/',header=None)
dfg6.columns=['Time','Enddevice','Habitat_IP','Message','Packetnumber','H2G_G2E_Identifier']
# dfg6 = dfg6.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 7
# dfg7 = pd.read_csv("G7/H2E/Multihop_data_(@G)_H2E_#3#.csv",sep='/',header=None)
# dfg7.columns=['Time','Enddevice','Habitat_IP','Message','Packetnumber','H2G_G2E_Identifier']
# dfg7 = dfg7.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 8
dfg8 = pd.read_csv("G8/H2E/Multihop_data_(@G)_H2E_#4#.csv",sep='/',header=None)
dfg8.columns=['Time','Enddevice','Habitat_IP','Message','Packetnumber','H2G_G2E_Identifier']
# dfg8 = dfg8.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#####################################################################################################
# Calculating delay from H2E from Habitat to Gateway for each end-device
def calculate_delay(dfh,dfg,dfe,Enddeviceid,GatewayIP):
    # Enddevice 1
    dfh_e = dfh.loc[dfh['Enddevice'] == Enddeviceid]
    dfh_e_g = dfh_e.loc[dfh_e['GatewayIP'] == GatewayIP]
    dfh_e_g = dfh_e_g.reset_index(drop=True)
    dfg_e_h2g = dfg.loc[(dfg['Enddevice'] == Enddeviceid) & (dfg['H2G_G2E_Identifier'] == 'H2G')]
    dfg_e_h2g = dfg_e_h2g.reset_index(drop=True)
    dfg_e_g2e = dfg.loc[(dfg['Enddevice'] == Enddeviceid) & (dfg['H2G_G2E_Identifier'] == 'G2E')]
    dfg_e_g2e = dfg_e_g2e.reset_index(drop=True)
    df_e_g_delay_g2e = dfe['Time'] - dfg_e_g2e['Time']
    df_e_g_delay_h2g = dfg_e_h2g['Time'] - dfh_e_g['Time']
    df_e_g_delay_h2e = dfe['Time']-dfh_e_g['Time'] 
    df_e_g_delay_h2g_avg = round(np.mean(df_e_g_delay_h2g), 2)
    df_e_g_delay_g2e_avg = round(np.mean(df_e_g_delay_g2e), 2)
    df_e_g_delay_h2e_avg = round(np.mean(df_e_g_delay_h2e), 2)
    dfh_e_g['scatter'] = "Habitat"
    dfg_e_h2g['scatter'] = GatewayIP
    dfe_g2e = dfe
    dfe_g2e['scatter'] = Enddeviceid
    dfh2e_delratio = 1 - (len(dfh_e_g)-len(dfe))/len(dfh_e_g)
    return df_e_g_delay_h2g_avg, df_e_g_delay_g2e_avg, df_e_g_delay_h2e_avg, dfh_e_g, dfg_e_h2g, dfe_g2e, dfh2e_delratio
#####################################################################################################
# Plot delay results for each-device

def plot_delay_and_delratio(h2e_delay,h2g_delay,g2e_delay,h2e_delratio,Enddevices,Gateways):
    

    labels = ['ID001', 'ID002', 'ID003', 'ID004']
    x = np.arange(len(labels))  
    width = 0.11
    h2g = plt.bar(x - 2*width, h2g_delay,width,label="H2G",zorder=3)
    g2e = plt.bar(x, g2e_delay,width,label="G2E",zorder=3)
    h2e = plt.bar(x + 2*width, h2e_delay,width,label="H2E",zorder=3)
    plt.bar_label(h2g, padding=3, rotation = 0, fontsize=24)
    plt.bar_label(g2e, padding=3, rotation = 0, fontsize=24)
    plt.bar_label(h2e, padding=3, rotation = 0, fontsize=24)
    plt.semilogy()
    plt.xticks(x,labels,fontsize=26)
    plt.yticks(fontsize=26)
    plt.ylabel('Delay (in sec.)', fontsize=26)
    plt.xlabel('End-device', fontsize=26)
    plt.grid(which='both',linestyle='-',color='0.8')
    plt.legend(fontsize=26)
    plt.tight_layout()
    plt.show()
    plt.close()

    e1_h2g_delay = plt.bar(Gateways[0], h2g_delay[0],width,label=Enddevices[0])
    e2_h2g_delay = plt.bar(Gateways[1], h2g_delay[1],width,label=Enddevices[1])
    e3_h2g_delay = plt.bar(Gateways[2], h2g_delay[2],width,label=Enddevices[2])
    e4_h2g_delay = plt.bar(Gateways[3], h2g_delay[3],width,label=Enddevices[3])
    plt.bar_label(e1_h2g_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e2_h2g_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e3_h2g_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e4_h2g_delay, padding=3, rotation = 0, fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylabel('Delay (in sec.)', fontsize=20)
    plt.title('H2G average delay for all the End-devices', fontsize=20)
    plt.legend(fontsize=20)
    plt.show()
    plt.close()

    width = 0.3

    e1_g2e_delay = plt.bar(Gateways[0], g2e_delay[0],width,label=Enddevices[0])
    e2_g2e_delay = plt.bar(Gateways[1], g2e_delay[1],width,label=Enddevices[1])
    e3_g2e_delay = plt.bar(Gateways[2], g2e_delay[2],width,label=Enddevices[2])
    e4_g2e_delay = plt.bar(Gateways[3], g2e_delay[3],width,label=Enddevices[3])
    plt.bar_label(e1_g2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e2_g2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e3_g2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e4_g2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.ylabel('Delay (in sec.)', fontsize=20)
    plt.title('G2E average delay for all the End-devices', fontsize=20)
    plt.legend(fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()
    plt.close()

    e1_h2e_delay = plt.bar(Gateways[0], h2e_delay[0],width,label=Enddevices[0])
    e2_h2e_delay = plt.bar(Gateways[1], h2e_delay[1],width,label=Enddevices[1])
    e3_h2e_delay = plt.bar(Gateways[2], h2e_delay[2],width,label=Enddevices[2])
    e4_h2e_delay = plt.bar(Gateways[3], h2e_delay[3],width,label=Enddevices[3])
    plt.bar_label(e1_h2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e2_h2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e3_h2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.bar_label(e4_h2e_delay, padding=3, rotation = 0, fontsize=20)
    plt.ylabel('Delay (in sec.)', fontsize=20)
    plt.title('H2E average delay for all the End-devices', fontsize=20)
    plt.legend(fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()
    plt.close()

    e1_h2e_delratio = plt.bar(Gateways[0], h2e_delratio[0],width,label=Enddevices[0])
    e2_h2e_delratio = plt.bar(Gateways[1], h2e_delratio[1],width,label=Enddevices[1])
    e3_h2e_delratio = plt.bar(Gateways[2], h2e_delratio[2],width,label=Enddevices[2])
    e4_h2e_delratio = plt.bar(Gateways[3], h2e_delratio[3],width,label=Enddevices[3])
    plt.bar_label(e1_h2e_delratio, padding=3, rotation = 0, fontsize=26)
    plt.bar_label(e2_h2e_delratio, padding=3, rotation = 0, fontsize=26)
    plt.bar_label(e3_h2e_delratio, padding=3, rotation = 0, fontsize=26)
    plt.bar_label(e4_h2e_delratio, padding=3, rotation = 0, fontsize=26)
    # plt.title('Delivery Ratio for each end-device in H2E communication', fontsize=26)
    plt.legend(fontsize=26)
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)
    plt.show()
    plt.close()
#####################################################################################################
# Plot packets for all End-devices

def plot_packets(dfh_e1_g5, dfg5_e1_h2g, dfe1_g2e, dfh_e2_g6, dfg6_e2_h2g, dfe2_g2e, dfh_e3_g8, dfg8_e3_h2g, dfe3_g2e, dfh_e4_g3, dfg3_e4_h2g, dfe4_g2e):
    fig, axs = plt.subplots(4, sharex=True)
    labels_ID001 = ['H', 'G5', 'ID001']
    axs[0].plot(range(0, len(dfh_e1_g5['scatter'])),dfh_e1_g5['scatter'], '^--',markersize=10,color='blue',linewidth=3.0)
    axs[0].plot(range(0, len(dfg5_e1_h2g['scatter'])),dfg5_e1_h2g['scatter'], 'o--',markersize=10,color='blue',linewidth=3.0)
    axs[0].plot(range(0, len(dfe1_g2e['scatter'])),dfe1_g2e['scatter'], 'x--',markersize=10,color='blue',linewidth=3.0)
    # axs[0].legend(bbox_to_anchor=(0.68,0.94), fontsize=20)
    axs[0].set_yticklabels(labels_ID001,fontsize=20)

    labels_ID002 = ['H', 'G6', 'ID002']
    axs[1].plot(range(0, len(dfh_e2_g6['scatter'])),dfh_e2_g6['scatter'], '^--',markersize=10,color='green',linewidth=3.0)
    axs[1].plot(range(0, len(dfg6_e2_h2g['scatter'])),dfg6_e2_h2g['scatter'], 'o--',markersize=10,color='green',linewidth=3.0)
    axs[1].plot(range(0, len(dfe2_g2e['scatter'])),dfe2_g2e['scatter'], 'x--',markersize=10,color='green',linewidth=3.0)
    # axs[1].legend(bbox_to_anchor=(0.68,0.94), fontsize=20)
    axs[1].set_yticklabels(labels_ID002,fontsize=20)

    labels_ID003 = ['H', 'G8', 'ID003']
    axs[2].plot(range(0, len(dfh_e3_g8['scatter'])),dfh_e3_g8['scatter'], '^--',markersize=10,color='orange',linewidth=3.0)
    axs[2].plot(range(0, len(dfg8_e3_h2g['scatter'])),dfg8_e3_h2g['scatter'], 'o--',markersize=10,color='orange',linewidth=3.0)
    axs[2].plot(range(0, len(dfe3_g2e['scatter'])),dfe3_g2e['scatter'], 'x--',markersize=10,color='orange',linewidth=3.0)
    # axs[2].legend(bbox_to_anchor=(0.68,0.94), fontsize=20)
    axs[2].set_yticklabels(labels_ID003,fontsize=20)

    labels_ID004 = ['H', 'G3', 'ID004']
    axs[3].plot(range(0, len(dfh_e4_g3['scatter'])),dfh_e4_g3['scatter'], '^--',markersize=10,color='cyan',linewidth=3.0)
    axs[3].plot(range(0, len(dfg3_e4_h2g['scatter'])),dfg3_e4_h2g['scatter'], 'o--',markersize=10,color='cyan',linewidth=3.0)
    axs[3].plot(range(0, len(dfe4_g2e['scatter'])),dfe4_g2e['scatter'], 'x--',markersize=10,color='cyan',linewidth=3.0)
    # axs[3].legend(bbox_to_anchor=(0.68,0.94), fontsize=20)
    axs[3].set_yticklabels(labels_ID004,fontsize=20)

    fig.suptitle('Data packets received from the Habitat on different Gateway and the Enddevice',fontsize=20)

    plt.xlabel('Packet Number', fontsize=20)
    plt.xticks(fontsize=20)
    plt.show()
    plt.close()

#####################################################################################################
# Calculating delay from H2E from Habitat to Gateway for each end-device

# Enddevice 1
df_e1_g5_delay_h2g_avg, df_e1_g5_delay_g2e_avg, df_e1_g5_delay_h2e_avg, dfh_e1_g5, dfg5_e1_h2g, dfe1_g2e, dfh2e1_delratio = calculate_delay(dfh,dfg5,dfe1,"ID001","10.10.10.5")

# Enddevice 2
df_e2_g6_delay_h2g_avg, df_e2_g6_delay_g2e_avg, df_e2_g6_delay_h2e_avg, dfh_e2_g6, dfg6_e2_h2g, dfe2_g2e, dfh2e2_delratio = calculate_delay(dfh,dfg6,dfe2,"ID002","10.10.10.6")

# Enddevice 3
df_e3_g8_delay_h2g_avg, df_e3_g8_delay_g2e_avg, df_e3_g8_delay_h2e_avg, dfh_e3_g8, dfg8_e3_h2g, dfe3_g2e, dfh2e3_delratio = calculate_delay(dfh,dfg8,dfe3,"ID003","10.10.10.8")


# Enddevice 4
df_e4_g3_delay_h2g_avg, df_e4_g3_delay_g2e_avg, df_e4_g3_delay_h2e_avg, dfh_e4_g3, dfg3_e4_h2g, dfe4_g2e, dfh2e4_delratio = calculate_delay(dfh,dfg3,dfe4,"ID004","10.10.10.3")

h2e_delay = [df_e1_g5_delay_h2e_avg, df_e2_g6_delay_h2e_avg, df_e3_g8_delay_h2e_avg, df_e4_g3_delay_h2e_avg]
h2g_delay = [df_e1_g5_delay_h2g_avg, df_e2_g6_delay_h2g_avg, df_e3_g8_delay_h2g_avg, df_e4_g3_delay_h2g_avg]
g2e_delay = [df_e1_g5_delay_g2e_avg, df_e2_g6_delay_g2e_avg, df_e3_g8_delay_g2e_avg, df_e4_g3_delay_g2e_avg]
h2e_delratio = [dfh2e1_delratio, dfh2e2_delratio, dfh2e3_delratio, dfh2e4_delratio]
Enddevices = ["ID001", "ID002", "ID003", "ID004"]
Gateways = ["G5", "G6", "G8", "G3"]
plot_delay_and_delratio(h2e_delay,h2g_delay,g2e_delay,h2e_delratio,Enddevices,Gateways)
plot_packets(dfh_e1_g5, dfg5_e1_h2g, dfe1_g2e, dfh_e2_g6, dfg6_e2_h2g, dfe2_g2e, dfh_e3_g8, dfg8_e3_h2g, dfe3_g2e, dfh_e4_g3, dfg3_e4_h2g, dfe4_g2e)
# plt.bar(Enddevices,h2e_delratio, label=Enddevices)
# plt.title('Delivery Ratio for each end-device in H2E communication')
# plt.legend()
# plt.show()
# plt.close()

