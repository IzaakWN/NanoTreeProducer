import ROOT
import math 
import numpy as num 



class TreeProducerCommon(object):

    def __init__(self, name):

        print 'TreeProducerCommon is called', name

        # create file
        self.outputfile = ROOT.TFile(name, 'recreate')
        self.tree = ROOT.TTree('tree','tree')

        # histogram for cutflow
        self.h_cutflow = ROOT.TH1F("h_cutflow", "h_cutflow", 50, 0, 50)

        
        ##################
        # event variables
        ##################

        self.run                        = num.zeros(1, dtype=int)
        self.luminosityBlock            = num.zeros(1, dtype=int)        
        self.event                      = num.zeros(1, dtype=int)
        self.MET_pt                     = num.zeros(1, dtype=float)
        self.MET_phi                    = num.zeros(1, dtype=float)
        self.GenMET_pt                  = num.zeros(1, dtype=float)
        self.GenMET_phi                 = num.zeros(1, dtype=float)
        self.PuppiMET_pt                = num.zeros(1, dtype=float)
        self.PuppiMET_phi               = num.zeros(1, dtype=float)
        self.MET_significance           = num.zeros(1, dtype=float)
        self.MET_covXX                  = num.zeros(1, dtype=float)
        self.MET_covXY                  = num.zeros(1, dtype=float)
        self.MET_covYY                  = num.zeros(1, dtype=float)
        self.nPU                        = num.zeros(1, dtype=int)
        self.nTrueInt                   = num.zeros(1, dtype=int)
        self.npvs                       = num.zeros(1, dtype=int)
        self.npvsGood                   = num.zeros(1, dtype=int)
        self.fixedGridRhoFastjetAll     = num.zeros(1, dtype=float)
        self.LHE_Njets                  = num.zeros(1, dtype=int)
        self.isData                     = num.zeros(1, dtype=int)
        self.genWeight                  = num.zeros(1, dtype=float)
        self.weight                     = num.zeros(1, dtype=float)
        self.trigweight                 = num.zeros(1, dtype=float)
        self.puweight                   = num.zeros(1, dtype=float)
        self.isisoweight_1              = num.zeros(1, dtype=float)
        self.isisoweight_2              = num.zeros(1, dtype=float)
        
        self.tree.Branch('run'                       , self.run, 'run/I')
        self.tree.Branch('luminosityBlock'           , self.luminosityBlock, 'luminosityBlock/I')
        self.tree.Branch('event'                     , self.event, 'event/I')
        self.tree.Branch('MET_pt'                    , self.MET_pt, 'MET_pt/D')
        self.tree.Branch('MET_phi'                   , self.MET_phi, 'MET_phi/D')
        self.tree.Branch('GenMET_pt'                 , self.GenMET_pt, 'GenMET_pt/D')
        self.tree.Branch('GenMET_phi'                , self.GenMET_phi, 'GenMET_phi/D')
        self.tree.Branch('PuppiMET_pt'               , self.PuppiMET_pt, 'PuppiMET_pt/D')
        self.tree.Branch('PuppiMET_phi'              , self.PuppiMET_phi, 'PuppiMET_phi/D')
        self.tree.Branch('MET_significance'          , self.MET_significance, 'MET_significance/D')
        self.tree.Branch('nPU'                       , self.nPU, 'nPU/I')
        self.tree.Branch('nTrueInt'                  , self.nTrueInt, 'nTrueInt/I')
        self.tree.Branch('npvs'                      , self.npvs, 'npvs/I')
        self.tree.Branch('npvsGood'                  , self.npvsGood, 'npvsGood/I')
        self.tree.Branch('fixedGridRhoFastjetAll'    , self.fixedGridRhoFastjetAll, 'fixedGridRhoFastjetAll/D')
        self.tree.Branch('LHE_Njets'                 , self.LHE_Njets, 'LHE_Njets/I')
        self.tree.Branch('isData'                    , self.isData, 'isData/I')
        self.tree.Branch('genWeight'                 , self.genWeight, 'genWeight/D')
        self.tree.Branch('weight'                    , self.weight, 'weight/D')
        self.tree.Branch('trigweight'                , self.trigweight, 'trigweight/D')
        self.tree.Branch('puweight'                  , self.puweight, 'puweight/D')
        self.tree.Branch('isisoweight_1'             , self.isisoweight_1, 'isisoweight_1/D')
        self.tree.Branch('isisoweight_2'             , self.isisoweight_2, 'isisoweight_2/D')
        
        
        self.njets                      = num.zeros(1, dtype=int)
        self.njets50                    = num.zeros(1, dtype=int)
        self.nfjets                     = num.zeros(1, dtype=int)
        self.ncjets                     = num.zeros(1, dtype=int)
        self.nbtag                      = num.zeros(1, dtype=int)
        self.pfmt_1                     = num.zeros(1, dtype=float)
        self.pfmt_2                     = num.zeros(1, dtype=float)
        
        self.jpt_1                      = num.zeros(1, dtype=float)
        self.jeta_1                     = num.zeros(1, dtype=float)
        self.jphi_1                     = num.zeros(1, dtype=float)
        self.jcsvv2_1                   = num.zeros(1, dtype=float)
        self.jdeepb_1                   = num.zeros(1, dtype=float)
        
        self.jpt_2                      = num.zeros(1, dtype=float)
        self.jeta_2                     = num.zeros(1, dtype=float)
        self.jphi_2                     = num.zeros(1, dtype=float)
        self.jcsvv2_2                   = num.zeros(1, dtype=float)
        self.jdeepb_2                   = num.zeros(1, dtype=float)
        
        self.m_vis                      = num.zeros(1, dtype=float)
        self.pt_tt                      = num.zeros(1, dtype=float)
        self.dR_ll                      = num.zeros(1, dtype=float)
        self.dphi_ll                    = num.zeros(1, dtype=float)
        
        self.pzetamiss                  = num.zeros(1, dtype=float)
        self.pzetavis                   = num.zeros(1, dtype=float)
        self.pzeta_disc                 = num.zeros(1, dtype=float)
        
        self.dilepton_veto              = num.zeros(1, dtype=int)
        self.extraelec_veto             = num.zeros(1, dtype=int)
        self.extramuon_veto             = num.zeros(1, dtype=int)
        
        self.ngentauhads                = num.zeros(1, dtype=int)
        self.ngentaus                   = num.zeros(1, dtype=int)
        
        self.tree.Branch('njets'                       , self.njets, 'njets/I')
        self.tree.Branch('njets50'                     , self.njets50, 'njets50/I')
        self.tree.Branch('ncjets'                      , self.ncjets, 'ncjets/I')
        self.tree.Branch('nfjets'                      , self.nfjets, 'nfjets/I')
        self.tree.Branch('nbtag'                       , self.nbtag, 'nbtag/I')
        
        self.tree.Branch('pfmt_1'                      , self.pfmt_1, 'pfmt_1/D')
        self.tree.Branch('pfmt_2'                      , self.pfmt_2, 'pfmt_2/D')
        
        self.tree.Branch('jpt_1'                       , self.jpt_1, 'jpt_1/D')
        self.tree.Branch('jeta_1'                      , self.jeta_1, 'jeta_1/D')
        self.tree.Branch('jphi_1'                      , self.jphi_1, 'jphi_1/D')
        self.tree.Branch('jcsvv2_1'                    , self.jcsvv2_1, 'jcsvv2_1/D')
        self.tree.Branch('jdeepb_1'                    , self.jdeepb_1, 'jdeepb_1/D')
        
        self.tree.Branch('jpt_2'                       , self.jpt_2, 'jpt_2/D')
        self.tree.Branch('jeta_2'                      , self.jeta_2, 'jeta_2/D')
        self.tree.Branch('jphi_2'                      , self.jphi_2, 'jphi_2/D')
        self.tree.Branch('jcsvv2_2'                    , self.jcsvv2_2, 'jcsvv2_2/D')
        self.tree.Branch('jdeepb_2'                    , self.jdeepb_2, 'jdeepb_2/D')
        
        self.tree.Branch('m_vis'                       , self.m_vis, 'm_vis/D')
        self.tree.Branch('pt_tt'                       , self.pt_tt, 'pt_tt/D')
        self.tree.Branch('dR_ll'                       , self.dR_ll, 'dR_ll/D')
        self.tree.Branch('dphi_ll'                     , self.dphi_ll, 'dphi_ll/D')
        
        self.tree.Branch('pzetamiss'                   , self.pzetamiss, 'pzetamiss/D')
        self.tree.Branch('pzetavis'                    , self.pzetavis, 'pzetavis/D')
        self.tree.Branch('pzeta_disc'                  , self.pzeta_disc, 'pzeta_disc/D')
        
        self.tree.Branch('dilepton_veto'               , self.dilepton_veto, 'dilepton_veto/I')
        self.tree.Branch('extraelec_veto'              , self.extraelec_veto, 'extraelec_veto/I')
        self.tree.Branch('extramuon_veto'              , self.extramuon_veto, 'extramuon_veto/I')
        
        self.tree.Branch('ngentauhads'                 , self.ngentauhads, 'ngentauhads/I')
        self.tree.Branch('ngentaus'                    , self.ngentaus, 'ngentaus/I')
        
        self.GenMET_pt[0]  = -1
        self.GenMET_phi[0] = -9
        self.nPU[0]        = -1
        self.nTrueInt[0]   = -1
        self.genWeight[0]  =  1
        self.LHE_Njets[0]  = -1
        


