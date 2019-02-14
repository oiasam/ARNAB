## Orchestration and Control System


### Install Controller
* Prepare a machine for Floodlight Controller - Tested in Ubuntu 16.04. 
```sudo apt install default-jdk ant```
```cd ocs/controller```
```ant```
### Controller Configuration
* Edit `floodlightdefault.properties` to look something like the following: 
    ```shell
    ~/ARNAB/ocs/controller/src/main/resources/floodlightdefault.properties
    floodlight.modules = net.floodlightcontroller.storage.memory.MemoryStorageSource,\
    net.floodlightcontroller.staticflowentry.StaticFlowEntryPusher,\
    net.floodlightcontroller.learningswitch.LearningSwitch,\
    net.floodlightcontroller.jython.JythonDebugInterface,\
    net.floodlightcontroller.counter.CounterStore,\
    net.floodlightcontroller.perfmon.PktInProcessingTime,\
    net.floodlightcontroller.ui.web.StaticWebRoutable,\
    net.floodlightcontroller.odin.master.OdinMaster
    net.floodlightcontroller.restserver.RestApiServer.port = 8080
    net.floodlightcontroller.core.FloodlightProvider.openflowport = 6633
    net.floodlightcontroller.jython.JythonDebugInterface.port = 6655
    net.floodlightcontroller.odin.master.OdinMaster.masterPort = 2819
    net.floodlightcontroller.odin.master.OdinMaster.poolFile = poolfile
    net.floodlightcontroller.odin.master.OdinMaster.clientList = odin_client_list
    ```
* Prepare poolFile by editting `~/ARNAB/ocs/controller/poolFile` to reflict the network settings and applications to be used
    ```shell
    # Pool-1
    NAME pool-1
    NODES 192.168.1.14
    NETWORKS wi5-demo

    ####### Now applications and its parameters are defined ######

    ####### FlowDetectionManager params
    ####### DETECTION IpAddressOfDetector
   # APPLICATION net.floodlightcontroller.odin.applications.FlowDetectionManager
   # DETECTION 192.168.1.200

   # APPLICATION net.floodlightcontroller.odin.applications.ShowStatistics

    ####### MobilityManager params
    ####### MOBILITY TimeToStart(sec) IdleClient(sec) Hysteresis(sec) SignalThreshold(dBm) ScanningTime(sec) NumberOfTriggers TimerResetTriggers(sec)
    APPLICATION net.floodlightcontroller.odin.applications.MobilityManager
    MOBILITY 30 180 15 -56 1 5 1

    ####### ShowScannedStationsStatistics params - Optional filename to save statistics
    ####### INTERFERENCES TimeToStart(sec) ReportingPeriod(sec) ScanningInterval(sec) AddedTime(sec)
   # APPLICATION net.floodlightcontroller.odin.applications.ShowScannedStationsStatistics
   # INTERFERENCES 30 30 5 1 ScannedStationsStatistics.txt

    ####### ShowMatrixOfDistancedBs params
    ####### MATRIX TimeToStart(sec) ReportingPeriod(sec) ScanningInterval(sec) AddedTime(sec) Channel
   # APPLICATION net.floodlightcontroller.odin.applications.ShowMatrixOfDistancedBs
   # MATRIX 30 30 5 1 6

    # Pool-2
    #NAME pool-2
    #NODES 192.168.1.7 192.168.1.8 192.168.1.9
    #NETWORKS odin-guest-network
    #APPLICATION net.floodlightcontroller.odin.applications.SimpleLoadBalancer
    ```
* Run the controller 
    ```shell
    ~/ARNAB/ocs/controller# java -jar ./target/floodlight.jar -cf ./src/main/resources/floodlightdefault.properties
    ```
