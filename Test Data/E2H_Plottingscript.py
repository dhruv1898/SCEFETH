#from cmath import NaN
from cmath import nan
#from datetime import datetime
import datetime
from re import X
from tkinter import Y
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


showplot = False
showgatewayplot = True
#####################################################################################################
#Read CSV files, assign columns and convert epoch time to datetime format (conversion of time only for Enddevices)

#Enddevice 1
dfe1 = pd.read_csv("E1/E2H/datalog_17_.csv",sep=':',header=None,engine="python")
dfe1.columns=['Time','Sendreceiveidentifier','Type','Enddevice','Temperature','Packetnumber']
dfe1 = dfe1.dropna(subset=['Packetnumber']).reset_index(drop=True)

#Enddevice 2
dfe2 = pd.read_csv("E2/E2H/datalog_3_.csv",sep=':',header=None,engine="python")
dfe2.columns=['Time','Sendreceiveidentifier','Type','Enddevice','Temperature','Packetnumber']
dfe2 = dfe2.dropna(subset=['Packetnumber']).reset_index(drop=True)

#Enddevice 3
dfe3 = pd.read_csv("E3/E2H/datalog_3_.csv",sep=':',header=None,engine="python")
dfe3.columns=['Time','Sendreceiveidentifier','Type','Enddevice','Temperature','Packetnumber']
dfe3 = dfe3.dropna(subset=['Packetnumber']).reset_index(drop=True)

#Enddevice 4
dfe4 = pd.read_csv("E4/E2H/datalog_5_.csv",sep=':',header=None,engine="python")
dfe4.columns=['Time','Sendreceiveidentifier','Type','Enddevice','Temperature','Packetnumber']
dfe4 = dfe4.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)
#dfe5['Datetime'] = pd.to_datetime(dfe5['Datetime'],unit='s')
#print('Enddeive 3 datetime: ',dfe3.head())


#Habitat
dfh = pd.read_csv("H/E2H/Multihop_data_(@H)_E2H_#2#.csv",sep='/',header=None)
dfh.columns=['Time','GatewayIP','Gatewayport','Enddevice','Temperature','Packetnumber']
dfh = dfh.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 3
dfg3 = pd.read_csv("G3/E2H/Multihop_data_(@G)_E2H_#2#.csv",sep='/',header=None)
dfg3.columns=['Time','Type','Enddevice','Rssi','Temperature','Packetnumber','E2G_G2H_Identifier']
dfg3 = dfg3.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 4
dfg4 = pd.read_csv("G4/E2H/Multihop_data_(@G)_E2H_#2#.csv",sep='/',header=None)
dfg4.columns=['Time','Type','Enddevice','Rssi','Temperature','Packetnumber','E2G_G2H_Identifier']
dfg4 = dfg4.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 5
# dfg5 = pd.read_csv("G5/E2H/Multihop_data_(@G)_E2H_#3#.csv",sep='/',header=None)
# dfg5.columns=['Time','Type','Enddevice','Rssi','Temperature','Packetnumber','E2G_G2H_Identifier']
# dfg5 = dfg5.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 6
dfg6 = pd.read_csv("G6/E2H/Multihop_data_(@G)_E2H_#2#.csv",sep='/',header=None)
dfg6.columns=['Time','Type','Enddevice','Rssi','Temperature','Packetnumber','E2G_G2H_Identifier']
dfg6 = dfg6.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 7
dfg7 = pd.read_csv("G7/E2H/Multihop_data_(@G)_E2H_#3#.csv",sep='/',header=None)
dfg7.columns=['Time','Type','Enddevice','Rssi','Temperature','Packetnumber','E2G_G2H_Identifier']
dfg7 = dfg7.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#Gateway 8
dfg8 = pd.read_csv("G8/E2H/Multihop_data_(@G)_E2H_#2#.csv",sep='/',header=None)
dfg8.columns=['Time','Type','Enddevice','Rssi','Temperature','Packetnumber','E2G_G2H_Identifier']
dfg8 = dfg8.dropna(subset=['Temperature','Packetnumber']).reset_index(drop=True)

#####################################################################################################

# def calculate_delay(dfg, dfh, dfe, EnddeviceID, GatewayIP):
#     print("Gateway: ",GatewayIP)
#     dfh_e = dfh.loc[dfh['Enddevice'] == EnddeviceID]
#     dfh_e = dfh_e.reset_index(drop=True)
#     dfh_e_g = dfh_e.loc[dfh_e['GatewayIP'] == GatewayIP]
#     dfh_e = dfh_e_g.reset_index(drop=True)
#     dfg_e_e2g = dfg.loc[(dfg3['Enddevice'] == EnddeviceID) & (dfg['E2G_G2H_Identifier'] == 'E2G')]
#     dfg_e_e2g = dfg_e_e2g.reset_index(drop=True)
#     dfg_e_e2g = dfg_e_e2g.drop(['Rssi', 'E2G_G2H_Identifier'],axis=1)
#     dfg_e_e2g = dfg_e_e2g.reset_index(drop=True)
#     dfe_e2h = dfe.drop(['Sendreceiveidentifier'],axis=1)
#     dfe_e2h = dfe_e2h.reset_index(drop=True)
#     dfe_e2h = [dfe_e2h,dfg_e_e2g]
#     dfe_e2h = pd.concat(dfe_e2h)
#     dfe_e2h = dfe_e2h[dfe_e2h.duplicated(subset=['Packetnumber'],keep=False)]
#     dfe_e2h = dfe_e2h.reset_index(drop=True)
#     dfe_e2h = dfe_e2h.drop_duplicates(subset=['Packetnumber'],keep='first')
#     dfe_e2h = dfe_e2h.reset_index(drop=True)
#     dfg_e_g2h = dfg.loc[(dfg['Enddevice'] == EnddeviceID) & (dfg['E2G_G2H_Identifier'] == 'G2H')]
#     dfg_e_g2h = dfg_e_g2h.reset_index(drop=True)

