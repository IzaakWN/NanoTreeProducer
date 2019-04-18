import re, math
from math import sqrt, sin, cos, pi
import ROOT
from ROOT import TTree, TH1D, TH2D, TLorentzVector, TVector3
from CorrectionTools.RecoilCorrectionTool import hasBit
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Event



def checkBranches(tree):
  """Redirect some branch names in case they are not available in some samples or nanoAOD versions."""
  branches = [
    ('Electron_mvaFall17V2Iso',        'Electron_mvaFall17Iso'       ),
    ('Electron_mvaFall17V2Iso_WPL',    'Electron_mvaFall17Iso_WPL'   ),
    ('Electron_mvaFall17V2Iso_WP80',   'Electron_mvaFall17Iso_WP80'  ),
    ('Electron_mvaFall17V2Iso_WP90',   'Electron_mvaFall17Iso_WP90'  ),
    ('Electron_mvaFall17V2noIso_WPL',  'Electron_mvaFall17noIso_WPL' ),
    ('Electron_mvaFall17V2noIso_WP80', 'Electron_mvaFall17noIso_WP80'),
    ('Electron_mvaFall17V2noIso_WP90', 'Electron_mvaFall17noIso_WP90'),
    ('HLT_Ele32_WPTight_Gsf',           False                        ),
  ]
  fullbranchlist = tree.GetListOfBranches()
  for newbranch, oldbranch in branches:
    if newbranch not in fullbranchlist:
      if isinstance(oldbranch,str):
        print "checkBranches: directing '%s' -> '%s'"%(newbranch,oldbranch)
        exec "setattr(Event,newbranch,property(lambda self: self._tree.readBranch('%s')))"%oldbranch
      else:
        print "checkBranches: directing '%s' -> %s"%(newbranch,oldbranch)
        exec "setattr(Event,newbranch,%s)"%(oldbranch)
    


def setBranchStatuses(tree,otherbranches=[ ]):
  """Activate or deactivate branch statuses for better performance."""
  tree.SetBranchStatus('*',0)
  branches = [
   'run', 'luminosityBlock', 'event', 'PV_*', 'Pileup_*', 'Flag_*', 'HLT_*',
   'LHE_*', 'nGenPart', 'GenPart_*', 'GenMET_*', 'nGenVisTau', 'GenVisTau_*', 'genWeight',
   'nElectron', 'Electron_*', 'nMuon', 'Muon_*', 'nTau', 'Tau_*',
   'nJet', 'Jet_*', 'MET_*',
  ]
  for branchname in branches+otherbranches:
   tree.SetBranchStatus(branchname,1)
  


def getVLooseTauIso(year):
  """Return a method to check whether event passes the VLoose working
  point of all available tau IDs. (For tau ID measurement.)"""
  return lambda e,i: ord(e.Tau_idMVAoldDM[i])>0 or ord(e.Tau_idMVAnewDM2017v2[i])>0 or ord(e.Tau_idMVAoldDM2017v1[i])>0 or ord(e.Tau_idMVAoldDM2017v2[i])>0
  


def getMET(year):
  """Return year-dependent MET recipe."""
  ###if year==2017:
  ###  return lambda e: TLorentzVector(e.METFixEE2017_pt*cos(e.METFixEE2017_phi),e.METFixEE2017_pt*sin(e.METFixEE2017_phi),0,e.METFixEE2017_pt)
  ###else:
  return lambda e: TLorentzVector(e.MET_pt*cos(e.MET_phi),e.MET_pt*sin(e.MET_phi),0,e.MET_pt)
  


def getMETFilters(year,isData):
  """Return a method to check if an event passes the recommended MET filters."""
  if year==2018:
    if isData:
      return lambda e: e.Flag_goodVertices and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and e.Flag_globalSuperTightHalo2016Filter and\
                       e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadChargedCandidateFilter and e.Flag_eeBadScFilter and e.Flag_ecalBadCalibFilterV2
    else:
      return lambda e: e.Flag_goodVertices and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and\
                       e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadChargedCandidateFilter and e.Flag_ecalBadCalibFilterV2
  else:
    if isData:
      return lambda e: e.Flag_goodVertices and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and e.Flag_globalSuperTightHalo2016Filter and\
                       e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadChargedCandidateFilter and e.Flag_eeBadScFilter and e.Flag_ecalBadCalibFilter
    else:
      return lambda e: e.Flag_goodVertices and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and\
                       e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadChargedCandidateFilter and e.Flag_ecalBadCalibFilter
  


