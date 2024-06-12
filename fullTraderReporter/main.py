import json
from collections import defaultdict
from enum import Enum

# Specify the directory path
directory_path = 'parser/NinjaTrader/data/TradingPerformance/'

import csv
import os

import pandas as pd


class ExitType(Enum):
    STOP = "Stop"
    TAKE_PROFIT = "TP"


class EntryExit:
    relevant_columns = ['Account', 'Market pos.', 'Entry price', 'Exit price', 'Qty', 'Entry time', 'Exit time',
                        'Instrument']

    def __init__(self, account, market_position, entry_price, exit_price, qty, entry_time, exit_time, instrument):
        self.Account = account
        self.Market_pos = market_position
        self.Entry_price = entry_price
        self.Exit_price = exit_price
        self.Qty = qty
        self.Entry_time = entry_time
        self.Exit_time = exit_time
        self.Instrument = instrument

    def get_exit_type(self):
        if self.Profit > 0:
            return ExitType.TAKE_PROFIT
        else:
            return ExitType.STOP

    @property
    def Exit(self):
        return {'price': self.Exit_price, 'Qty': self.Qty, 'Pnl': self.Profit}

    @property
    def Profit(self):
        if self.Market_pos == 'Long':
            return (self.Exit_price - self.Entry_price) * self.Qty
        return -(self.Exit_price - self.Entry_price) * self.Qty
    @classmethod
    def from_csv_row(cls, csv_row):
        kwargs = {column: csv_row[column] for column in cls.relevant_columns}
        return cls(**kwargs)

    def __repr__(self):
        return f"EntryExit(Account={self.Account}, Market_pos={self.Market_pos}, Entry_price={self.Entry_price}, " \
               f"Exit_price={self.Exit_price}, Qty={self.Qty}, " \
               f"Entry_time={self.Entry_time}, Exit_time={self.Exit_time}, Instrument={self.Instrument}\n"


class Trade:
    relevant_columns = EntryExit.relevant_columns

    def __init__(self, entry_exit_objects):
        if not entry_exit_objects:
            raise ValueError("Trade must have at least one EntryExit object.")

        # Calculate total Qty
        self.Qty = sum(obj.Qty for obj in entry_exit_objects)

        # Combine Exits from all EntryExit objects into one list
        self.Exits = self.get_exits(entry_exit_objects)

        # Set other properties from the reference EntryExit object
        reference_object = entry_exit_objects[0]
        self.Account = reference_object.Account
        self.Market_pos = reference_object.Market_pos
        self.Entry_price = reference_object.Entry_price
        self.Entry_time = reference_object.Entry_time
        self.Instrument = reference_object.Instrument

    def get_exits(self, entry_exits):
        Exits = []
        if len(entry_exits) > 1:
            for i in range(len(entry_exits)):
                exit = entry_exits[i].Exit
                Exits.append(f'{entry_exits[i].get_exit_type().value}{i+1}: {exit}')
            return Exits
        else:
            close = entry_exits[0].Exit
            Exits.append(f'{entry_exits[0].get_exit_type().value} {close}')
            return Exits



    @classmethod
    def from_entry_exit_objects(cls, entry_exit_objects):
        return cls(entry_exit_objects)

    @classmethod
    def from_csv_file(cls, csv_file_path):
        entry_exit_objects = []

        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entry_exit_objects.append(EntryExit.from_csv_row(row))

        return cls.from_entry_exit_objects(entry_exit_objects)

    def __repr__(self):
        return f"Account={self.Account}, Market_pos={self.Market_pos}, Entry_price={self.Entry_price}, " \
               f"Qty={self.Qty}, Entry_time={self.Entry_time}, Instrument={self.Instrument}, " \
               f"Exits={self.Exits}\n"


def create_trades(entry_exits):
    unique_sets = {}

    for entry_exit in entry_exits:
        key = (entry_exit.Entry_time, entry_exit.Entry_price, entry_exit.Instrument)

        if key not in unique_sets:
            unique_sets[key] = [entry_exit]
        else:
            exit_index = -1
            idx = 0
            for line in unique_sets[key]:
                if line.Exit_price == entry_exit.Exit_price:
                    exit_index = idx
                idx += 1

            if exit_index < 0:
                unique_sets[key].append(entry_exit)
            else:
                unique_sets[key][exit_index].Qty += entry_exit.Qty

    trades = [Trade(entry_exit) for entry_exit in unique_sets.values()]
    return trades


def parse_ninjatrader_csv(directory_path):
    # Get a list of all files in the directory
    files = os.listdir(directory_path)

    # Filter for CSV files
    csv_files = [file for file in files if file.endswith('.csv')]

    # Check if there are any CSV files
    if not csv_files:
        print(f"No CSV files found in the specified directory: {directory_path}")
        return None

    # Select the first CSV file
    csv_file_path = os.path.join(directory_path, csv_files[0])

    # Read NinjaTrader CSV file
    df = pd.read_csv(csv_file_path)

    # Extract relevant columns
    relevant_columns = ['Account', 'Market pos.', 'Entry price', 'Exit price', 'Qty', 'Profit', 'Entry time',
                        'Exit time', 'Instrument']
    df = df[relevant_columns]

    # Create a list to store EntryExit instances
    entryexits = []

    for index, row in df.iterrows():
        # Assuming 'Qty', 'Entry price', 'Exit price' are valid numerical values
        entryexit_instance = EntryExit(
            account=row['Account'],
            instrument=row['Instrument'],
            market_position=row['Market pos.'],
            entry_price=row['Entry price'],
            exit_price=row['Exit price'],
            qty=row['Qty'],
            entry_time=row['Entry time'],
            exit_time=row['Exit time']
        )

        entryexits.append(entryexit_instance)

    return entryexits


all_entry_exits = parse_ninjatrader_csv(directory_path)
trades = create_trades(all_entry_exits)
print(trades)


# Function to convert Trade objects to a dictionary
def trade_to_dict(trade):
    return {
        'Account': trade.Account,
        'Market_pos': trade.Market_pos,
        'Entry_price': trade.Entry_price,
        'Qty': trade.Qty,
        'Entry_time': trade.Entry_time,
        'Instrument': trade.Instrument,
        'Exits': trade.Exits
    }


# Write trades to a JSON file
output_file_path = 'trades.json'

output_csv_path = "trades.csv"
with open(output_file_path, 'w') as json_file:
    trades_data = [trade_to_dict(trade) for trade in trades]
    json.dump(trades_data, json_file, indent=2)

print(f"Trades details written to {output_file_path}")

with open(output_csv_path, 'w', newline='') as csv_file:
    fieldnames = ['Account', 'Market_pos', 'Entry_price', 'Qty', 'Entry_time', 'Instrument', 'Exits']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Write trade details
    for trade in trades:
        writer.writerow(trade_to_dict(trade))

print(f"Trades details written to {output_csv_path}")
