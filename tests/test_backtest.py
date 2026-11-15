import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
from backtest import ASSETS, Config, targets, simulate, run, validate

class BacktestTests(unittest.TestCase):
    def prices(self):
        dates=pd.bdate_range('2020-01-01', periods=420)
        rng=np.random.default_rng(42)
        return pd.DataFrame(100*np.exp(np.cumsum(rng.normal(.0003,.01,(420,4)),axis=0)),index=dates,columns=ASSETS)

    def test_future_prices_do_not_change_past_signals_or_equity(self):
        p=self.prices(); altered=p.copy(); altered.iloc[300:]*=2
        cfg=Config(start='2020-01-01',momentum=63)
        a,_,_=run(p,cfg); b,_,_=run(altered,cfg)
        pd.testing.assert_frame_equal(a.iloc[:300],b.iloc[:300])

    def test_new_position_cannot_earn_execution_day_return(self):
        p=self.prices().iloc[:3].copy(); p.loc[:,:]=100; p.iloc[1,0]=200; p.iloc[2,0]=220
        w=pd.Series([1.,0,0,0],index=ASSETS)
        r=simulate(p,{p.index[1]:w},str(p.index[0].date()),0)
        self.assertAlmostEqual(r.equity.iloc[1],1)
        self.assertAlmostEqual(r.equity.iloc[2],1.1)

    def test_costs_charge_both_replacement_legs(self):
        p=self.prices().iloc[:3].copy(); p.loc[:,:]=100
        a=pd.Series([1.,0,0,0],index=ASSETS); b=pd.Series([0,1.,0,0],index=ASSETS)
        r=simulate(p,{p.index[0]:a,p.index[1]:b},str(p.index[0].date()),10)
        self.assertAlmostEqual(r.turnover.iloc[1],2)
        self.assertAlmostEqual(r.equity.iloc[-1],.999*.998)

    def test_long_only_fully_invested_targets_and_next_day_execution(self):
        p=self.prices(); sig,_=targets(p,Config())
        for date,w in sig.items():
            self.assertAlmostEqual(w.sum(),1); self.assertTrue((w>=0).all())
            i=p.index.get_loc(date)
            self.assertNotEqual(p.index[i-1].month,date.month)

    def test_negative_momentum_falls_back_to_short_treasuries(self):
        p=self.prices(); p.loc[:,:]=100*np.exp(-np.arange(len(p))[:,None]*.001)
        sig,_=targets(p,Config()); self.assertTrue(all(w.SHY==1 for w in sig.values()))

    def test_nonpositive_or_duplicate_prices_rejected(self):
        p=self.prices(); p.iloc[2,1]=0
        with self.assertRaises(ValueError): validate(p)
        p=self.prices(); p.index=[p.index[0]]*len(p)
        with self.assertRaises(ValueError): validate(p)

    def test_larger_costs_never_increase_terminal_wealth(self):
        p=self.prices(); a,_,_=run(p,Config(start='2020')); b,_,_=run(p,Config(start='2020',cost_bps=25))
        self.assertLessEqual(b.equity.iloc[-1],a.equity.iloc[-1])

if __name__=='__main__': unittest.main()