def Tau_idIso(event,i):
  raw = event.Tau_rawIso[i]
  if event.Tau_photonsOutsideSignalCone[i]/event.Tau_pt[i]<0.10:
    return 0 if raw>4.5 else 1 if raw>3.5 else 3 if raw>2.5 else 7 if raw>1.5 else 15 if raw>0.8 else 31 # VVLoose, VLoose, Loose, Medium, Tight
  return 0 if raw>4.5 else 1 if raw>3.5 else 3 # VVLoose, VLoose
  


class DiLeptonBasicClass:
    """Container class to pair and order tau decay candidates."""
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
        elif self.iso1 != oltau.iso1: return self.iso1 < oltau.iso1 # greater = smaller lepton isolation
        elif self.iso2 != oltau.iso2: return self.iso2 > oltau.iso2 # greater = larger tau isolation
        return True
    
class DiTauPair(DiLeptonBasicClass):
    def __gt__(self, oditau):
        """Override for tau isolation."""
        if   self.pt1  != oditau.pt1:  return self.pt1  > oditau.pt1  # greater = higher pT
        elif self.pt2  != oditau.pt2:  return self.pt2  > oditau.pt2  # greater = higher pT
        elif self.iso1 != oditau.iso1: return self.iso1 > oditau.iso1 # greater = larger tau isolation
        elif self.iso2 != oditau.iso2: return self.iso2 > oditau.iso2 # greater = larger tau isolation
        return True
    


def bestDiLepton(diLeptons):
    """Take best dilepton pair."""
    if len(diLeptons)==1:
        return diLeptons[0]
    #least_iso_highest_pt = lambda dl: (-dl.tau1_pt, -dl.tau2_pt, dl.tau2_iso, -dl.tau1_iso)
    #return sorted(diLeptons, key=lambda dl: least_iso_highest_pt(dl), reverse=False)[0]
    return sorted(diLeptons, reverse=True)[0]
    


def deltaR(eta1, phi1, eta2, phi2):
    """Compute DeltaR."""
    deta = eta1 - eta2
    dphi = deltaPhi(phi1, phi2)
    return sqrt( deta*deta + dphi*dphi )
    


def deltaPhi(phi1, phi2):
    """Computes Delta phi, handling periodic limit conditions."""
    res = phi1 - phi2
    while res > pi:
      res -= 2*pi
    while res < -pi:
      res += 2*pi
    return res
    


def genmatch(event,index,out=None):
    """Match reco tau to gen particles, as there is a bug in the nanoAOD matching
    for lepton to tau fakes of taus reconstructed as DM1."""
    genmatch  = 0
    dR_min    = 0.2
    particles = Collection(event,'GenPart')
    eta_reco  = event.Tau_eta[index]
    phi_reco  = event.Tau_phi[index]
    
    # lepton -> tau fakes
    for id in range(event.nGenPart):
      particle = particles[id]
      PID = abs(particle.pdgId)
      if (particle.status!=1 and PID!=13) or particle.pt<8: continue
      dR = deltaR(eta_reco,phi_reco,particle.eta,particle.phi)
      if dR<dR_min:
        if hasBit(particle.statusFlags,0): # isPrompt
          if   PID==11: genmatch = 1; dR_min = dR
          elif PID==13: genmatch = 2; dR_min = dR
        elif hasBit(particle.statusFlags,5): # isDirectPromptTauDecayProduct
          if   PID==11: genmatch = 3; dR_min = dR
          elif PID==13: genmatch = 4; dR_min = dR
    
    # real tau leptons
    for id in range(event.nGenVisTau):
      dR = deltaR(eta_reco,phi_reco,event.GenVisTau_eta[id],event.GenVisTau_phi[id])
      if dR<dR_min:
        dR_min = dR
        genmatch = 5
    
    return genmatch
    


