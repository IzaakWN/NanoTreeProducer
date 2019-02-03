import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from TreeProducerMuMu import *
from CorrectionTools.MuonSFs import *
from CorrectionTools.PileupWeightTool import *
from CorrectionTools.BTaggingTool import BTagWeightTool, BTagWPs
from CorrectionTools.RecoilCorrectionTool import RecoilCorrectionTool, getZPTMass, getTTPTMass


class MuMuProducer(Module):
    
    def __init__(self, name, dataType, **kwargs):
        
        self.name            = name
        self.out             = TreeProducerMuMu(name)
        self.isData          = dataType=='data'
        self.year            = kwargs.get('year',    2017 )
        self.tes             = kwargs.get('tes',     1.0  )
        self.doZpt           = kwargs.get('doZpt',   'DY' in name )
        self.doTTpt          = kwargs.get('doTTpt',  'TT' in name )
        self.doTight         = kwargs.get('doTight', self.tes!=1 )
        self.channel         = 'mumu'
        year, channel        = self.year, self.channel
                
        setYear(year)
        self.vlooseIso       = getVLooseTauIso(year)
        if year==2016:
          self.trigger       = lambda e: e.HLT_IsoMu22 or e.HLT_IsoMu22_eta2p1 or e.HLT_IsoTkMu22 or e.HLT_IsoTkMu22_eta2p1 #or e.HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1
          self.muon1CutPt    = 23
        else:
          self.trigger       = lambda e: e.HLT_IsoMu24 or e.HLT_IsoMu27
          self.muon1CutPt    = 25
        self.muon2CutPt      = 15
        
        if not self.isData:
          self.muSFs         = MuonSFs(year=year)
          self.puTool        = PileupWeightTool(year=year)
          self.btagTool      = BTagWeightTool('CSVv2','medium',channel='mutau',year=year)
          self.btagTool_deep = BTagWeightTool('DeepCSV','medium',channel='mutau',year=year)
          if self.doZpt or self.doTTpt:
            self.recoilTool  = RecoilCorrectionTool(year=year)
        self.csvv2_wp        = BTagWPs('CSVv2',year=year)
        self.deepcsv_wp      = BTagWPs('DeepCSV',year=year)
        
        self.Nocut = 0
        self.Trigger = 1
        self.GoodMuons = 2
        self.GoodSecondMuon = 3
        self.GoodDiLepton = 4
        self.TotalWeighted = 15
        self.TotalWeighted_no0PU = 16
        
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Nocut,               "no cut"                 )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.Trigger,             "trigger"                )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodMuons,           "muon object"            )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodSecondMuon,      "second muon object"     )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.GoodDiLepton,        "mumu pair"              )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted,       "no cut, weighted"       )
        self.out.cutflow.GetXaxis().SetBinLabel(1+self.TotalWeighted_no0PU, "no cut, weighted, PU>0" )
        self.out.cutflow.GetXaxis().SetLabelSize(0.041)
        
    def beginJob(self):
        pass
        
    def endJob(self):
        self.out.outputfile.Write()
        self.out.outputfile.Close()
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):        
        pass
        
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        #####################################
        self.out.cutflow.Fill(self.Nocut)
        if self.isData:
          self.out.cutflow.Fill(self.TotalWeighted, 1.)
          if event.PV_npvs>0:
            self.out.cutflow.Fill(self.TotalWeighted_no0PU, 1.)
          else:
            return False
        else:
          self.out.cutflow.Fill(self.TotalWeighted, event.genWeight)
          self.out.pileup.Fill(event.Pileup_nTrueInt)
          if event.Pileup_nTrueInt>0:
            self.out.cutflow.Fill(self.TotalWeighted_no0PU, event.genWeight)
          else:
            return False
        #####################################
        
        
        if not self.trigger(event):
            return False
        
        #####################################
        self.out.cutflow.Fill(self.Trigger)
        #####################################
        
        
        idx_goodmuons = [ ]
        for imuon in range(event.nMuon):
            if event.Muon_pt[imuon] < self.muon2CutPt: continue # lower pT cut
            if abs(event.Muon_eta[imuon]) > 2.4: continue
            if abs(event.Muon_dz[imuon]) > 0.2: continue
            if abs(event.Muon_dxy[imuon]) > 0.045: continue
            if event.Muon_pfRelIso04_all[imuon] > 0.15: continue
            if not event.Muon_mediumId[imuon]: continue
            idx_goodmuons.append(imuon)
        
        if len(idx_goodmuons) < 1:
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodMuons)
        #####################################
        
        
        if not any(event.Muon_pt[i]>self.muon1CutPt for i in idx_goodmuons) or len(idx_goodmuons)<2: # higher pT cut
            return False
        
        #####################################
        self.out.cutflow.Fill(self.GoodSecondMuon)
        #####################################
        
        
        muons = Collection(event, 'Muon')
        dileptons = [ ]
        for idx1 in idx_goodmuons:
          for idx2 in idx_goodmuons:
              if idx1 >= idx2: continue
              muon1 = muons[idx1].p4()
              muon2 = muons[idx2].p4()
              if muon1.DeltaR(muon2) < 0.5: continue
              if not (70<(muon1+muon2).M()<110): continue # Z mass
              dilepton = DiLeptonBasicClass(idx1, event.Muon_pt[idx1], event.Muon_pfRelIso04_all[idx1], 
                                            idx2, event.Muon_pt[idx2], event.Muon_pfRelIso04_all[idx2])
              dileptons.append(dilepton)
        
        if len(dileptons)==0:
            return False
        
        dilepton = bestDiLepton(dileptons)
        muon1    = muons[dilepton.id1].p4()
        muon2    = muons[dilepton.id2].p4()
        
        #####################################
        self.out.cutflow.Fill(self.GoodDiLepton)
        #####################################
        
        
        # JETS
        jetIds  = [ ]
        bjetIds = [ ]
        jets    = Collection(event, 'Jet')
        nfjets  = 0
        ncjets  = 0
        nbtag   = 0
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 20: continue # 20 for tau -> j fake measurement
            if abs(event.Jet_eta[ijet]) > 4.7: continue
            if muon1.DeltaR(jets[ijet].p4()) < 0.5: continue
            if muon2.DeltaR(jets[ijet].p4()) < 0.5: continue
            jetIds.append(ijet)
            
            if abs(event.Jet_eta[ijet]) > 2.4:
                nfjets += 1
            else:
                ncjets += 1
            
            if event.Jet_btagDeepB[ijet] > self.deepcsv_wp.medium:
              nbtag += 1
              bjetIds.append(ijet)
        
        if not self.isData and event.Muon_pfRelIso04_all[dilepton.id1]<0.50 and event.Muon_pfRelIso04_all[dilepton.id2]<0.50:
          self.btagTool.fillEfficiencies(event,jetIds)
          self.btagTool_deep.fillEfficiencies(event,jetIds)
        
        
        # MUON 1
        self.out.pt_1[0]                       = event.Muon_pt[dilepton.id1]
        self.out.eta_1[0]                      = event.Muon_eta[dilepton.id1]
        self.out.phi_1[0]                      = event.Muon_phi[dilepton.id1]
        self.out.m_1[0]                        = event.Muon_mass[dilepton.id1]
        self.out.dxy_1[0]                      = event.Muon_dxy[dilepton.id1]
        self.out.dz_1[0]                       = event.Muon_dz[dilepton.id1]         
        self.out.q_1[0]                        = event.Muon_charge[dilepton.id1]
        self.out.pfRelIso04_all_1[0]           = event.Muon_pfRelIso04_all[dilepton.id1]
        
        
        # MUON 2
        self.out.pt_2[0]                       = event.Muon_pt[dilepton.id2]
        self.out.eta_2[0]                      = event.Muon_eta[dilepton.id2]
        self.out.phi_2[0]                      = event.Muon_phi[dilepton.id2]
        self.out.m_2[0]                        = event.Muon_mass[dilepton.id2]
        self.out.dxy_2[0]                      = event.Muon_dxy[dilepton.id2]
        self.out.dz_2[0]                       = event.Muon_dz[dilepton.id2]         
        self.out.q_2[0]                        = event.Muon_charge[dilepton.id2]
        self.out.pfRelIso04_all_2[0]           = event.Muon_pfRelIso04_all[dilepton.id2]
        
        
        # TAU for jet -> tau fake rate measurement
        maxId = -1
        maxPt = 20
        taus  = Collection(event, 'Tau')
        for itau in range(event.nTau):
          if event.Tau_pt[itau] < maxPt: continue
          if muon1.DeltaR(taus[itau].p4())<0.5: continue
          if muon2.DeltaR(taus[itau].p4())<0.5: continue
          if abs(event.Tau_eta[itau])>2.3: continue
          if abs(event.Tau_dz[itau])>0.2: continue
          if event.Tau_decayMode[itau] not in [0,1,10,11]: continue
          if abs(event.Tau_charge[itau])!=1: continue
          if ord(event.Tau_idAntiEle[itau])<1: continue # VLoose
          if ord(event.Tau_idAntiMu[itau])<1: continue # Loose
          #if not self.vlooseIso(event,itau): continue
          maxId = itau
          maxPt = event.Tau_pt[itau]
        if maxId>-1:
          self.out.pt_3[0]                     = event.Tau_pt[maxId]
          self.out.eta_3[0]                    = event.Tau_eta[maxId]
          self.out.m_3[0]                      = event.Tau_mass[maxId]
          self.out.decayMode_3[0]              = event.Tau_decayMode[maxId]
          self.out.idAntiEle_3[0]              = ord(event.Tau_idAntiEle[maxId])
          self.out.idAntiMu_3[0]               = ord(event.Tau_idAntiMu[maxId])
          self.out.idMVAoldDM_3[0]             = ord(event.Tau_idMVAoldDM[maxId])
          self.out.idMVAoldDM2017v1_3[0]       = ord(event.Tau_idMVAoldDM2017v1[maxId])
          self.out.idMVAoldDM2017v2_3[0]       = ord(event.Tau_idMVAoldDM2017v2[maxId])
          self.out.idMVAnewDM2017v2_3[0]       = ord(event.Tau_idMVAnewDM2017v2[maxId])
          self.out.idIso_3[0]                  = Tau_idIso(event,maxId)
          if not self.isData:
            self.out.genPartFlav_3[0]          = ord(event.Tau_genPartFlav[maxId])
        else:
          self.out.pt_3[0]                     = -1
          self.out.eta_3[0]                    = -9
          self.out.m_3[0]                      = -1
          self.out.decayMode_3[0]              = -1
          self.out.idAntiEle_3[0]              = -1
          self.out.idAntiMu_3[0]               = -1
          self.out.idMVAoldDM_3[0]             = -1
          self.out.idMVAoldDM2017v1_3[0]       = -1
          self.out.idMVAoldDM2017v2_3[0]       = -1
          self.out.idMVAnewDM2017v2_3[0]       = -1
          self.out.idIso_3[0]                  = -1
          self.out.genPartFlav_3[0]            = -1
        
        
        # EVENT
        self.out.isData[0]                     = self.isData
        self.out.run[0]                        = event.run
        self.out.lumi[0]                       = event.luminosityBlock
        self.out.event[0]                      = event.event & 0xffffffffffffffff
        self.out.met[0]                        = event.MET_pt
        self.out.metphi[0]                     = event.MET_phi
        ###self.out.puppimet[0]                  = event.PuppiMET_pt
        ###self.out.puppimetphi[0]               = event.PuppiMET_phi
        ###self.out.metsignificance[0]           = event.MET_significance
        ###self.out.metcovXX[0]                  = event.MET_covXX
        ###self.out.metcovXY[0]                  = event.MET_covXY
        ###self.out.metcovYY[0]                  = event.MET_covYY
        ###self.out.fixedGridRhoFastjetAll[0]    = event.fixedGridRhoFastjetAll
        self.out.npvs[0]                       = event.PV_npvs
        self.out.npvsGood[0]                   = event.PV_npvsGood
        
        if not self.isData:
          self.out.genPartFlav_1[0]            = ord(event.Muon_genPartFlav[dilepton.id1])
          self.out.genPartFlav_2[0]            = ord(event.Muon_genPartFlav[dilepton.id2])
          self.out.genmet[0]                   = event.GenMET_pt
          self.out.genmetphi[0]                = event.GenMET_phi
          self.out.nPU[0]                      = event.Pileup_nPU
          self.out.nTrueInt[0]                 = event.Pileup_nTrueInt
          try:
            self.out.LHE_Njets[0]              = event.LHE_Njets
          except RuntimeError:
            self.out.LHE_Njets[0]              = -1
        
        
        # JETS
        self.out.njets[0]                      = len(jetIds)
        self.out.njets50[0]                    = len([j for j in jetIds if event.Jet_pt[j]>50])
        self.out.nfjets[0]                     = nfjets
        self.out.ncjets[0]                     = ncjets
        self.out.nbtag[0]                      = nbtag
        
        if len(jetIds)>0:
          self.out.jpt_1[0]                    = event.Jet_pt[jetIds[0]]
          self.out.jeta_1[0]                   = event.Jet_eta[jetIds[0]]
          self.out.jphi_1[0]                   = event.Jet_phi[jetIds[0]]
          self.out.jcsvv2_1[0]                 = event.Jet_btagCSVV2[jetIds[0]]
          self.out.jdeepb_1[0]                 = event.Jet_btagDeepB[jetIds[0]]
        else:
          self.out.jpt_1[0]                    = -9.
          self.out.jeta_1[0]                   = -9.
          self.out.jphi_1[0]                   = -9.
          self.out.jcsvv2_1[0]                 = -9.
          self.out.jdeepb_1[0]                 = -9.
        
        if len(jetIds)>1:  
          self.out.jpt_2[0]                    = event.Jet_pt[jetIds[1]]
          self.out.jeta_2[0]                   = event.Jet_eta[jetIds[1]]
          self.out.jphi_2[0]                   = event.Jet_phi[jetIds[1]]
          self.out.jcsvv2_2[0]                 = event.Jet_btagCSVV2[jetIds[1]]
          self.out.jdeepb_2[0]                 = event.Jet_btagDeepB[jetIds[1]]
        else:
          self.out.jpt_2[0]                    = -9.
          self.out.jeta_2[0]                   = -9.
          self.out.jphi_2[0]                   = -9.
          self.out.jcsvv2_2[0]                 = -9.
          self.out.jdeepb_2[0]                 = -9.
        
        if len(bjetIds)>0:
          self.out.bpt_1[0]                    = event.Jet_pt[bjetIds[0]]
          self.out.beta_1[0]                   = event.Jet_eta[bjetIds[0]]
        else:
          self.out.bpt_1[0]                    = -9.
          self.out.beta_1[0]                   = -9.
        
        if len(bjetIds)>1:
          self.out.bpt_2[0]                    = event.Jet_pt[bjetIds[1]]
          self.out.beta_2[0]                   = event.Jet_eta[bjetIds[1]]
        else:
          self.out.bpt_2[0]                    = -9.
          self.out.beta_2[0]                   = -9.
        
        
        self.out.njets[0]                      = len(jetIds)
        self.out.nfjets[0]                     = nfjets
        self.out.ncjets[0]                     = ncjets
        self.out.nbtag[0]                      = nbtag
        
        self.out.pfmt_1[0]                     = math.sqrt( 2 * self.out.pt_1[0] * self.out.met[0] * ( 1 - math.cos(deltaPhi(self.out.phi_1[0], self.out.metphi[0])) ) );
        self.out.pfmt_2[0]                     = math.sqrt( 2 * self.out.pt_2[0] * self.out.met[0] * ( 1 - math.cos(deltaPhi(self.out.phi_2[0], self.out.metphi[0])) ) );
        
        self.out.m_vis[0]                      = (muon1 + muon2).M()
        self.out.pt_ll[0]                      = (muon1 + muon2).Pt()
        self.out.dR_ll[0]                      = muon1.DeltaR(muon2)
        self.out.dphi_ll[0]                    = deltaPhi(self.out.phi_1[0], self.out.phi_2[0])
        
        
        # PZETA
        leg1     = ROOT.TVector3(muon1.Px(), muon1.Py(), 0.)
        leg2     = ROOT.TVector3(muon2.Px(), muon2.Py(), 0.)
        met_tlv  = ROOT.TLorentzVector()
        met_tlv.SetPxPyPzE(self.out.met[0]*math.cos(self.out.metphi[0]), self.out.met[0]*math.cos(self.out.metphi[0]), 0, self.out.met[0])
        metleg   = met_tlv.Vect()
        zetaAxis = ROOT.TVector3(leg1.Unit() + leg2.Unit()).Unit()
        pzetaVis = leg1*zetaAxis + leg2*zetaAxis
        pzetaMET = metleg*zetaAxis
        self.out.pzetamiss[0]  = pzetaMET
        self.out.pzetavis[0]   = pzetaVis
        self.out.dzeta[0]      = pzetaMET - 0.85*pzetaVis
        
        
        # VETOS
        self.out.extramuon_veto[0], self.out.extraelec_veto[0], self.out.dilepton_veto[0] = extraLeptonVetos(event, [dilepton.id1, dilepton.id2], [-1], self.channel)
        self.out.lepton_vetos[0] = self.out.extramuon_veto[0] or self.out.extraelec_veto[0] or self.out.dilepton_veto[0]
        
        
        # WEIGHTS
        if not self.isData:
          if self.doZpt:
            zboson = getZPTMass(event)
            self.out.m_genboson[0]    = zboson.M()
            self.out.pt_genboson[0]   = zboson.Pt()
            self.out.zptweight[0]     = self.recoilTool.getZptWeight(zboson.Pt(),zboson.M())
          if self.doTTpt:
            toppt1, toppt2 = getTTPTMass(event)
            self.out.ttptweight[0]    = self.recoilTool.getTTptWeight(toppt1,toppt2)
          self.out.genweight[0]       = event.genWeight
          self.out.puweight[0]        = self.puTool.getWeight(event.Pileup_nTrueInt)
          self.out.trigweight[0]      = self.muSFs.getTriggerSF(self.out.pt_1[0],self.out.eta_1[0])
          self.out.idisoweight_1[0]   = self.muSFs.getIdIsoSF(self.out.pt_1[0],self.out.eta_1[0])
          self.out.idisoweight_2[0]   = self.muSFs.getIdIsoSF(self.out.pt_2[0],self.out.eta_2[0])
          self.out.btagweight[0]      = self.btagTool.getWeight(event,jetIds)
          self.out.btagweight_deep[0] = self.btagTool_deep.getWeight(event,jetIds)
          self.out.weight[0]          = self.out.genweight[0]*self.out.puweight[0]*self.out.trigweight[0]*self.out.idisoweight_1[0]*self.out.idisoweight_2[0]
        
        
        self.out.tree.Fill() 
        return True