class DiLeptonBasicClass:
    def __init__(self, id1, pt1, iso1, id2, pt2, iso2):
        self.id1  = id1
        self.id2  = id2
        self.pt1  = pt1
        self.pt2  = pt2
        self.iso1 = iso1
        self.iso2 = iso2
        
    def __gt__(self, odilep):
        """Order dilepton pairs according to the pT of both objects first, then in isolation."""
        if   self.pt1  != odilep.pt1:  return self.pt1  > odilep.pt1  # greater = higher pT
        elif self.pt2  != odilep.pt2:  return self.pt2  > odilep.pt2  # greater = higher pT
        elif self.iso1 != odilep.iso1: return self.iso1 < odilep.iso1 # greater = smaller isolation
        elif self.iso2 != odilep.iso2: return self.iso2 < odilep.iso2 # greater = smaller isolation
        return True
    
class LeptonTauPair(DiLeptonBasicClass):
    def __gt__(self, oltau):
        """Override for tau isolation."""
        if   self.pt1  != oltau.pt1:  return self.pt1  > oltau.pt1  # greater = higher pT
        elif self.pt2  != oltau.pt2:  return self.pt2  > oltau.pt2  # greater = higher pT
        elif self.iso1 != oltau.iso1: return self.iso1 > oltau.iso1 # greater = larger tau isolation
        elif self.iso2 != oltau.iso2: return self.iso2 < oltau.iso2 # greater = smaller lepton isolation
        return True
    