#     dfe2gdelay = dfg_e_e2g['Time']-dfe_e2h['Time']
#     dfg2hdelay = dfh_e['Time']-dfg_e_g2h['Time']
#     dfe2hdelay = dfh_e['Time']-dfe_e2h['Time']

#     return dfe2gdelay, dfg2hdelay, dfe2hdelay


#####################################################################################################

def calculate_delay(dfg, dfh, dfe, EnddeviceID, GatewayIP, Gatewayscatter_mul):
    print("Gateway: ",GatewayIP)
    dfh_e = dfh.loc[dfh['Enddevice'] == EnddeviceID]
    dfh_e = dfh_e.reset_index(drop=True)
    dfh_e = dfh_e.loc[dfh_e['GatewayIP'] == GatewayIP]
    dfh_e = dfh_e.reset_index(drop=True)
    dfh_e['scatter'] = 1
    dfg_e_e2g = dfg.loc[(dfg['Enddevice'] == EnddeviceID) & (dfg['E2G_G2H_Identifier'] == 'E2G')]
    dfg_e_e2g = dfg_e_e2g.reset_index(drop=True)
    dfg_e_e2g = dfg_e_e2g.drop(['Rssi', 'E2G_G2H_Identifier'],axis=1)
    dfg_e_e2g = dfg_e_e2g.reset_index(drop=True)
    dfg_e_e2g['scatter'] = Gatewayscatter_mul
    dfe_e2h = dfe.drop(['Sendreceiveidentifier'],axis=1)
    dfe_e2h = dfe_e2h.reset_index(drop=True)
    dfe_e2h['scatter'] = 1
    dfe_e2g_delratio = 1-(len(dfe_e2h) - len(dfg_e_e2g))/len(dfe_e2h)
    dfe_g_g2h_delratio = (len(dfh_e)/len(dfg_e_e2g))
    dfg_e_e2g_duplicate = [dfg_e_e2g, dfe_e2h]
    dfg_e_e2g_duplicate = pd.concat(dfg_e_e2g_duplicate)
    # dfg_e_e2g = dfg_e_e2g[dfg_e_e2g.duplicated(subset=['Packetnumber'],keep=False)]
    # dfg_e_e2g = dfg_e_e2g.reset_index(drop=True)
    dfg_e_e2g_duplicate = dfg_e_e2g_duplicate.drop_duplicates(subset=['Packetnumber'],keep=False)
    dfg_e_e2g_duplicate = dfg_e_e2g_duplicate.reset_index(drop=True)
    dfg_e_e2g_duplicate['Time'] = nan
    dfg_e_e2g = [dfg_e_e2g, dfg_e_e2g_duplicate]
    dfg_e_e2g = pd.concat(dfg_e_e2g)
    dfg_e_e2g = dfg_e_e2g.sort_values(by=['Packetnumber'])
    dfg_e_e2g = dfg_e_e2g.reset_index(drop=True)
    dfg_e_g2h = dfg.loc[(dfg['Enddevice'] == EnddeviceID) & (dfg['E2G_G2H_Identifier'] == 'G2H')]
    dfg_e_g2h = dfg_e_g2h.reset_index(drop=True)
    dfg_e_g2h_duplicate = [dfg_e_g2h, dfe_e2h]
    dfg_e_g2h_duplicate = pd.concat(dfg_e_g2h_duplicate)
    # dfg_e_g2h = dfg_e_g2h[dfg_e_g2h.duplicated(subset=['Packetnumber'],keep=False)]
    # dfg_e_g2h = dfg_e_g2h.reset_index(drop=True)
    dfg_e_g2h_duplicate = dfg_e_g2h_duplicate.drop_duplicates(subset=['Packetnumber'],keep=False)
    dfg_e_g2h_duplicate = dfg_e_g2h_duplicate.reset_index(drop=True)
    dfg_e_g2h_duplicate['Time'] = nan
    dfg_e_g2h = [dfg_e_g2h, dfg_e_g2h_duplicate]
    dfg_e_g2h = pd.concat(dfg_e_g2h)
    dfg_e_g2h = dfg_e_g2h.sort_values(by=['Packetnumber'])
    dfg_e_g2h = dfg_e_g2h.reset_index(drop=True)
    dfh_e = [dfh_e, dfg_e_g2h_duplicate]
    dfh_e = pd.concat(dfh_e)
    dfh_e = dfh_e.sort_values(by=['Packetnumber'])
    dfh_e = dfh_e.reset_index(drop=True)

    dfh_e.loc[dfh_e['Time'] == nan, 'scatter'] = nan
    dfg_e_e2g.loc[dfg_e_e2g['Time'] == nan, 'scatter'] = nan
    dfg_e_e2g.loc[dfg_e_e2g['scatter'] == 1, 'scatter'] = nan


    dfe2gdelay = dfg_e_e2g['Time']-dfe_e2h['Time']
    dfg2hdelay = dfh_e['Time']-dfg_e_g2h['Time']
    dfe2hdelay = dfh_e['Time']-dfe_e2h['Time']
    # dfe2hdelay = dfe2gdelay-dfg2hdelay
    dfe2gdelay_avg = abs(round(np.mean(dfe2gdelay), 2))
    dfg2hdelay_avg = round(np.mean(dfg2hdelay), 2)
    dfe2hdelay_avg = round(np.mean(dfe2hdelay), 2)

    dfe_plot = dfe
    dfe_plot['scatter'] = 1
    dfh_e_plot = dfh.loc[dfh['Enddevice']==EnddeviceID]
    dfh_e_plot = dfh_e_plot.drop_duplicates(subset=['Packetnumber'], keep= 'first')
    dfh_e_plot = dfh_e_plot.reset_index(drop=True)
    dfh_e_plot['scatter'] = 1
    dfh_e_duplicate = [dfh_e_plot, dfe_plot]
    dfh_e_duplicate = pd.concat(dfh_e_duplicate)
    dfh_e_duplicate = dfh_e_duplicate.drop_duplicates(subset=['Packetnumber'], keep=False)
    dfh_e_duplicate = dfh_e_duplicate.reset_index(drop=True)
    dfh_e_duplicate['scatter'] = nan

    dfh_e_plot = [dfh_e_plot, dfh_e_duplicate]
    dfh_e_plot = pd.concat(dfh_e_plot)
    dfh_e_plot = dfh_e_plot.reset_index(drop=True)
    dfh_e_plot = dfh_e_plot.sort_values(by=['Packetnumber'])
    dfh_e_plot = dfh_e_plot.reset_index(drop=True)
    dfh_e2h_delratio = dfh.loc[dfh['Enddevice'] == EnddeviceID]
    dfh_e2h_delratio = dfh_e2h_delratio.drop_duplicates(subset=['Packetnumber'], keep= 'first')
    dfh_e2h_delratio = dfh_e2h_delratio.reset_index(drop=True)
    dfh_e2h_delratio = round(len(dfh_e2h_delratio)/len(dfe), 2)

    return dfe2gdelay, dfg2hdelay, dfe2hdelay, dfe2gdelay_avg, dfg2hdelay_avg, dfe2hdelay_avg, dfe_e2g_delratio, dfh_e_plot, dfg_e_e2g, dfe_e2h, dfh_e2h_delratio, dfe_g_g2h_delratio


