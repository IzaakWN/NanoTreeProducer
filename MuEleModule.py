import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from TreeProducerMuEle import *


class declareVariables(TreeProducerMuEle):
    
    def __init__(self, name):

        super(declareVariables, self).__init__(name)


class MuEleProducer(Module):

    def __init__(self, name, dataType, **kwargs):
        
        self.name = name
        self.out = declareVariables(name)

        if dataType=='data':
            self.isData = True
        else:
            self.isData = False

        self.Nocut = 0
        self.Trigger = 1
        self.GoodMuons = 2
        self.GoodElectrons = 3
        self.GoodDiLepton = 4
        self.TotalWeighted = 15

    def beginJob(self):
        pass

    def endJob(self):
        self.out.outputfile.Write()
        self.out.outputfile.Close()
#        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):        
        pass
        
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

#        electrons = Collection(event, "Electron")


        #####################################
        self.out.h_cutflow.Fill(self.Nocut)
        #####################################

        #####################################
        if not self.isData:
            self.out.h_cutflow.Fill(self.TotalWeighted, event.genWeight)
        else:
            self.out.h_cutflow.Fill(self.TotalWeighted, 1.)
        #####################################

        if not event.HLT_IsoMu27:
            return False

        #####################################
        self.out.h_cutflow.Fill(self.Trigger)
        #####################################

        idx_goodmuons = []
        
        for imuon in range(event.nMuon):

            if event.Muon_pt[imuon] < 28: continue
            if abs(event.Muon_eta[imuon]) > 2.4: continue
            if abs(event.Muon_dz[imuon]) > 0.2: continue
            if abs(event.Muon_dxy[imuon]) > 0.045: continue
            if not event.Muon_mediumId[imuon]: continue

            idx_goodmuons.append(imuon)


        if len(idx_goodmuons)==0:
            return False

        #####################################
        self.out.h_cutflow.Fill(self.GoodMuons)
        #####################################

        idx_goodelectrons = []
        
        for ielectron in range(event.nElectron):

            if event.Electron_pt[ielectron] < 20: continue
            if abs(event.Electron_eta[ielectron]) > 2.1: continue
            if abs(event.Electron_dz[ielectron]) > 0.2: continue
            if abs(event.Electron_dxy[ielectron]) > 0.045: continue
            if event.Electron_convVeto[ielectron] !=1: continue
            if ord(event.Electron_lostHits[ielectron]) > 1: continue
#            if event.Electron_mvaFall17Iso_WP80[ielectron] < 0.5: continue

            idx_goodelectrons.append(ielectron)


        if len(idx_goodelectrons)==0:
            return False

        #####################################
        self.out.h_cutflow.Fill(self.GoodElectrons)
        #####################################


        
        # to check dR matching

        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        dileptons = []

        for idx1 in idx_goodmuons:
            for idx2 in idx_goodelectrons:
                
                if idx1 >= idx2: continue

                dR = muons[idx1].p4().DeltaR(electrons[idx2].p4())
                if dR < 0.5: continue
                
                muon_reliso = event.Muon_pfRelIso04_all[idx1]
                electron_reliso = event.Electron_pfRelIso03_all[idx2]

                # muon first
                _dilepton = DiLeptonBasicClass(idx1, event.Muon_pt[idx1], muon_reliso,
                                               idx2, event.Electron_pt[idx2], electron_reliso)

                dileptons.append(_dilepton)

        if len(dileptons)==0:
            return False


        #####################################
        self.out.h_cutflow.Fill(self.GoodDiLepton)
        #####################################

        dilepton = bestDiLepton(dileptons)

#        print 'chosen tau1 (idx, pt) = ', dilepton.tau1_idx, dilepton.tau1_pt, 'check', taus[dilepton.tau1_idx].p4().Pt()
#        print 'chosen tau2 (idx, pt) = ', dilepton.tau2_idx, dilepton.tau2_pt, 'check', taus[dilepton.tau2_idx].p4().Pt()

        jetIds = []

        jets = Collection(event, "Jet")
#        jets = filter(self.jetSel,jets):

        nfjets = 0
        ncjets = 0
        nbtag = 0

        for ijet in range(event.nJet):

#        for j in filter(self.jetSel,jets):


            if event.Jet_pt[ijet] < 30: 
                continue

            if abs(event.Jet_eta[ijet]) > 4.7: 
                continue

            dR = muons[dilepton.tau1_idx].p4().DeltaR(jets[ijet].p4())
            if dR < 0.5: 
                continue

            dR = electrons[dilepton.tau2_idx].p4().DeltaR(jets[ijet].p4())

            if dR < 0.5: 
                continue