class DiTauPair(DiLeptonBasicClass):
    def __gt__(self, oditau):
        """Override for tau isolation."""
        if   self.pt1  != oditau.pt1:  return self.pt1  > oditau.pt1  # greater = higher pT
        elif self.pt2  != oditau.pt2:  return self.pt2  > oditau.pt2  # greater = higher pT
        elif self.iso1 != oditau.iso1: return self.iso1 > oditau.iso1 # greater = smaller lepton isolation
        elif self.iso2 != oditau.iso2: return self.iso2 > oditau.iso2 # greater = larger tau isolation
        return True
    


def bestDiLepton(diLeptons):
    """Take best dilepton pair."""
    
    if len(diLeptons)==1:
        return diLeptons[0]
        
    #least_iso_highest_pt = lambda dl: (-dl.tau1_pt, -dl.tau2_pt, dl.tau2_iso, -dl.tau1_iso)
    #return sorted(diLeptons, key=lambda dl: least_iso_highest_pt(dl), reverse=False)[0]
    return sorted(diLeptons, reverse=True)[0]
    

def deltaR2( e1, p1, e2, p2):
    de = e1 - e2
    dp = deltaPhi(p1, p2)
    return de*de + dp*dp


def deltaR( *args ):
    return math.sqrt( deltaR2(*args) )


