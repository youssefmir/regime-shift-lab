"""Monthly allocation research with delayed execution and explicit turnover costs.

Signals are known at month-end t; rebalance at next trading day's close.
New weights first earn the subsequent close-to-close return. Holdings drift daily.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd

ASSETS = ['SPY', 'IEF', 'GLD', 'SHY']

@dataclass(frozen=True)
class Config:
    momentum: int = 126
    correlation: int = 63
    volatility: int = 63
    top_n: int = 2
    cost_bps: float = 10.0
    regime_filter: bool = True
    start: str = '2007-01-01'


def validate(prices):
    if list(prices.columns) != ASSETS:
        raise ValueError('Expected columns SPY, IEF, GLD, SHY in that order')
    if prices.index.has_duplicates or not prices.index.is_monotonic_increasing:
        raise ValueError('Dates must be unique and sorted')
    if not np.isfinite(prices.values).all() or (prices <= 0).any().any():
        raise ValueError('Prices must be finite, strictly positive, without gaps')


def targets(prices, cfg):
    """Rank positive 6-month momentum, use inverse volatility, fallback to SHY.

    If trailing stock/bond return correlation is positive, exclude IEF from
    defensive candidates. This is a predeclared hypothesis, not a fitted classifier.
    """
    returns = prices.pct_change(fill_method=None)
    mom = prices.pct_change(cfg.momentum, fill_method=None)
    vol = returns.rolling(cfg.volatility).std()
    corr = returns.SPY.rolling(cfg.correlation).corr(returns.IEF)
    signals={}
    for i in range(max(cfg.momentum, cfg.correlation, cfg.volatility), len(prices)-1):
        date = prices.index[i]
        if date.to_period('M') == prices.index[i+1].to_period('M'):
            continue
        pool = ['SPY','IEF','GLD']
        if cfg.regime_filter and corr.iloc[i] > 0:
            pool.remove('IEF')
        selected = [a for a in pool if mom[a].iloc[i] > 0 and vol[a].iloc[i] > 0]
        selected = sorted(selected, key=lambda a: (-mom[a].iloc[i], a))[:cfg.top_n]
        w = pd.Series(0., index=ASSETS)
        if selected:
            inv=1/vol.loc[date, selected]; w.loc[selected]=inv/inv.sum()
        else:
            w.SHY=1.
        # Trade only at the NEXT close; returns on that day belong to old holdings.
        signals[prices.index[i+1]] = w
    return signals, corr


def simulate(prices, signals, start, cost_bps):
    """Self-financing daily accounting, including drift and one-way notional costs.

    cash before the first trade earns zero. Full replacement incurs 200% gross
    turnover (sell + buy). Fees apply to both legs. No leverage, shorts, borrowing,
    taxes or intraday execution model. Trading at adjusted close is a simplification.
    """
    if cost_bps < 0: raise ValueError('Costs must be nonnegative')
    returns = prices.pct_change(fill_method=None).fillna(0)
    holdings = pd.Series(0., index=ASSETS); cash=1.; records=[]
    for date,row in returns.loc[start:].iterrows():
        holdings *= 1+row
        pre = float(holdings.sum()+cash)
        turnover=0.; fee=0.
        if date in signals:
            target=signals[date]
            turnover=float((target-holdings/pre).abs().sum())
            fee=pre*turnover*cost_bps/10000
            holdings=target*(pre-fee); cash=0.
        equity=float(holdings.sum()+cash)
        record={'date':date,'equity':equity,'turnover':turnover,'fee':fee}
        record.update({f'w_{a}': float(holdings[a]/equity) for a in ASSETS})
        records.append(record)
    return pd.DataFrame(records).set_index('date')


def metrics(equity):
    equity=equity.dropna()
    if len(equity)<2: return None
    # Start-of-period capital is 1; caller normalizes subperiods at prior close.
    r=equity.pct_change().dropna(); years=(equity.index[-1]-equity.index[0]).days/365.25
    volatility=float(r.std(ddof=1)*np.sqrt(252))
    return {'cagr':float((equity.iloc[-1]/equity.iloc[0])**(1/years)-1),
            'volatility':volatility,'sharpe_zero_rf':float(r.mean()/r.std(ddof=1)*np.sqrt(252)) if volatility else None,
            'max_drawdown':float((equity/equity.cummax()-1).min()),
            'total_return':float(equity.iloc[-1]/equity.iloc[0]-1)}


def run(prices, cfg=Config()):
    validate(prices)
    if cfg.momentum < 2 or cfg.correlation < 2 or cfg.volatility < 2 or cfg.top_n not in (1,2,3):
        raise ValueError('Invalid lookbacks or selection count')
    signal,corr=targets(prices,cfg)
    strategy=simulate(prices,signal,cfg.start,cfg.cost_bps)
    fixed={}
    for date in signal:
        w=pd.Series([.6,.4,0,0],index=ASSETS); fixed[date]=w
    benchmark=simulate(prices,fixed,cfg.start,cfg.cost_bps)
    return strategy,benchmark,corr


def export(prices, output, site):
    cfg=Config(); s,b,corr=run(prices,cfg)
    # Same evaluation start after warmup, excluding the initial no-exposure interval.
    first=next(d for d in s.index if s.loc[d,'w_SPY':].sum()>0)
    # Include previous close at equity=1 so the opening fee is represented.
    loc=max(0,s.index.get_loc(first)-1); s=s.iloc[loc:]; b=b.loc[s.index]
    periods={}
    for name,start,end in [('full',None,None),('development','2007','2017'),('validation','2018','2021'),('evaluation','2022',None)]:
        ss=s.loc[start:end]; bb=b.loc[start:end]
        if len(ss)>1: periods[name]={'start':str(ss.index[0].date()),'end':str(ss.index[-1].date()),'strategy':metrics(ss.equity),'benchmark':metrics(bb.equity)}
    sensitivity=[]
    for lookback in (63,126,252):
        for cost in (0,10,25):
            x,y,_=run(prices,Config(momentum=lookback,cost_bps=cost))
            sensitivity.append({'momentum_days':lookback,'cost_bps':cost,**metrics(x.loc['2022':].equity)})
    ablation,_,_=run(prices,Config(regime_filter=False))
    monthly=s.equity.resample('ME').last().pct_change().dropna()
    payload={'title':'Regime Shift Lab','data_start':str(prices.index[0].date()),'data_end':str(prices.index[-1].date()),
             'config':cfg.__dict__,'periods':periods,'sensitivity':sensitivity,
             'ablation_evaluation':metrics(ablation.loc['2022':].equity),
             'caveat':'Retrospective study designed in November 2026. Evaluation is a chronological holdout, not a prospective untouched test. No claims of live performance.',
             'monthly_returns':[{'date':str(d.date()),'value':float(v)} for d,v in monthly.items()],
             'series':[{'date':str(d.date()),'strategy':float(s.loc[d,'equity']),'benchmark':float(b.loc[d,'equity']),
                        'correlation':None if pd.isna(corr.loc[d]) else float(corr.loc[d]),
                        'weights':{a:float(s.loc[d,f'w_{a}']) for a in ASSETS}} for d in s.index]}
    Path(output).mkdir(parents=True,exist_ok=True); Path(site).mkdir(parents=True,exist_ok=True)
    s.to_csv(Path(output)/'strategy.csv'); b.to_csv(Path(output)/'benchmark.csv')
    for dest in [Path(output)/'results.json',Path(site)/'results.json']:
        dest.write_text(json.dumps(payload,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    print(json.dumps(periods,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--prices',default='data/prices.csv'); p.add_argument('--output',default='reports'); p.add_argument('--site',default='site'); a=p.parse_args()
    export(pd.read_csv(a.prices,index_col=0,parse_dates=True),a.output,a.site)