#####################################################################################################



def plot_results(EnddeviceID,dfeg3e2gdelay, dfeg4e2gdelay, dfeg6e2gdelay, dfeg7e2gdelay, dfeg8e2gdelay,
                dfeg3g2hdelay, dfeg4g2hdelay, dfeg6g2hdelay, dfeg7g2hdelay, dfeg8g2hdelay,
                dfeg3e2hdelay, dfeg4e2hdelay, dfeg6e2hdelay, dfeg7e2hdelay, dfeg8e2hdelay):
    
    fig, axs = plt.subplots(3)
    axs[0].plot(np.arange(0,len(dfeg3e2gdelay),1),dfeg3e2gdelay, label='10.10.10.3')
    axs[0].plot(np.arange(0,len(dfeg4e2gdelay),1),dfeg4e2gdelay, label='10.10.10.4')
    # axs[0].plot(np.arange(0,len(dfeg5e2gdelay),1),dfeg5e2gdelay, label='10.10.10.5')
    axs[0].plot(np.arange(0,len(dfeg6e2gdelay),1),dfeg6e2gdelay, label='10.10.10.6')
    axs[0].plot(np.arange(0,len(dfeg7e2gdelay),1),dfeg7e2gdelay, label='10.10.10.7')
    axs[0].plot(np.arange(0,len(dfeg8e2gdelay),1),dfeg8e2gdelay, label='10.10.10.8')
    axs[0].set_title('E2G delay plot for End-device:'+EnddeviceID)
    axs[0].set_xlabel('Packetnumber')
    axs[0].set_ylabel('Delay (in sec.)')
    axs[0].legend()

    axs[1].plot(np.arange(0,len(dfeg3g2hdelay),1),dfeg3g2hdelay, label='10.10.10.3')
    axs[1].plot(np.arange(0,len(dfeg4g2hdelay),1),dfeg4g2hdelay, label='10.10.10.4')
    # axs[1].plot(np.arange(0,len(dfeg5ghgdelay),1),dfeg5g2hdelay, label='10.10.10.5')
    axs[1].plot(np.arange(0,len(dfeg6g2hdelay),1),dfeg6g2hdelay, label='10.10.10.6')
    axs[1].plot(np.arange(0,len(dfeg7g2hdelay),1),dfeg7g2hdelay, label='10.10.10.7')
    axs[1].plot(np.arange(0,len(dfeg8g2hdelay),1),dfeg8g2hdelay, label='10.10.10.8')
    axs[1].set_title('G2H delay plot for End-device:'+EnddeviceID)
    axs[1].set_xlabel('Packetnumber')
    axs[1].set_ylabel('Delay (in sec.)')
    axs[1].legend()
    
    axs[2].plot(np.arange(0,len(dfeg3e2hdelay),1),dfeg3e2hdelay, label='10.10.10.3')
    axs[2].plot(np.arange(0,len(dfeg4e2hdelay),1),dfeg4e2hdelay, label='10.10.10.4')
    # axs[2].plot(np.arange(0,len(dfeg5ehgdelay),1),dfeg5e2hdelay, label='10.10.10.5')
    axs[2].plot(np.arange(0,len(dfeg6e2hdelay),1),dfeg6e2hdelay, label='10.10.10.6')
    axs[2].plot(np.arange(0,len(dfeg7e2hdelay),1),dfeg7e2hdelay, label='10.10.10.7')
    axs[2].plot(np.arange(0,len(dfeg8e2hdelay),1),dfeg8e2hdelay, label='10.10.10.8')
    axs[2].set_title('E2H delay plot for End-device:'+EnddeviceID)
    axs[2].set_xlabel('Packetnumber')
    axs[2].set_ylabel('Delay (in sec.)')
    axs[2].legend()

    # plt.show()
    # plt.close()

