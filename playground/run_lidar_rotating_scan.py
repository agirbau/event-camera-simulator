import bpy
import range_scanner

range_scanner.ui.user_interface.scan_rotating(
    bpy.context, 
    scannerObject=bpy.context.scene.objects["Camera"],

    xStepDegree=1,
    fovX=360.0,
    yStepDegree=1,
    fovY=30.0,
    rotationsPerSecond=20,

    reflectivityLower=0.0,
    distanceLower=0.0,
    reflectivityUpper=0.0,
    distanceUpper=100.0,
    maxReflectionDepth=10,
    
    enableAnimation=False,
    frameStart=1,
    frameEnd=24,
    frameStep=4,
    frameRate=24,

    addNoise=False,
    noiseType='gaussian',
    mu=0.0,
    sigma=0.01,
    noiseAbsoluteOffset=0.0,
    noiseRelativeOffset=0.0, 

    simulateRain=False,
    rainfallRate=0.0, 

    addMesh=True,

    exportLAS=False,
    exportHDF=False,
    exportCSV=False,
    exportPLY=False,
    exportSingleFrames=True,
    dataFilePath="/Users/felix/Projects/LINA/02_event-cameras/event-camera-simulator/out/leipzig",
    dataFileName="rotating",
    
    debugLines=False,
    debugOutput=False,
    outputProgress=True,
    measureTime=False,
    singleRay=False,
    destinationObject=None,
    targetObject=None
)  