#            print '#', ijet, 'pt = ', jets[ijet].p4().Pt(), event.Jet_pt[ijet]

            jetIds.append(ijet)
            
            if abs(event.Jet_eta[ijet]) > 2.4:
                nfjets += 1
            else:
                ncjets += 1

            if event.Jet_btagCSVV2[ijet] > 0.8838:
                nbtag += 1
            
            

#        eventSum = ROOT.TLorentzVector()
#
#        for lep in electrons :
#            eventSum += lep.p4()
#        for lep in electrons :
#            eventSum += lep.p4()
#        for j in filter(self.jetSel,jets):
#            eventSum += j.p4()


        # electron
        self.out.pt_2[0]                       = event.Electron_pt[dilepton.tau1_idx]
        self.out.eta_2[0]                      = event.Electron_eta[dilepton.tau1_idx]
        self.out.phi_2[0]                      = event.Electron_phi[dilepton.tau1_idx]
        self.out.mass_2[0]                     = event.Electron_mass[dilepton.tau1_idx]
        self.out.dxy_2[0]                      = event.Electron_dxy[dilepton.tau1_idx]
        self.out.dz_2[0]                       = event.Electron_dz[dilepton.tau1_idx]         
        self.out.q_2[0]                        = event.Electron_charge[dilepton.tau1_idx]
        self.out.pfRelIso03_all_2[0]           = event.Electron_pfRelIso03_all[dilepton.tau1_idx]
        self.out.cutBased_2[0]                 = event.Electron_cutBased[dilepton.tau1_idx]
        self.out.mvaFall17Iso_2[0]             = event.Electron_mvaFall17Iso[dilepton.tau1_idx]
        self.out.mvaFall17Iso_WP80_2[0]        = event.Electron_mvaFall17Iso_WP80[dilepton.tau1_idx]
        self.out.mvaFall17Iso_WP90_2[0]        = event.Electron_mvaFall17Iso_WP90[dilepton.tau1_idx]
        self.out.mvaFall17Iso_WPL_2[0]         = event.Electron_mvaFall17Iso_WPL[dilepton.tau1_idx]




        if not self.isData:
            self.out.genPartFlav_1[0]              = ord(event.Muon_genPartFlav[dilepton.tau1_idx])
            self.out.genPartFlav_2[0]              = ord(event.Electron_genPartFlav[dilepton.tau2_idx])


        # event weights
        self.out.run[0]                        = event.run
        self.out.luminosityBlock[0]            = event.luminosityBlock
        self.out.event[0]                      = event.event & 0xffffffffffffffff
        self.out.MET_pt[0]                     = event.MET_pt
        self.out.MET_phi[0]                    = event.MET_phi
        self.out.PuppiMET_pt[0]                = event.PuppiMET_pt
        self.out.PuppiMET_phi[0]               = event.PuppiMET_phi
        self.out.MET_significance[0]           = event.MET_significance
        self.out.MET_covXX[0]                  = event.MET_covXX
        self.out.MET_covXY[0]                  = event.MET_covXY
        self.out.MET_covYY[0]                  = event.MET_covYY
        self.out.fixedGridRhoFastjetAll[0]     = event.fixedGridRhoFastjetAll
        self.out.npvs[0]                       = event.PV_npvs
        self.out.npvsGood[0]                   = event.PV_npvsGood

        if not self.isData:
            self.out.GenMET_pt[0]              = event.GenMET_pt
            self.out.GenMET_phi[0]             = event.GenMET_phi
            self.out.nPU[0]                    = event.Pileup_nPU
            self.out.nTrueInt[0]               = event.Pileup_nTrueInt
            self.out.genWeight[0]              = event.genWeight
            self.out.LHE_Njets[0]              = event.LHE_Njets


        self.out.jpt_1[0]                      = -9.
        self.out.jeta_1[0]                     = -9.
        self.out.jphi_1[0]                     = -9.
        self.out.jcsvv2_1[0]                   = -9.
        self.out.jdeepb_1[0]                   = -9.

        self.out.jpt_2[0]                      = -9.
        self.out.jeta_2[0]                     = -9.
        self.out.jphi_2[0]                     = -9.
        self.out.jcsvv2_2[0]                   = -9.
        self.out.jdeepb_2[0]                   = -9.


        if len(jetIds)>0:
            self.out.jpt_1[0]                  = event.Jet_pt[jetIds[0]]
            self.out.jeta_1[0]                 = event.Jet_eta[jetIds[0]]
            self.out.jphi_1[0]                 = event.Jet_phi[jetIds[0]]
            self.out.jcsvv2_1[0]               = event.Jet_btagCSVV2[jetIds[0]]
            self.out.jdeepb_1[0]               = event.Jet_btagDeepB[jetIds[0]]

        if len(jetIds)>1:
            self.out.jpt_2[0]                  = event.Jet_pt[jetIds[1]]
            self.out.jeta_2[0]                 = event.Jet_eta[jetIds[1]]
            self.out.jphi_2[0]                 = event.Jet_phi[jetIds[1]]
            self.out.jcsvv2_2[0]               = event.Jet_btagCSVV2[jetIds[1]]
            self.out.jdeepb_2[0]               = event.Jet_btagDeepB[jetIds[1]]


        self.out.njets[0]                      = len(jetIds)
        self.out.nfjets[0]                     = nfjets
        self.out.ncjets[0]                     = ncjets
        self.out.nbtag[0]                      = nbtag

        self.out.pfmt_1[0]                     = math.sqrt( 2 * self.out.pt_1[0] * self.out.MET_pt[0] * ( 1 - math.cos(deltaPhi(self.out.phi_1[0], self.out.MET_phi[0])) ) );
        self.out.pfmt_2[0]                     = math.sqrt( 2 * self.out.pt_2[0] * self.out.MET_pt[0] * ( 1 - math.cos(deltaPhi(self.out.phi_2[0], self.out.MET_phi[0])) ) );

        self.out.m_vis[0]                      = (muons[dilepton.tau1_idx].p4() + electrons[dilepton.tau2_idx].p4()).M()
        self.out.pt_ll[0]                      = (muons[dilepton.tau1_idx].p4() + electrons[dilepton.tau2_idx].p4()).Pt()
        
        self.out.dR_ll[0]                      = muons[dilepton.tau1_idx].p4().DeltaR(electrons[dilepton.tau2_idx].p4())
        self.out.dphi_ll[0]                    = deltaPhi(self.out.phi_1[0], self.out.phi_2[0])


        # pzeta calculation

        leg1 = ROOT.TVector3(muons[dilepton.tau1_idx].p4().Px(), muons[dilepton.tau1_idx].p4().Py(), 0.)
        leg2 = ROOT.TVector3(electrons[dilepton.tau2_idx].p4().Px(), electrons[dilepton.tau2_idx].p4().Py(), 0.)
        