#####################################################################################################
def plot_results_avgdelay(enddevice_id, e2h_avgdelay_e1, e2h_avgdelay_e2, e2h_avgdelay_e3, e2h_avgdelay_e4,
                            g2h_avgdelay_e1, g2h_avgdelay_e2, g2h_avgdelay_e3, g2h_avgdelay_e4,
                            e2g_avgdelay_e1, e2g_avgdelay_e2, e2g_avgdelay_e3, e2g_avgdelay_e4,
                            e1_e2g_delratio, e2_e2g_delratio, e3_e2g_delratio, e4_e2g_delratio, h2e_delratio,
                            e1_g2h_delratio, e2_g2h_delratio, e3_g2h_delratio, e4_g2h_delratio):

    labels = ['G3', 'G4', 'G6', 'G7', 'G8']
    x = np.arange(len(labels))  
    width = 0.1
    # fig, ax = plt.subplots()
    e1_e2h_delay = plt.bar(x - 1.5*width,e2h_avgdelay_e1, width, label=enddevice_id[0])
    e2_e2h_delay = plt.bar(x - width/2,e2h_avgdelay_e2, width, label=enddevice_id[1])
    e3_e2h_delay = plt.bar(x + width/2,e2h_avgdelay_e3, width, label=enddevice_id[2])
    e4_e2h_delay = plt.bar(x + 1.5* width,e2h_avgdelay_e4, width, label=enddevice_id[3])
    plt.bar_label(e1_e2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e2_e2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e3_e2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e4_e2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.ylabel('Delay (in sec.)', fontsize=20)
    plt.title('E2H average delay for all the End-devices', fontsize=20)
    plt.xticks(x, labels, fontsize=20)
    plt.ylim(0,26)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20,bbox_to_anchor=(0.68,1))
    plt.tight_layout()
    plt.show()
    plt.close()



    e1_e2g_delay = plt.bar(x - 1.5*width,e2g_avgdelay_e1, width, label=enddevice_id[0])
    e2_e2g_delay = plt.bar(x - width/2,e2g_avgdelay_e2, width, label=enddevice_id[1])
    e3_e2g_delay = plt.bar(x + width/2,e2g_avgdelay_e3, width, label=enddevice_id[2])
    e4_e2g_delay = plt.bar(x + 1.5* width,e2g_avgdelay_e4, width, label=enddevice_id[3])
    plt.bar_label(e1_e2g_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e2_e2g_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e3_e2g_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e4_e2g_delay, padding=3, rotation = 90, fontsize=20)
    plt.ylabel('Delay (in sec.)', fontsize=20)
    plt.title('E2G average delay for all the End-devices', fontsize=20)
    plt.xticks(x, labels, fontsize=20)
    plt.ylim(0,0.43)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20,bbox_to_anchor=(0.68,1))
    plt.tight_layout()
    plt.show()
    plt.close()


    e1_g2h_delay = plt.bar(x - 1.5*width,g2h_avgdelay_e1, width, label=enddevice_id[0])
    e2_g2h_delay = plt.bar(x - width/2,g2h_avgdelay_e2, width, label=enddevice_id[1])
    e3_g2h_delay = plt.bar(x + width/2,g2h_avgdelay_e3, width, label=enddevice_id[2])
    e4_g2h_delay = plt.bar(x + 1.5* width,g2h_avgdelay_e4, width, label=enddevice_id[3])
    plt.bar_label(e1_g2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e2_g2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e3_g2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(e4_g2h_delay, padding=3, rotation = 90, fontsize=20)
    plt.ylabel('Delay (in sec.)', fontsize=20)
    plt.title('G2H average delay for all the End-devices', fontsize=20)
    plt.xticks(x, labels, fontsize=20)
    plt.ylim(0,14)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20,bbox_to_anchor=(0.68,1))
    plt.tight_layout()
    plt.show()
    plt.close()

    plt.plot(x,e1_e2g_delratio, 'o--', markersize=10, label=enddevice_id[0],linewidth=3.0)
    plt.plot(x,e2_e2g_delratio, 'v--', markersize=10, label=enddevice_id[1],linewidth=3.0)
    plt.plot(x,e3_e2g_delratio, '^--', markersize=10, label=enddevice_id[2],linewidth=3.0)
    plt.plot(x,e4_e2g_delratio, '*--', markersize=10, label=enddevice_id[3],linewidth=3.0)
    plt.title('Delivery Ratio for E2G communication for all the End-devices and Gateways', fontsize=20)
    plt.xticks(x, labels, fontsize=20)
    plt.ylim(0,1)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.grid()
    plt.tight_layout()
    plt.show()
    plt.close()

    plt.plot(x,e1_g2h_delratio, 'o--', markersize=10, label=enddevice_id[0],linewidth=3.0)
    plt.plot(x,e2_g2h_delratio, 'v--', markersize=10, label=enddevice_id[1],linewidth=3.0)
    plt.plot(x,e3_g2h_delratio, '^--', markersize=10, label=enddevice_id[2],linewidth=3.0)
    plt.plot(x,e4_g2h_delratio, '*--', markersize=10, label=enddevice_id[3],linewidth=3.0)
    plt.title('Delivery Ratio for G2H communication for all the End-devices and Gateways', fontsize=20)
    plt.xticks(x, labels, fontsize=20)
    plt.ylim(0,1.1)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.grid()
    plt.tight_layout()
    plt.show()
    plt.close()

    h2e_e1_delratio = plt.bar(enddevice_id[0],h2e_delratio[0], width=0.3, label=enddevice_id[0])
    h2e_e2_delratio = plt.bar(enddevice_id[1],h2e_delratio[1], width=0.3, label=enddevice_id[1])
    h2e_e3_delratio = plt.bar(enddevice_id[2],h2e_delratio[2], width=0.3, label=enddevice_id[2])
    h2e_e4_delratio = plt.bar(enddevice_id[3],h2e_delratio[3], width=0.3, label=enddevice_id[3])
    plt.bar_label(h2e_e1_delratio, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(h2e_e2_delratio, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(h2e_e3_delratio, padding=3, rotation = 90, fontsize=20)
    plt.bar_label(h2e_e4_delratio, padding=3, rotation = 90, fontsize=20)
    plt.title('Delivery Ratio for E2H communication for all the End-devices',fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.tight_layout()
    plt.show()
    plt.close()

#####################################################################################################

# Plotting scatter plot for showing missing packets

def plot_scatter(dfh_e1, dfg_e1g3_e2g, dfg_e1g4_e2g, dfg_e1g6_e2g, dfg_e1g7_e2g, dfg_e1g8_e2g, dfe1_e2h,
                dfh_e2, dfg_e2g3_e2g, dfg_e2g4_e2g, dfg_e2g6_e2g, dfg_e2g7_e2g, dfg_e2g8_e2g, dfe2_e2h,
                dfh_e3, dfg_e3g3_e2g, dfg_e3g4_e2g, dfg_e3g6_e2g, dfg_e3g7_e2g, dfg_e3g8_e2g, dfe3_e2h,
                dfh_e4, dfg_e4g3_e2g, dfg_e4g4_e2g, dfg_e4g6_e2g, dfg_e4g7_e2g, dfg_e4g8_e2g, dfe4_e2h):


    labels = ['G3', 'G4', 'G5', 'G6', 'G7', 'G8']
    y = range(3,3+len(labels))
    fig, axs = plt.subplots(3, sharex=True, gridspec_kw={'hspace': 0})
    axs[0].plot(range(0, len(dfe1_e2h['scatter'])),dfe1_e2h['scatter'], 'p--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e1g3_e2g['scatter'])),dfg_e1g3_e2g['scatter'], 'o--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e1g4_e2g['scatter'])),dfg_e1g4_e2g['scatter'], 'v--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e1g6_e2g['scatter'])),dfg_e1g6_e2g['scatter'], '*--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e1g7_e2g['scatter'])),dfg_e1g7_e2g['scatter'], '^--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e1g8_e2g['scatter'])),dfg_e1g8_e2g['scatter'], 's--',markersize=10,linewidth=3.0)
    axs[2].plot(range(0, len(dfh_e1['scatter'])),dfh_e1['scatter'], 'x--',markersize=10,linewidth=3.0)
    axs[0].yaxis.set_ticklabels([])
    axs[2].yaxis.set_ticklabels([])
    plt.xlabel("Packet number",fontsize=20)
    plt.xticks(fontsize=20)
    axs[0].set_ylabel("ID001",fontsize=20)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels(labels,fontsize=20)
    axs[2].set_ylabel("H",fontsize=20)
    fig.suptitle('Data packets received from ID001 on different Gateways and the Habitat',fontsize=20)
    plt.show()
    plt.close()

    fig, axs = plt.subplots(3, sharex=True, gridspec_kw={'hspace': 0})
    axs[0].plot(range(0, len(dfe2_e2h['scatter'])),dfe2_e2h['scatter'], 'p--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e2g3_e2g['scatter'])),dfg_e2g3_e2g['scatter'], 'o--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e2g4_e2g['scatter'])),dfg_e2g4_e2g['scatter'], 'v--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e2g6_e2g['scatter'])),dfg_e2g6_e2g['scatter'], '*--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e2g7_e2g['scatter'])),dfg_e2g7_e2g['scatter'], '^--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e2g8_e2g['scatter'])),dfg_e2g8_e2g['scatter'], 's--',markersize=10,linewidth=3.0)
    axs[2].plot(range(0, len(dfh_e2['scatter'])),dfh_e2['scatter'], 'x--',markersize=10,linewidth=3.0)
    axs[0].yaxis.set_ticklabels([])
    axs[2].yaxis.set_ticklabels([])
    plt.xlabel("Packet number",fontsize=20)
    plt.xticks(fontsize=20)
    axs[0].set_ylabel("ID002",fontsize=20)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels(labels,fontsize=20)
    axs[2].set_ylabel("Habitat",fontsize=20)
    fig.suptitle('Data packets received from ID002 on different Gateways and the Habitat',fontsize=20)
    plt.show()
    plt.close()

    fig, axs = plt.subplots(3, sharex=True, gridspec_kw={'hspace': 0})
    axs[0].plot(range(0, len(dfe3_e2h['scatter'])),dfe3_e2h['scatter'], 'p--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e3g3_e2g['scatter'])),dfg_e3g3_e2g['scatter'], 'o--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e3g4_e2g['scatter'])),dfg_e3g4_e2g['scatter'], 'v--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e3g6_e2g['scatter'])),dfg_e3g6_e2g['scatter'], '*--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e3g7_e2g['scatter'])),dfg_e3g7_e2g['scatter'], '^--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e3g8_e2g['scatter'])),dfg_e3g8_e2g['scatter'], 's--',markersize=10,linewidth=3.0)
    axs[2].plot(range(0, len(dfh_e3['scatter'])),dfh_e3['scatter'], 'x--',markersize=10,linewidth=3.0)
    axs[0].yaxis.set_ticklabels([])
    axs[2].yaxis.set_ticklabels([])
    plt.xlabel("Packet number",fontsize=20)
    plt.xticks(fontsize=20)
    axs[0].set_ylabel("ID003",fontsize=20)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels(labels,fontsize=20)
    axs[2].set_ylabel("H",fontsize=20)
    fig.suptitle('Data packets received from ID003 on different Gateways and the Habitat',fontsize=20)
    plt.show()
    plt.close()

    fig, axs = plt.subplots(3, sharex=True, gridspec_kw={'hspace': 0})
    axs[0].plot(range(0, len(dfe4_e2h['scatter'])),dfe4_e2h['scatter'], 'p--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e4g3_e2g['scatter'])),dfg_e4g3_e2g['scatter'], 'o--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e4g4_e2g['scatter'])),dfg_e4g4_e2g['scatter'], 'v--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e4g6_e2g['scatter'])),dfg_e4g6_e2g['scatter'], '*--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e4g7_e2g['scatter'])),dfg_e4g7_e2g['scatter'], '^--',markersize=10,linewidth=3.0)
    axs[1].plot(range(0, len(dfg_e4g8_e2g['scatter'])),dfg_e4g8_e2g['scatter'], 's--',markersize=10,linewidth=3.0)
    axs[2].plot(range(0, len(dfh_e4['scatter'])),dfh_e4['scatter'], 'x--',markersize=10,linewidth=3.0)
    axs[0].yaxis.set_ticklabels([])
    axs[2].yaxis.set_ticklabels([])
    plt.xlabel("Packet number",fontsize=20)
    plt.xticks(fontsize=20)
    axs[0].set_ylabel("ID004",fontsize=20)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels(labels,fontsize=20)
    axs[2].set_ylabel("H",fontsize=20)
    fig.suptitle('Data packets received from ID004 on different Gateways and the Habitat',fontsize=20)
    plt.show()
    plt.close()

