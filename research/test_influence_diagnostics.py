import unittest
import numpy as np
from influence_diagnostics import weighted_constant, leave_one_out_constant, contrast_windows

class TestInfluence(unittest.TestCase):
    def test_constant(self):
        mu,err,chi,dof=weighted_constant([3,3,3],[1,2,3])
        self.assertAlmostEqual(mu,3)
        self.assertAlmostEqual(chi,0)
        self.assertEqual(dof,2)
        self.assertGreater(err,0)
    def test_loo_matches_bruteforce(self):
        y=np.array([1.,2.,1.5,8.,2.2,2.1]); s=np.array([.2,.3,.4,.5,.3,.2])
        means,chis,dofs=leave_one_out_constant(y,s)
        for i in range(len(y)):
            mask=np.arange(len(y))!=i
            mu,_,chi,dof=weighted_constant(y[mask],s[mask])
            self.assertAlmostEqual(means[i],mu,places=10)
            self.assertAlmostEqual(chis[i],chi,places=9)
            self.assertEqual(dofs[i],dof)
    def test_contrast(self):
        lam=np.arange(8,dtype=float)
        delta,err=contrast_windows(lam,np.array([2]*4+[5]*4),np.ones(8),(4,7),(0,3))
        self.assertAlmostEqual(delta,3)
        self.assertAlmostEqual(err,np.sqrt(.5))
    def test_overlap_rejected(self):
        with self.assertRaises(ValueError):
            contrast_windows(np.arange(5),np.ones(5),np.ones(5),(0,3),(2,4))
    def test_nonpositive_error(self):
        with self.assertRaises(ValueError):
            weighted_constant([1,2],[0,1])
if __name__=='__main__':unittest.main()