###def genmatchCheck(event,index,out):
###    """Match reco tau to gen particles, as there is a bug in the nanoAOD matching
###    for lepton to tau fakes of taus reconstructed as DM1."""
###    #print '-'*80
###    genmatch  = 0
###    #partmatch_s1 = None
###    #partmatch_sn1 = None # status != 1
###    dR_min    = 1.0
###    particles = Collection(event,'GenPart')
###    eta_reco  = event.Tau_eta[index]
###    phi_reco  = event.Tau_phi[index]
###    
###    # lepton -> tau fakes
###    for id in range(event.nGenPart):
###      particle = particles[id]
###      PID = abs(particle.pdgId)
###      if particle.status!=1 or particle.pt<8: continue
###      #if (particle.status!=1 and PID!=13) or particle.pt<8: continue
###      dR = deltaR(eta_reco,phi_reco,particle.eta,particle.phi)
###      if dR<dR_min:
###        if hasBit(particle.statusFlags,0): # isPrompt
###          if   PID==11:
###            genmatch = 1; dR_min = dR
###            #if particle.status==1: partmatch_s1 = particle
###            #else:                  partmatch_sn1 = particle
###          elif PID==13:
###            genmatch = 2; dR_min = dR
###            #if particle.status==1: partmatch_s1 = particle
###            #else:                  partmatch_sn1 = particle
###        elif hasBit(particle.statusFlags,5): # isDirectPromptTauDecayProduct
###          if   PID==11:
###            genmatch = 3; dR_min = dR
###            #if particle.status==1: partmatch_s1 = particle
###            #else:                  partmatch_sn1 = particle
###          elif PID==13:
###            genmatch = 4; dR_min = dR
###            #if particle.status==1: partmatch_s1 = particle
###            #else:                  partmatch_sn1 = particle
###        #if particle.status!=1 and particle.status!=23:
###        # mother = abs(particles[particle.genPartIdxMother].pdgId) if hasattr(particle,'genPartIdxMother') and particle.genPartIdxMother>0 else 0
###        # print "%3d: PID=%3d, mass=%3.1f, pt=%4.1f, status=%2d, mother=%2d, statusFlags=%5d (%16s), isPrompt=%d, isDirectPromptTauDecayProduct=%d, fromHardProcess=%1d, isHardProcessTauDecayProduct=%1d, isDirectHardProcessTauDecayProduct=%1d"%\
###        # (id,particle.pdgId,particle.mass,particle.pt,particle.status,mother,particle.statusFlags,bin(particle.statusFlags),hasBit(particle.statusFlags,0),hasBit(particle.statusFlags,5),hasBit(particle.statusFlags,8),hasBit(particle.statusFlags,9),hasBit(particle.statusFlags,10))
###    
###    # real tau leptons
###    for id in range(event.nGenVisTau):
###      dR = deltaR(eta_reco,phi_reco,event.GenVisTau_eta[id],event.GenVisTau_phi[id])
###      if dR<dR_min:
###        dR_min = dR
###        genmatch = 5
###    
###    ## CHECKS
###    #if genmatch!=ord(event.Tau_genPartFlav[index]):
###    # #mother = abs(particles[partmatch_s1.genPartIdxMother].pdgId) if hasattr(partmatch_s1,'genPartIdxMother') else 0
###    # #print "gen mismatch: Tau_genPartFlav = %s, genmatch = %s, Tau_decayMode = %2s, mother = %s"%(ord(event.Tau_genPartFlav[index]),genmatch,event.Tau_decayMode[index],mother)
###    # if genmatch>0 and genmatch<5 and event.Tau_decayMode[index]==1:
###    #   if partmatch_s1:
###    #     fillFlagHistogram(out.flags_LTF_mis,partmatch_s1)
###    #   elif partmatch_sn1:
###    #     fillFlagHistogram(out.flags_LTF_mis_sn1,partmatch_sn1)
###    #
###    ## CHECK status and flags
###    #if genmatch>0 and genmatch<5:
###    # if event.Tau_decayMode[index]==0:
###    #   if partmatch_s1:
###    #     fillFlagHistogram(out.flags_LTF_DM0,partmatch_s1)       
###    #   elif partmatch_sn1:
###    #     fillFlagHistogram(out.flags_LTF_DM0_sn1,partmatch_sn1)
###    # elif event.Tau_decayMode[index]==1:
###    #   if partmatch_s1:
###    #     fillFlagHistogram(out.flags_LTF_DM1,partmatch_s1)
###    #   elif partmatch_sn1:
###    #     fillFlagHistogram(out.flags_LTF_DM1_sn1,partmatch_sn1)
###    #     #if partmatch_sn1.status not in [23,44,52]:
###    #     #  print partmatch_sn1.status
###    #
###    ## CHECK correlation
###    #out.genmatch_corr.Fill(ord(event.Tau_genPartFlav[index]),genmatch)
###    #if event.Tau_decayMode[index]==0:
###    # out.genmatch_corr_DM0.Fill(ord(event.Tau_genPartFlav[index]),genmatch)
###    #if event.Tau_decayMode[index]==1:
###    # out.genmatch_corr_DM1.Fill(ord(event.Tau_genPartFlav[index]),genmatch)
###    
###    return genmatch