#####################################################################################################

#Plotting delays of each enddevice w.r.t. packet number

# End-device 1
dfe1g3e2gdelay, dfe1g3g2hdelay, dfe1g3e2hdelay, dfe1g3e2gdelay_avg, dfe1g3g2hdelay_avg, dfe1g3e2hdelay_avg, dfe1g3_e2g_delratio, dfh_e1, dfg_e1g3_e2g, dfe1_e2h, dfh_e1_delratio, dfe1_g3_g2h_delratio = calculate_delay(dfg3, dfh, dfe1, "ID001", "10.10.10.3", 3)
dfe1g4e2gdelay, dfe1g4g2hdelay, dfe1g4e2hdelay, dfe1g4e2gdelay_avg, dfe1g4g2hdelay_avg, dfe1g4e2hdelay_avg, dfe1g4_e2g_delratio, dfh_e1, dfg_e1g4_e2g, dfe1_e2h, dfh_e1_delratio, dfe1_g4_g2h_delratio = calculate_delay(dfg4, dfh, dfe1, "ID001", "10.10.10.4", 4)
# dfe1g5e2gdelay, dfe1g5g2hdelay, dfe1g5e2hdelay, dfe1g5e2gdelay_avg, dfe1g5g2hdelay_avg, dfe1g5e2hdelay_avg, dfe1g5_e2g_delratio, dfh_e1, dfg_e1g5_e2g, dfe1_e2h, dfh_e1_delratio, dfe1_g5_g2h_delratio = calculate_delay(dfg5, dfh, dfe1, "ID001", "10.10.10.5", 5)
dfe1g6e2gdelay, dfe1g6g2hdelay, dfe1g6e2hdelay, dfe1g6e2gdelay_avg, dfe1g6g2hdelay_avg, dfe1g6e2hdelay_avg, dfe1g6_e2g_delratio, dfh_e1, dfg_e1g6_e2g, dfe1_e2h, dfh_e1_delratio, dfe1_g6_g2h_delratio = calculate_delay(dfg6, dfh, dfe1, "ID001", "10.10.10.6", 6)
dfe1g7e2gdelay, dfe1g7g2hdelay, dfe1g7e2hdelay, dfe1g7e2gdelay_avg, dfe1g7g2hdelay_avg, dfe1g7e2hdelay_avg, dfe1g7_e2g_delratio, dfh_e1, dfg_e1g7_e2g, dfe1_e2h, dfh_e1_delratio, dfe1_g7_g2h_delratio = calculate_delay(dfg7, dfh, dfe1, "ID001", "10.10.10.7", 7)
dfe1g8e2gdelay, dfe1g8g2hdelay, dfe1g8e2hdelay, dfe1g8e2gdelay_avg, dfe1g8g2hdelay_avg, dfe1g8e2hdelay_avg, dfe1g8_e2g_delratio, dfh_e1, dfg_e1g8_e2g, dfe1_e2h, dfh_e1_delratio, dfe1_g8_g2h_delratio = calculate_delay(dfg8, dfh, dfe1, "ID001", "10.10.10.8", 8)

