# Correction Tools
Several tools to get corrections, efficiencies, scale factors (SFs), event weights, etc.



## Pileup reweighting

`PileupWeightTool.py` provides the pileup event weight based on the data and MC profiles in [`pileup`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/CorrectionTools/pileup).

The data profile can be computed with the `brilcalc` tool on `lxplus`.
The MC profile can be taken from the all-inclusive distribution of the `Pileup_nTrueInt` variable in nanoAOD, for each event:
```
    self.out.pileup.Fill(event.Pileup_nTrueInt)
```
and then extracted with [`pileup/getPileupProfiles.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/CorrectionTools/pileup/getPileupProfiles.py).



## Lepton efficiencies

Several classes are available to get corrections for electrons, muons and hadronically-decayed tau leptons:

* `ScaleFactorTool.py`
  * `ScaleFactor`: general class to get SFs from histograms;
  * `ScaleFactorHTT`: class to get SFs from histograms, as measured by the [HTT group](https://github.com/CMS-HTT/LeptonEfficiencies);
* `MuonSFs.py`: class to get muon trigger / identification / isolation SFs;
* `ElectronSFs.py` class to get electron trigger / identification / isolation SFs;
* `TauTauSFs.py` class to get ditau trigger SFs;
* `LeptonTauFakeSFs.py` class to get lepton to tau fake SFs.



## B-tagging tools

`BTaggingTool.py` provides two classes: `BTagWPs` for saving the working points (WPs) per year and type of tagger, and `BTagWeightTool` to provide b-tagging weights. These can be called during the initialization of you analysis module, e.g.:
```
class MuTauProducer(Module):
    
    def __init__(self, name, dataType, **kwargs):
        
        ...
        
        if not self.isData:
          self.btagTool      = BTagWeightTool('CSVv2','medium',channel=channel,year=year)
        self.csvv2_wp  = BTagWPs('CSVv2',year=year)
        
        ...
```

`BTagWeightTool` calculates b-tagging reweighting based on the SFs provided from the BTagging group and analysis-dependent efficiencies measured in MC. These are saved in `ROOT` files in [`btag`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/CorrectionTools/btag).
The event weight is calculated according to [this method](https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagSFMethods#1a_Event_reweighting_using_scale).

The efficiencies in MC can be calculated by filling histograms with `fillEfficiencies` for each selected event, after removing overlap with other selected objects, e.g. the muon and tau object in [`MuTauModule.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/MuTauModule.py):
```
    def analyze(self event):
    
        # select isolated muon and tau
        ...
        
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 4.7: continue
            if muon.DeltaR(jets[ijet].p4()) < 0.5: continue
            if tau.DeltaR(jets[ijet].p4()) < 0.5: continue
            jetIds.append(ijet)
        
        if not self.isData:
          self.btagTool.fillEfficiencies(event,jetIds)
        
        ...
```
Then use [`btag/getBTagEfficiencies.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/CorrectionTools/btag/getBTagEfficiencies.py) to extract all histograms from MC output and compute the efficiencies.



## Recoil corrections

`RecoilCorrectionTool.py` provides a class to calculate the Z boson four-vector, and get the reweighting of LO Drell-Yan events as a function of Z boson pT and mass. Weights are stored in [`Zpt`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/CorrectionTools/Zpt).