###def fillFlagHistogram(hist,particle):
###  """Fill histograms with status flags for genPartFlav check."""
###  if hasBit(particle.statusFlags, 0): hist.Fill( 0) # isPrompt
###  if hasBit(particle.statusFlags, 5): hist.Fill( 1) # isDirectPromptTauDecayProduct
###  if hasBit(particle.statusFlags, 7): hist.Fill( 2) # isHardProcess
###  if hasBit(particle.statusFlags, 8): hist.Fill( 3) # fromHardProcess
###  if hasBit(particle.statusFlags,10): hist.Fill( 4) # isDirectHardProcessTauDecayProduct
###  if hasBit(particle.statusFlags,11): hist.Fill( 5) # fromHardProcessBeforeFSR
###  if hasBit(particle.statusFlags,12): hist.Fill( 6) # isFirstCopy
###  if hasBit(particle.statusFlags,13): hist.Fill( 7) # isLastCop
###  if hasBit(particle.statusFlags,14): hist.Fill( 8) # isLastCopyBeforeFSR
###  if   particle.status==1:            hist.Fill( 9) # status==1
###  elif particle.status==23:           hist.Fill(10) # status==23
###  elif particle.status==44:           hist.Fill(11) # status==44
###  elif particle.status==51:           hist.Fill(12) # status==51
###  elif particle.status==52:           hist.Fill(13) # status==52
###  else:                               hist.Fill(14) # other status
    


def extraLeptonVetos(event, muon_idxs, electron_idxs, channel):
    """Check if event has extra electrons or muons. (HTT definitions.)"""
    
    extramuon_veto = False
    extraelec_veto = False
    dilepton_veto  = False
    
    LooseMuons = [ ]
    for imuon in range(event.nMuon):
        if event.Muon_pt[imuon] < 10: continue
        if abs(event.Muon_eta[imuon]) > 2.4: continue
        if abs(event.Muon_dz[imuon]) > 0.2: continue
        if abs(event.Muon_dxy[imuon]) > 0.045: continue
        if event.Muon_pfRelIso04_all[imuon] > 0.3: continue
        if event.Muon_mediumId[imuon] and (imuon not in muon_idxs):
            extramuon_veto = True
        if event.Muon_pt[imuon] > 15 and event.Muon_isPFcand[imuon]: #Muon_isGlobal[imuon] and Muon_isTracker[imuon]
            LooseMuons.append(imuon)
    
    LooseElectrons = [ ]
    for ielectron in range(event.nElectron):
        if event.Electron_pt[ielectron] < 10: continue
        if abs(event.Electron_eta[ielectron]) > 2.5: continue
        if abs(event.Electron_dz[ielectron]) > 0.2: continue
        if abs(event.Electron_dxy[ielectron]) > 0.045: continue
        if event.Electron_pfRelIso03_all[ielectron] > 0.3: continue
        if event.Electron_convVeto[ielectron] ==1 and ord(event.Electron_lostHits[ielectron]) <= 1 and event.Electron_mvaFall17V2Iso_WP90[ielectron] and (ielectron not in electron_idxs):
            extraelec_veto = True
        if event.Electron_pt[ielectron] > 15 and event.Electron_mvaFall17V2Iso_WPL[ielectron]:
            LooseElectrons.append(ielectron)
    
    if channel=='mutau':
      for idx1 in LooseMuons:
        for idx2 in LooseMuons:
            if idx1 >= idx2: continue 
            dR = deltaR(event.Muon_eta[idx1], event.Muon_phi[idx1], 
                        event.Muon_eta[idx2], event.Muon_phi[idx2])
            if event.Muon_charge[idx1] * event.Muon_charge[idx2] < 0 and dR > 0.15:
                dilepton_veto = True
    
    if channel=='eletau':
      for idx1 in LooseElectrons:
        for idx2 in LooseElectrons:
            if idx1 >= idx2: continue 
            dR = deltaR(event.Electron_eta[idx1], event.Electron_phi[idx1], 
                        event.Electron_eta[idx2], event.Electron_phi[idx2])
            if event.Electron_charge[idx1] * event.Electron_charge[idx2] < 0 and dR > 0.15:
                dilepton_veto = True
    
    return extramuon_veto, extraelec_veto, dilepton_veto
    


