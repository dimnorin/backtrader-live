import os, time
import ccxt
from datetime import datetime, timedelta, timezone
import math
import argparse
import pandas as pd
from time import sleep
import utils.util as utils


class Dump():
    def __init__(self, exchange, symbol):
        self.symbol = symbol
        self.exchange = self._init_exchange(exchange)

    def get_data(self, timeframe, sinceDays, use_cache=True):
        self._validate_timeframe(timeframe)
        symbol_out = self.symbol.replace("/", "")
        filename = '{}-{}-{}-{}.csv'.format(self.exchange, symbol_out, timeframe, sinceDays)
        filename = os.path.join(utils.get_project_root(), 'data', filename)
        if use_cache:
            if os.path.exists(filename):
                if self._is_1day_old(filename):
                    os.remove(filename)
                else:
                    return pd.read_csv(filename,
                         header=0,
                         index_col='Timestamp',
                         parse_dates=['Timestamp'],
                         # date_parser=lambda x: pd.to_datetime(int(x),unit='s')
                         )
        df = self._download_data(timeframe, sinceDays)
        df.to_csv(filename)
        return df

    def _download_data(self, timeframe, sinceDays):
        sinceDays_in_min = sinceDays * 24 * 60
        limitDelta = frame_to_minutes(timeframe) * 1000
        iterations = math.ceil(sinceDays_in_min / limitDelta)  # ceil is a round up
        data = list()
        for i in range(1, iterations+1):
            minutes = sinceDays_in_min - i * limitDelta if i * limitDelta < sinceDays_in_min else sinceDays_in_min
            # Get data
            since = int((datetime.now() + timedelta(minutes=-minutes)).timestamp() * 1000)
            data += self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=1000)
            sleep(0.5)  # sleep to not overload exchange
        header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = pd.DataFrame(data, columns=header)
        df['Timestamp'] = df['Timestamp'].apply(lambda x: pd.to_datetime(int(x) / 1000,unit='s')).sort_values()
        df = df.set_index('Timestamp')
        df.sort_index(inplace=True)
        return df

    def _init_exchange(self, exchange_name):
        # Get our Exchange
        try:
            exchange = getattr(ccxt, exchange_name)()
        except AttributeError:
            raise AttributeError('Exchange "{}" not found. Please check the exchange is supported.'.format(args.exchange))

        # Check if fetching of OHLC Data is supported
        if exchange.has["fetchOHLCV"] != True:
            raise AttributeError('{} does not support fetching OHLC data. Please use another exchange'.format(args.exchange))

        return exchange

    def _validate_timeframe(self, timeframe):
        # Check requested timeframe is available. If not return a helpful error.
        if (not hasattr(self.exchange, 'timeframes')) or (timeframe not in self.exchange.timeframes):
            err = 'The requested timeframe ({}) is not available from {}\n'.format(args.timeframe, args.exchange)
            err += '\nAvailable timeframes are:'
            for key in self.exchange.timeframes.keys():
                err += '\n\t- ' + key
            raise AttributeError(err)

    def _is_1day_old(self, filepath):
        sec = round(time.time() - utils.file_mtime(filepath))
        return sec / (60 * 60 * 24) > 1

def parse_args():
    parser = argparse.ArgumentParser(description='CCXT Market Data Downloader')


    parser.add_argument('-s','--symbol',
                        type=str,
                        required=True,
                        help='The Symbol of the Instrument/Currency Pair To Download')

    parser.add_argument('-e','--exchange',
                        type=str,
                        required=True,
                        help='The exchange to download from')

    parser.add_argument('-t','--timeframe',
                        type=str,
                        default='1d',
                        choices=['1m', '5m','15m', '30m','1h', '2h', '3h', '4h', '6h', '12h', '1d', '1M', '1y'],
                        help='The timeframe to download')

    parser.add_argument('-sd', '--sinceDays',
                        type=int,
                        default=1,
                        help='How many days to download from')


    parser.add_argument('--debug',
                            action ='store_true',
                            help=('Print Sizer Debugs'))

    return parser.parse_args()

def frame_to_minutes(frame):
    multi = 1
    if frame.endswith('h'): multi = 60
    return int(frame[:-1]) * multi

if __name__ == '__main__':
    # Get our arguments
    args = parse_args()

    Dump(args.exchange, args.symbol).get_data(args.timeframe, args.sinceDays)