#        print 'leg1 px,py,pz = ', taus[dilepton.tau1_idx].p4().Px(), taus[dilepton.tau1_idx].p4().Py(), '0'
#        print 'leg2 px,py,pz = ', taus[dilepton.tau2_idx].p4().Px(), taus[dilepton.tau2_idx].p4().Py(), '0'

        met_tlv = ROOT.TLorentzVector()
        met_tlv.SetPxPyPzE(self.out.MET_pt[0]*math.cos(self.out.MET_phi[0]), 
                           self.out.MET_pt[0]*math.cos(self.out.MET_phi[0]),
                           0, 
                           self.out.MET_pt[0])

#        print self.out.MET_pt[0]*math.cos(self.out.MET_phi[0]), self.out.MET_pt[0]*math.cos(self.out.MET_phi[0]), '0', self.out.MET_pt[0]

        metleg = met_tlv.Vect()
        zetaAxis = ROOT.TVector3(leg1.Unit() + leg2.Unit()).Unit()
        pZetaVis_ = leg1*zetaAxis + leg2*zetaAxis
        pZetaMET_ = metleg*zetaAxis
        
#        print 'pZetaVis = ', pZetaVis_, ' pZetaMET = ', pZetaMET_                                                                                           

        self.out.pzetamiss[0]  = pZetaMET_
        self.out.pzetavis[0]   = pZetaVis_
        self.out.pzeta_disc[0] = pZetaMET_ - 0.5*pZetaVis_


        # extra lepton vetos
        self.out.extramuon_veto[0], self.out.extraelec_veto[0], self.out.dilepton_veto[0]  = extraLeptonVetos(event, [dilepton.tau1_idx], [dilepton.tau2_idx], self.name)

        self.out.isData[0] = self.isData

        self.out.tree.Fill() 

        return True