def fillJetsBranches(self,event,tau1,tau2):
    """Help function to select jets and b tags, after removing overlap with tau decay candidates,
    and fill the jet variable branches."""
    
    jetIds, bjetIds = [ ], [ ]
    nfjets, ncjets  = 0, 0
    nbtag, nbtag50  = 0, 0
    nbtag_loose, nbtag50_loose = 0, 0
    
    # REMOVE OVERLAP
    jets = Collection(event,'Jet')
    #jets = filter(self.jetSel,jets)
    for ijet in range(event.nJet):
        if event.Jet_pt[ijet] < self.jetCutPt: continue
        if abs(event.Jet_eta[ijet]) > 4.7: continue
        if tau1.DeltaR(jets[ijet].p4()) < 0.5: continue
        if tau2.DeltaR(jets[ijet].p4()) < 0.5: continue
        jetIds.append(ijet)
        
        if abs(event.Jet_eta[ijet]) > 2.4:
          nfjets += 1
        else:
          ncjets += 1
        
        if event.Jet_btagDeepB[ijet] > self.deepcsv_wp.loose:
          nbtag_loose += 1
          if event.Jet_pt[ijet]>50:
            nbtag50_loose += 1
          if event.Jet_btagDeepB[ijet] > self.deepcsv_wp.medium:
            nbtag += 1
            if event.Jet_pt[ijet]>50:
              nbtag50 += 1
            bjetIds.append(ijet)
    
    # FILL BRANCHES JETS
    self.out.njets[0]         = len(jetIds)
    self.out.njets50[0]       = len([i for i in jetIds if event.Jet_pt[i]>50])
    self.out.nfjets[0]        = nfjets
    self.out.ncjets[0]        = ncjets
    self.out.nbtag[0]         = nbtag
    self.out.nbtag50[0]       = nbtag50
    self.out.nbtag_loose[0]   = nbtag_loose
    self.out.nbtag50_loose[0] = nbtag50_loose
    
    if len(jetIds)>0:
      self.out.jpt_1[0]       = event.Jet_pt[jetIds[0]]
      self.out.jeta_1[0]      = event.Jet_eta[jetIds[0]]
      self.out.jphi_1[0]      = event.Jet_phi[jetIds[0]]
      self.out.jdeepb_1[0]    = event.Jet_btagDeepB[jetIds[0]]
    else:
      self.out.jpt_1[0]       = -1.
      self.out.jeta_1[0]      = -9.
      self.out.jphi_1[0]      = -9.
      self.out.jdeepb_1[0]    = -9.
    
    if len(jetIds)>1:
      self.out.jpt_2[0]       = event.Jet_pt[jetIds[1]]
      self.out.jeta_2[0]      = event.Jet_eta[jetIds[1]]
      self.out.jphi_2[0]      = event.Jet_phi[jetIds[1]]
      self.out.jdeepb_2[0]    = event.Jet_btagDeepB[jetIds[1]]
    else:
      self.out.jpt_2[0]       = -1.
      self.out.jeta_2[0]      = -9.
      self.out.jphi_2[0]      = -9.
      self.out.jdeepb_2[0]    = -9.
    
    if len(bjetIds)>0:
      self.out.bpt_1[0]       = event.Jet_pt[bjetIds[0]]
      self.out.beta_1[0]      = event.Jet_eta[bjetIds[0]]
    else:
      self.out.bpt_1[0]       = -1.
      self.out.beta_1[0]      = -9.
    
    if len(bjetIds)>1:
      self.out.bpt_2[0]       = event.Jet_pt[bjetIds[1]]
      self.out.beta_2[0]      = event.Jet_eta[bjetIds[1]]
    else:
      self.out.bpt_2[0]       = -1.
      self.out.beta_2[0]      = -9.
    
    return jetIds
    


def countTops(event):
    """Count number of tops in a given event. (Used for LQ signal samples, with inclusive
    decays containing a b or top quark.)"""
    ntops = 0
    for id in range(event.nGenPart):
      if abs(event.GenPart_pdgId[id])==6 and hasBit(event.GenPart_statusFlags[id],13):
        ntops += 1
    return ntops
    