# End-device 2
dfe2g3e2gdelay, dfe2g3g2hdelay, dfe2g3e2hdelay, dfe2g3e2gdelay_avg, dfe2g3g2hdelay_avg, dfe2g3e2hdelay_avg, dfe2g3_e2g_delratio, dfh_e2, dfg_e2g3_e2g, dfe2_e2h, dfh_e2_delratio, dfe2_g3_g2h_delratio = calculate_delay(dfg3, dfh, dfe2, "ID002", "10.10.10.3", 3)
dfe2g4e2gdelay, dfe2g4g2hdelay, dfe2g4e2hdelay, dfe2g4e2gdelay_avg, dfe2g4g2hdelay_avg, dfe2g4e2hdelay_avg, dfe2g4_e2g_delratio, dfh_e2, dfg_e2g4_e2g, dfe2_e2h, dfh_e2_delratio, dfe2_g4_g2h_delratio = calculate_delay(dfg4, dfh, dfe2, "ID002", "10.10.10.4", 4)
# dfe2g5e2gdelay, dfe2g5g2hdelay, dfe2g5e2hdelay, dfe2g5e2gdelay_avg, dfe2g5g2hdelay_avg, dfe2g5e2hdelay_avg, dfe2g5_e2g_delratio, dfh_e2, dfg_e2g5_e2g, dfe2_e2h, dfh_e2_delratio, dfe2_g5_g2h_delratio = calculate_delay(dfg5, dfh, dfe2, "ID002", "10.10.10.5", 5)
dfe2g6e2gdelay, dfe2g6g2hdelay, dfe2g6e2hdelay, dfe2g6e2gdelay_avg, dfe2g6g2hdelay_avg, dfe2g6e2hdelay_avg, dfe2g6_e2g_delratio, dfh_e2, dfg_e2g6_e2g, dfe2_e2h, dfh_e2_delratio, dfe2_g6_g2h_delratio = calculate_delay(dfg6, dfh, dfe2, "ID002", "10.10.10.6", 6)
dfe2g7e2gdelay, dfe2g7g2hdelay, dfe2g7e2hdelay, dfe2g7e2gdelay_avg, dfe2g7g2hdelay_avg, dfe2g7e2hdelay_avg, dfe2g7_e2g_delratio, dfh_e2, dfg_e2g7_e2g, dfe2_e2h, dfh_e2_delratio, dfe2_g7_g2h_delratio = calculate_delay(dfg7, dfh, dfe2, "ID002", "10.10.10.7", 7)
dfe2g8e2gdelay, dfe2g8g2hdelay, dfe2g8e2hdelay, dfe2g8e2gdelay_avg, dfe2g8g2hdelay_avg, dfe2g8e2hdelay_avg, dfe2g8_e2g_delratio, dfh_e2, dfg_e2g8_e2g, dfe2_e2h, dfh_e2_delratio, dfe2_g8_g2h_delratio = calculate_delay(dfg8, dfh, dfe2, "ID002", "10.10.10.8", 8)

