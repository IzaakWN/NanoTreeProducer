import ROOT
import math 
import numpy as num 

from TreeProducerCommon import *

class TreeProducerMuMu(TreeProducerCommon):

    def __init__(self, name):

        super(TreeProducerMuMu, self).__init__(name)
        print 'TreeProducerMuMu is called', name
        
        
        ##############
        #   MUON 1   #
        ##############
        
        self.pt_1                           = num.zeros(1, dtype=float)
        self.eta_1                          = num.zeros(1, dtype=float)
        self.phi_1                          = num.zeros(1, dtype=float)
        self.m_1                            = num.zeros(1, dtype=float)
        self.dxy_1                          = num.zeros(1, dtype=float)
        self.dz_1                           = num.zeros(1, dtype=float)        
        self.pfRelIso04_all_1               = num.zeros(1, dtype=float)
        self.q_1                            = num.zeros(1, dtype=int)
        self.genPartFlav_1                  = num.zeros(1, dtype=int)

        self.tree.Branch('pt_1',                 self.pt_1, 'pt_1/D')
        self.tree.Branch('eta_1',                self.eta_1, 'eta_1/D')
        self.tree.Branch('phi_1',                self.phi_1, 'phi_1/D')
        self.tree.Branch('m_1',                  self.m_1, 'm_1/D')
        self.tree.Branch('dxy_1',                self.dxy_1, 'dxy_1/D')
        self.tree.Branch('dz_1',                 self.dz_1, 'dz_1/D')
        self.tree.Branch('q_1',                  self.q_1, 'q_1/I')
        self.tree.Branch('pfRelIso04_all_1',     self.pfRelIso04_all_1, 'pfRelIso04_all_1/D')
        self.tree.Branch('genPartFlav_1',        self.genPartFlav_1, 'genPartFlav_1/I')
        
        
        ##############
        #   MUON 2   #
        ##############
        
        self.pt_2                           = num.zeros(1, dtype=float)
        self.eta_2                          = num.zeros(1, dtype=float)
        self.phi_2                          = num.zeros(1, dtype=float)
        self.m_2                            = num.zeros(1, dtype=float)
        self.dxy_2                          = num.zeros(1, dtype=float)
        self.dz_2                           = num.zeros(1, dtype=float)        
        self.pfRelIso04_all_2               = num.zeros(1, dtype=float)
        self.q_2                            = num.zeros(1, dtype=int)
        self.genPartFlav_2                  = num.zeros(1, dtype=int)

        self.tree.Branch('pt_2',                 self.pt_2, 'pt_2/D')
        self.tree.Branch('eta_2',                self.eta_2, 'eta_2/D')
        self.tree.Branch('phi_2',                self.phi_2, 'phi_2/D')
        self.tree.Branch('m_2',                  self.m_2, 'm_2/D')
        self.tree.Branch('dxy_2',                self.dxy_2, 'dxy_2/D')
        self.tree.Branch('dz_2',                 self.dz_2, 'dz_2/D')
        self.tree.Branch('q_2',                  self.q_2, 'q_2/I')
        self.tree.Branch('pfRelIso04_all_2',     self.pfRelIso04_all_2, 'pfRelIso04_all_2/D')
        self.tree.Branch('genPartFlav_2',        self.genPartFlav_2, 'genPartFlav_2/I')
        
        
        ###########
        #   TAU   #
        ###########
        
        self.pt_3                           = num.zeros(1, dtype=float)
        self.eta_3                          = num.zeros(1, dtype=float)
        self.m_3                            = num.zeros(1, dtype=float)
        self.genPartFlav_3                  = num.zeros(1, dtype=int)
        self.decayMode_3                    = num.zeros(1, dtype=int)
        self.idAntiEle_3                    = num.zeros(1, dtype=int)
        self.idAntiMu_3                     = num.zeros(1, dtype=int)
        ###self.idDecayMode_3                  = num.zeros(1, dtype=int)
        ###self.idDecayModeNewDMs_3            = num.zeros(1, dtype=int)
        self.idMVAoldDM_3                   = num.zeros(1, dtype=int)
        self.idMVAoldDM2017v1_3             = num.zeros(1, dtype=int)
        self.idMVAoldDM2017v2_3             = num.zeros(1, dtype=int)
        self.idMVAnewDM2017v2_3             = num.zeros(1, dtype=int)
        self.idIso_3                        = num.zeros(1, dtype=int)
        
        self.tree.Branch('pt_3',                 self.pt_3, 'pt_3/D')
        self.tree.Branch('eta_3',                self.eta_3, 'eta_3/D')
        self.tree.Branch('m_3',                  self.m_3, 'm_3/D')
        self.tree.Branch('genPartFlav_3',        self.genPartFlav_3, 'genPartFlav_3/I')
        self.tree.Branch('decayMode_3',          self.decayMode_3, 'decayMode_3/I')
        self.tree.Branch('idAntiEle_3',          self.idAntiEle_3, 'idAntiEle_3/I')
        self.tree.Branch('idAntiMu_3',           self.idAntiMu_3, 'idAntiMu_3/I')
        ###self.tree.Branch('idDecayMode_3',        self.idDecayMode_3, 'idDecayMode_3/I')
        ###self.tree.Branch('idDecayModeNewDMs_3',  self.idDecayModeNewDMs_3, 'idDecayModeNewDMs_3/I')
        self.tree.Branch('idMVAoldDM_3',         self.idMVAoldDM_3, 'idMVAoldDM_3/I')
        self.tree.Branch('idMVAoldDM2017v1_3',   self.idMVAoldDM2017v1_3, 'idMVAoldDM2017v1_3/I')
        self.tree.Branch('idMVAoldDM2017v2_3',   self.idMVAoldDM2017v2_3, 'idMVAoldDM2017v2_3/I')
        self.tree.Branch('idMVAnewDM2017v2_3',   self.idMVAnewDM2017v2_3, 'idMVAnewDM2017v2_3/I')
        self.tree.Branch('idIso_3',              self.idIso_3, 'idIso_3/I')
        

