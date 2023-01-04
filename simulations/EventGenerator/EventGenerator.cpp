#include "EventGenerator.h"
#include "TRandom.h"
#include <cmath>
#include "objects/Pixel.hpp"

using namespace corryvreckan;
using namespace std;

EventGenerator::EventGenerator(Configuration& config, std::vector<std::shared_ptr<Detector>> detectors)
    : Module(config, std::move(detectors)) {

    config_.setDefault<std::string>("input_file", "/local/data/simulation.txt");
    config_.setDefault<std::string>("track_model", "straightline");
    config_.setDefault<int>("mean_tracks_per_event", 3);
    config_.setDefault<long unsigned int>("seed", 42);

    seed_ = config_.get<long unsigned int>("seed");
    input_file_ = config_.get<std::string>("input_file");
    track_model_ = config_.get<std::string>("track_model");
    mean_tracks_per_event_ = config_.get<int>("mean_tracks_per_event");

}

void EventGenerator::initialize() {
    gRandom->SetSeed(seed_);
    event = 0;
    std::string title = "Track multiplicity;tracks;events";
    tracksPerEvent = new TH1F("tracksPerEvent", title.c_str(), 100, -0.5, 99.5);
    newfile.open(input_file_.c_str()); //open a file to perform read operation using file object
    float posX, posY, posZ, disX, disY, disZ, rotX ,rotY ,rotZ;
    // Loop over all planes
    int n_detectors = 0;
    for(auto& detector : get_regular_detectors(true)) {
        n_detectors++;
        if (newfile.is_open()){
            newfile >> posX >> posY >> posZ >> disX >> disY >> disZ >> rotX >> rotY >> rotZ;
            posX+=disX;
            posY+=disY;
            posZ+=disZ;
            printf("position = %f um,%f um,%f um \n", posX, posY, posZ);
            printf("orientation = %f deg,%f deg,%f deg \n", rotX, rotY, rotZ);
        }
        auto detectorID = detector->getName();

        TDirectory* directory = getROOTDirectory();
        TDirectory* local_directory = directory->mkdir(detectorID.c_str());
        local_directory->cd();
        title = detector->getName() + " Cluster Position (Global);x [mm];y [mm];events";
        clusterPositionGlobal[detectorID] = new TH2F("clusterPositionGlobal",
                                        title.c_str(),
                                        400,
                                        -detector->getSize().X() / 1.5,
                                        detector->getSize().X() / 1.5,
                                        400,
                                        -detector->getSize().Y() / 1.5,
                                        detector->getSize().Y() / 1.5);
        title = detector->getName() + " Cluster Position (Local);x [px];y [px];events";
        clusterPositionLocal[detectorID] = new TH2F("clusterPositionLocal",
                                        title.c_str(),
                                        detector->nPixels().X(),
                                        -0.5,
                                        detector->nPixels().X() - 0.5,
                                        detector->nPixels().Y(),
                                        -0.5,
                                        detector->nPixels().Y() - 0.5);
        title = detector->getName() + " Cluster multiplicity;clusters;events";
        clusterMultiplicity[detectorID] = new TH1F("clusterMultiplicity", title.c_str(), 50, -0.5, 49.5);

    }

    TDirectory* directory = getROOTDirectory();
    directory->cd();
    title = "Hits per track;hits;events";
    hitsPerTrack = new TH1F("hitsPerTrack", title.c_str(), n_detectors+1, -0.5, n_detectors+0.5);

}

StatusCode EventGenerator::run(const std::shared_ptr<Clipboard>& clipboard) {
    // Make the cluster container and the maps for clustering
    std::map<std::string, ClusterVector> deviceClusters;
    std::map<std::string, int> clusterCounter;

    for(auto& detector : get_regular_detectors(true)){
        auto detectorID = detector->getName();
        clusterCounter[detectorID] = 0;
    }
    int nTracks = gRandom->Poisson(mean_tracks_per_event_);
    tracksPerEvent->Fill(nTracks);
    for(int iTrack = 0; iTrack<nTracks; iTrack++) {
        int nHits=0;
        for(auto& detector : get_regular_detectors(true)) {
            float column,row;
            if (!newfile.is_open()) continue;
            newfile >> column >> row;
            LOG(DEBUG) << "cluster column: " << column<< "cluster row: " << row;
            if(column < 0 || row < 0 || row > 511 || column > 1023) continue;
            nHits++;
            auto detectorID = detector->getName();
            // New pixel => new cluster
            auto cluster = std::make_shared<Cluster>();
            double charge(0);
            
            // Create object with local cluster position
            auto positionLocal = detector->getLocalPosition(column, row);

            // Calculate global cluster position
            auto positionGlobal = detector->localToGlobal(positionLocal);

            // Set the cluster parameters
            cluster->setRow(row);
            cluster->setColumn(column);
            cluster->setCharge(charge);

            // Set uncertainty on position from intrinstic detector spatial resolution:
            cluster->setError(detector->getSpatialResolution());
            cluster->setTimestamp(event);
            cluster->setDetectorID(detectorID);
            cluster->setClusterCentre(positionGlobal);
            cluster->setClusterCentreLocal(positionLocal);


            clusterCounter[detectorID]++;
            deviceClusters[detectorID].push_back(cluster);
            clusterPositionGlobal[detectorID]->Fill(cluster->global().x(), cluster->global().y());
            clusterPositionLocal[detectorID]->Fill(cluster->column(), cluster->row());

            
        }
        hitsPerTrack->Fill(nHits);
    }
    event++;
    for(auto& detector : get_regular_detectors(true)){
        auto detectorID = detector->getName();
        clusterMultiplicity[detectorID]->Fill(clusterCounter[detectorID]);
        clipboard->putData(deviceClusters[detectorID], detectorID);
    }
    // Return value telling analysis to keep running
    return StatusCode::Success;
}