# End-device 3
dfe3g3e2gdelay, dfe3g3g2hdelay, dfe3g3e2hdelay, dfe3g3e2gdelay_avg, dfe3g3g2hdelay_avg, dfe3g3e2hdelay_avg, dfe3g3_e2g_delratio, dfh_e3, dfg_e3g3_e2g, dfe3_e2h, dfh_e3_delratio, dfe3_g3_g2h_delratio = calculate_delay(dfg3, dfh, dfe3, "ID003", "10.10.10.3", 3)
dfe3g4e2gdelay, dfe3g4g2hdelay, dfe3g4e2hdelay, dfe3g4e2gdelay_avg, dfe3g4g2hdelay_avg, dfe3g4e2hdelay_avg, dfe3g4_e2g_delratio, dfh_e3, dfg_e3g4_e2g, dfe3_e2h, dfh_e3_delratio, dfe3_g4_g2h_delratio = calculate_delay(dfg4, dfh, dfe3, "ID003", "10.10.10.4", 4)
# dfe3g5e2gdelay, dfe3g5g2hdelay, dfe3g5e2hdelay, dfe3g5e2gdelay_avg, dfe3g5g2hdelay_avg, dfe3g5e2hdelay_avg, dfe3g5_e2g_delratio, dfh_e3, dfg_e3g5_e2g, dfe3_e2h, dfh_e3_delratio, dfe3_g5_g2h_delratio = calculate_delay(dfg5, dfh, dfe3, "ID003", "10.10.10.5", 5)
dfe3g6e2gdelay, dfe3g6g2hdelay, dfe3g6e2hdelay, dfe3g6e2gdelay_avg, dfe3g6g2hdelay_avg, dfe3g6e2hdelay_avg, dfe3g6_e2g_delratio, dfh_e3, dfg_e3g6_e2g, dfe3_e2h, dfh_e3_delratio, dfe3_g6_g2h_delratio = calculate_delay(dfg6, dfh, dfe3, "ID003", "10.10.10.6", 6)
dfe3g7e2gdelay, dfe3g7g2hdelay, dfe3g7e2hdelay, dfe3g7e2gdelay_avg, dfe3g7g2hdelay_avg, dfe3g7e2hdelay_avg, dfe3g7_e2g_delratio, dfh_e3, dfg_e3g7_e2g, dfe3_e2h, dfh_e3_delratio, dfe3_g7_g2h_delratio = calculate_delay(dfg7, dfh, dfe3, "ID003", "10.10.10.7", 7)
dfe3g8e2gdelay, dfe3g8g2hdelay, dfe3g8e2hdelay, dfe3g8e2gdelay_avg, dfe3g8g2hdelay_avg, dfe3g8e2hdelay_avg, dfe3g8_e2g_delratio, dfh_e3, dfg_e3g8_e2g, dfe3_e2h, dfh_e3_delratio, dfe3_g8_g2h_delratio = calculate_delay(dfg8, dfh, dfe3, "ID003", "10.10.10.8", 8)

# End-device 4
dfe4g3e2gdelay, dfe4g3g2hdelay, dfe4g3e2hdelay, dfe4g3e2gdelay_avg, dfe4g3g2hdelay_avg, dfe4g3e2hdelay_avg, dfe4g3_e2g_delratio, dfh_e4, dfg_e4g3_e2g, dfe4_e2h, dfh_e4_delratio, dfe4_g3_g2h_delratio = calculate_delay(dfg3, dfh, dfe4, "ID004", "10.10.10.3", 3)
dfe4g4e2gdelay, dfe4g4g2hdelay, dfe4g4e2hdelay, dfe4g4e2gdelay_avg, dfe4g4g2hdelay_avg, dfe4g4e2hdelay_avg, dfe4g4_e2g_delratio, dfh_e4, dfg_e4g4_e2g, dfe4_e2h, dfh_e4_delratio, dfe4_g4_g2h_delratio = calculate_delay(dfg4, dfh, dfe4, "ID004", "10.10.10.4", 4)
# dfe4g5e2gdelay, dfe4g5g2hdelay, dfe4g5e2hdelay, dfe4g5e2gdelay_avg, dfe4g5g2hdelay_avg, dfe4g5e2hdelay_avg, dfe4g5_e2g_delratio, dfh_e4, dfg_e4g5_e2g, dfe4_e2h, dfh_e4_delratio, dfe4_g5_g2h_delratio = calculate_delay(dfg5, dfh, dfe4, "ID004", "10.10.10.5", 5)
dfe4g6e2gdelay, dfe4g6g2hdelay, dfe4g6e2hdelay, dfe4g6e2gdelay_avg, dfe4g6g2hdelay_avg, dfe4g6e2hdelay_avg, dfe4g6_e2g_delratio, dfh_e4, dfg_e4g6_e2g, dfe4_e2h, dfh_e4_delratio, dfe4_g6_g2h_delratio = calculate_delay(dfg6, dfh, dfe4, "ID004", "10.10.10.6", 6)
dfe4g7e2gdelay, dfe4g7g2hdelay, dfe4g7e2hdelay, dfe4g7e2gdelay_avg, dfe4g7g2hdelay_avg, dfe4g7e2hdelay_avg, dfe4g7_e2g_delratio, dfh_e4, dfg_e4g7_e2g, dfe4_e2h, dfh_e4_delratio, dfe4_g7_g2h_delratio = calculate_delay(dfg7, dfh, dfe4, "ID004", "10.10.10.7", 7)
dfe4g8e2gdelay, dfe4g8g2hdelay, dfe4g8e2hdelay, dfe4g8e2gdelay_avg, dfe4g8g2hdelay_avg, dfe4g8e2hdelay_avg, dfe4g8_e2g_delratio, dfh_e4, dfg_e4g8_e2g, dfe4_e2h, dfh_e4_delratio, dfe4_g8_g2h_delratio = calculate_delay(dfg8, dfh, dfe4, "ID004", "10.10.10.8", 8)



