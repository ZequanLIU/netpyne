from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = 200 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 20 # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 5, 'yRange': [100,300], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'SOM_simple', 'numCells': 5, 'yRange': [100,300], 'cellModel': 'HH_simple'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 5, 'yRange': [300,600], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'PV_simple', 'numCells': 5, 'yRange': [300,600], 'cellModel': 'HH_simple'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 5, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'SOM', 'numCells': 5, 'ynormRange': [1.0,2.0], 'cellModel': 'HH_simple'}

## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='IT2_reduced_cellParams.json')
netParams.cellParams['CellRule']['conds'] = {'cellType': ['E','I']}

#------------------------------------------------------------------------------
## PV cell params (3-comp)
cellRule = netParams.importCellParams(label='PV_simple', conds={'cellType':'PV', 'cellModel':'HH_simple'}, 
  fileName='cells/FS3.hoc', cellName='FScell1', cellInstance = True)


#------------------------------------------------------------------------------
## SOM cell params (3-comp)
cellRule = netParams.importCellParams(label='SOM_simple', conds={'cellType':'SOM', 'cellModel':'HH_simple'}, 
  fileName='cells/LTS3.hoc', cellName='LTScell1', cellInstance = True)


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 40, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 10.0, 'sec': 'soma', 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}

## Cell connectivity rules
netParams.connParams['E->all'] = {
  'preConds': {'cellType': 'E'}, 'postConds': {'y': [100,1000]},  #  E -> all (100-1000 um)
  'probability': 0.1 ,                  # probability of connection
  'weight': '5.0*post_ynorm',         # synaptic weight 
  'delay': 'max(1.0, dist_3D/propVelocity)',      # transmission delay (ms) 
  'synMech': 'exc'}                     # synaptic mechanism 

netParams.connParams['I->E'] = {
  'preConds': {'cellType': 'I'}, 'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
  'probability': '0.4*exp(-dist_3D/probLengthConst)',   # probability of connection
  'weight': 1.0,                                      # synaptic weight 
  'delay': 'max(1.0, dist_3D/propVelocity)',                      # transmission delay (ms) 
  'synMech': 'inh'}                                     # synaptic mechanism 


# Simulation configuration
simConfig = specs.SimConfig()        # object of class SimConfig to store simulation configuration
simConfig.duration = 0.5*1e3           # Duration of the simulation, in ms
simConfig.dt = 0.1                # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages 
simConfig.recordStep = 0.1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'net_lfp'   # Set file output name
simConfig.printSynsAfterRule = True
#simConfig.recordLFP = [[-15, y, 1.0*netParams.sizeZ] for y in range(netParams.sizeY/5, netParams.sizeY, netParams.sizeY/5)]

simConfig.analysis['plotRaster'] = {'include': ['I5', 'E2', 'I2', 'E4'],'orderBy': ['pop','y'], 'orderInverse': True, 'saveFig':True, 'figSize': (9,3)}      # Plot a raster
#simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'NFFT': 256*20, 'noverlap': 128*20, 'nperseg': 132*20, 'saveFig': True} 
#simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'plots': ['timeSeries'], 'NFFT': 256*2, 'noverlap': 128*2, 'nperseg': 132*2, 'saveFig': True} 
#simConfig.analysis['plotSpikeStats'] = {'include': ['E2', 'E4', ['E2', 'E4']] , 'stats': ['rate'], 'graphType': 'histogram', 'figSize': (10,6)}

# Create network and run simulation
#sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    

sim.initialize(
    simConfig = simConfig,  
    netParams = netParams)          # create network object and set cfg and net params
sim.net.createPops()                    # instantiate network populations
sim.net.createCells()                   # instantiate network cells based on defined populations
sim.net.addStims()              # add network stimulation
sim.cfg.createPyStruct = 0
sim.net.connectCells()                  # create connections between cells based on params
sim.setupRecording()                    # setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                            # run parallel Neuron simulation  
sim.gatherData()                        # gather spiking data and cell info from each node
sim.saveData()                          # save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()               # plot spike raster etc


