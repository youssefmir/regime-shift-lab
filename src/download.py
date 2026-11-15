"""Download adjusted daily ETF closes; keep an auditable, dated local snapshot."""
from pathlib import Path
import argparse, hashlib, json
from datetime import datetime, timezone
import yfinance as yf

TICKERS = ['SPY', 'IEF', 'GLD', 'SHY']

def download(destination, end):
    data = yf.download(TICKERS, start='2006-01-01', end=end, auto_adjust=True, progress=False, threads=False)['Close']
    data = data.reindex(columns=TICKERS).dropna()
    if len(data) < 500:
        raise RuntimeError('Incomplete price download; refusing to replace the snapshot')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(destination, index_label='Date', float_format='%.8f')
    manifest = {'source': 'Yahoo Finance via yfinance, auto_adjust=True', 'tickers': TICKERS,
                'downloaded_at': datetime.now(timezone.utc).isoformat(), 'requested_end_exclusive': end,
                'start': str(data.index[0].date()), 'end': str(data.index[-1].date()),
                'rows': len(data), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                'notes': 'Adjusted closes include distribution/split adjustments; historical revisions are possible. USD, no FX conversion.'}
    destination.with_suffix('.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--end', default='2026-11-15'); p.add_argument('--output', default='data/prices.csv')
    a=p.parse_args(); download(a.output, a.end)