enddevice_id = ["ID001", "ID002", "ID003", "ID004"]
e2h_avgdelay_e1 = [dfe1g3e2hdelay_avg, dfe1g4e2hdelay_avg, dfe1g6e2hdelay_avg, dfe1g7e2hdelay_avg, dfe1g8e2hdelay_avg]
e2h_avgdelay_e2 = [dfe2g3e2hdelay_avg, dfe2g4e2hdelay_avg, dfe2g6e2hdelay_avg, dfe2g7e2hdelay_avg, dfe2g8e2hdelay_avg]
e2h_avgdelay_e3 = [dfe3g3e2hdelay_avg, dfe3g4e2hdelay_avg, dfe3g6e2hdelay_avg, dfe3g7e2hdelay_avg, dfe3g8e2hdelay_avg]
e2h_avgdelay_e4 = [dfe4g3e2hdelay_avg, dfe4g4e2hdelay_avg, dfe4g6e2hdelay_avg, dfe4g7e2hdelay_avg, dfe4g8e2hdelay_avg]

g2h_avgdelay_e1 = [dfe1g3g2hdelay_avg, dfe1g4g2hdelay_avg, dfe1g6g2hdelay_avg, dfe1g7g2hdelay_avg, dfe1g8g2hdelay_avg]
g2h_avgdelay_e2 = [dfe2g3g2hdelay_avg, dfe2g4g2hdelay_avg, dfe2g6g2hdelay_avg, dfe2g7g2hdelay_avg, dfe2g8g2hdelay_avg]
g2h_avgdelay_e3 = [dfe3g3g2hdelay_avg, dfe3g4g2hdelay_avg, dfe3g6g2hdelay_avg, dfe3g7g2hdelay_avg, dfe3g8g2hdelay_avg]
g2h_avgdelay_e4 = [dfe4g3g2hdelay_avg, dfe4g4g2hdelay_avg, dfe4g6g2hdelay_avg, dfe4g7g2hdelay_avg, dfe4g8g2hdelay_avg]


e2g_avgdelay_e1 = [dfe1g3e2gdelay_avg, dfe1g4e2gdelay_avg, dfe1g6e2gdelay_avg, dfe1g7e2gdelay_avg, dfe1g8e2gdelay_avg]
e2g_avgdelay_e2 = [dfe2g3e2gdelay_avg, dfe2g4e2gdelay_avg, dfe2g6e2gdelay_avg, dfe2g7e2gdelay_avg, dfe2g8e2gdelay_avg]
e2g_avgdelay_e3 = [dfe3g3e2gdelay_avg, dfe3g4e2gdelay_avg, dfe3g6e2gdelay_avg, dfe3g7e2gdelay_avg, dfe3g8e2gdelay_avg]
e2g_avgdelay_e4 = [dfe4g3e2gdelay_avg, dfe4g4e2gdelay_avg, dfe4g6e2gdelay_avg, dfe4g7e2gdelay_avg, dfe4g8e2gdelay_avg]


e1_e2g_delratio = [dfe1g3_e2g_delratio, dfe1g4_e2g_delratio, dfe1g6_e2g_delratio, dfe1g7_e2g_delratio, dfe1g8_e2g_delratio]
e2_e2g_delratio = [dfe2g3_e2g_delratio, dfe2g4_e2g_delratio, dfe2g6_e2g_delratio, dfe2g7_e2g_delratio, dfe2g8_e2g_delratio]
e3_e2g_delratio = [dfe3g3_e2g_delratio, dfe3g4_e2g_delratio, dfe3g6_e2g_delratio, dfe3g7_e2g_delratio, dfe3g8_e2g_delratio]
e4_e2g_delratio = [dfe4g3_e2g_delratio, dfe4g4_e2g_delratio, dfe4g6_e2g_delratio, dfe4g7_e2g_delratio, dfe4g8_e2g_delratio]

e1_g2h_delratio = [dfe1_g3_g2h_delratio, dfe1_g4_g2h_delratio, dfe1_g6_g2h_delratio, dfe1_g7_g2h_delratio, dfe1_g8_g2h_delratio]
e2_g2h_delratio = [dfe2_g3_g2h_delratio, dfe2_g4_g2h_delratio, dfe2_g6_g2h_delratio, dfe2_g7_g2h_delratio, dfe2_g8_g2h_delratio]
e3_g2h_delratio = [dfe3_g3_g2h_delratio, dfe3_g4_g2h_delratio, dfe3_g6_g2h_delratio, dfe3_g7_g2h_delratio, dfe3_g8_g2h_delratio]
e4_g2h_delratio = [dfe4_g3_g2h_delratio, dfe4_g4_g2h_delratio, dfe4_g6_g2h_delratio, dfe4_g7_g2h_delratio, dfe4_g8_g2h_delratio]

h2e_delratio = [dfh_e1_delratio, dfh_e2_delratio, dfh_e3_delratio, dfh_e4_delratio]

plot_results_avgdelay(enddevice_id, e2h_avgdelay_e1, e2h_avgdelay_e2, e2h_avgdelay_e3, e2h_avgdelay_e4,
                        g2h_avgdelay_e1, g2h_avgdelay_e2, g2h_avgdelay_e3, g2h_avgdelay_e4,
                        e2g_avgdelay_e1, e2g_avgdelay_e2, e2g_avgdelay_e3, e2g_avgdelay_e4,
                        e1_e2g_delratio, e2_e2g_delratio, e3_e2g_delratio, e4_e2g_delratio, h2e_delratio,
                        e1_g2h_delratio, e2_g2h_delratio, e3_g2h_delratio, e4_g2h_delratio)

plot_scatter(dfh_e1, dfg_e1g3_e2g, dfg_e1g4_e2g, dfg_e1g6_e2g, dfg_e1g7_e2g, dfg_e1g8_e2g, dfe1_e2h,
                dfh_e2, dfg_e2g3_e2g, dfg_e2g4_e2g, dfg_e2g6_e2g, dfg_e2g7_e2g, dfg_e2g8_e2g, dfe2_e2h,
                dfh_e3, dfg_e3g3_e2g, dfg_e3g4_e2g, dfg_e3g6_e2g, dfg_e3g7_e2g, dfg_e3g8_e2g, dfe3_e2h,
                dfh_e4, dfg_e4g3_e2g, dfg_e4g4_e2g, dfg_e4g6_e2g, dfg_e4g7_e2g, dfg_e4g8_e2g, dfe4_e2h)