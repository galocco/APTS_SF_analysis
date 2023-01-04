#ifndef EventGenerator_H
#define EventGenerator_H 1

#include <TCanvas.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TFile.h>
#include <iostream>
#include <fstream>
#include "core/module/Module.hpp"
#include "objects/Cluster.hpp"

namespace corryvreckan {
    /** @ingroup Modules
     */
    class EventGenerator : public Module {

    public:
        // Constructors and destructors
        EventGenerator(Configuration& config, std::vector<std::shared_ptr<Detector>> detectors);
        ~EventGenerator() {}

        // Functions
        void initialize() override;
        StatusCode run(const std::shared_ptr<Clipboard>& clipboard) override;

    private:

        //void generateCluster(Cluster*, float[3], float[3]);

        std::map<std::string, TH1F*> clusterMultiplicity;
        std::map<std::string, TH2F*> clusterPositionGlobal;
        std::map<std::string, TH2F*> clusterPositionLocal;

        TH1F* tracksPerEvent;
        TH2F* hitmap;
        TH1F* hitsPerTrack;
        std::fstream newfile;
        int event;
        int mean_tracks_per_event_;
        long unsigned int seed_;
        std::string input_file_;
        std::string track_model_;
    };
} // namespace corryvreckan
#endif // EventGenerator_H