def deltaPhi( p1, p2):
    """Computes delta phi, handling periodic limit conditions."""
    res = p1 - p2
    while res > math.pi:
      res -= 2*math.pi
    while res < -math.pi:
      res += 2*math.pi
    return res
    

def extraLeptonVetos(event, muon_idxs, electron_idxs, name):
    
    b_dilepton_veto_  = False;
    b_extraelec_veto_ = False;
    b_extramuon_veto_ = False;
    
    LooseMuons = [ ]
    for imuon in range(event.nMuon):
        if event.Muon_pt[imuon] < 10: continue
        if abs(event.Muon_eta[imuon]) > 2.4: continue
        if abs(event.Muon_dz[imuon]) > 0.2: continue
        if abs(event.Muon_dxy[imuon]) > 0.045: continue
        if event.Muon_pfRelIso04_all[imuon] > 0.3: continue
        if event.Muon_mediumId[imuon] > 0.5 and (imuon not in muon_idxs):
            b_extramuon_veto_ = True
        if event.Muon_pt[imuon] > 15 and event.Muon_isPFcand[imuon] > 0.5:
            LooseMuons.append(imuon)
    
    LooseElectrons = [ ]
    for ielectron in range(event.nElectron):
        if event.Electron_pt[ielectron] < 10: continue
        if abs(event.Electron_eta[ielectron]) > 2.5: continue
        if abs(event.Electron_dz[ielectron]) > 0.2: continue
        if abs(event.Electron_dxy[ielectron]) > 0.045: continue
        if event.Electron_pfRelIso03_all[ielectron] > 0.3: continue
        if event.Electron_convVeto[ielectron] ==1 and ord(event.Electron_lostHits[ielectron]) <= 1 and event.Electron_mvaFall17Iso_WP90[ielectron] > 0.5 and (ielectron not in electron_idxs):
            b_extraelec_veto_ = True
        if event.Electron_pt[ielectron] > 15 and event.Electron_mvaFall17Iso_WPL[ielectron] > 0.5:
            LooseElectrons.append(ielectron)
    
    if name.find('mutau')!=-1:
      for idx1 in LooseMuons:
        for idx2 in LooseMuons:
            if idx1 >= idx2: continue 
            dR = deltaR(event.Muon_eta[idx1], event.Muon_phi[idx1], 
                        event.Muon_eta[idx2], event.Muon_phi[idx2])
            if event.Muon_charge[idx1] * event.Muon_charge[idx2] < 0 and dR > 0.15:
                b_dilepton_veto_ = True
    
    if name.find('eletau')!=-1:
      for idx1 in LooseElectrons:
        for idx2 in LooseElectrons:
            if idx1 >= idx2: continue 
            dR = deltaR(event.Electron_eta[idx1], event.Electron_phi[idx1], 
                        event.Electron_eta[idx2], event.Electron_phi[idx2])
            if event.Electron_charge[idx1] * event.Electron_charge[idx2] < 0 and dR > 0.15:
                b_dilepton_veto_ = True
    
    return b_extramuon_veto_, b_extraelec_veto_, b_dilepton_veto_

#  b_dilepton_veto[ch]                   = (int) b_dilepton_veto_;
#  b_extraelec_veto[ch]                  = (int) b_extraelec_veto_;
#  b_extramuon_veto[ch]                  = (int) b_extramuon_veto_;
#  b_lepton_vetos[ch]                    = ( b_dilepton_veto_ || b_extraelec_veto_ || b_extramuon_veto_ );


