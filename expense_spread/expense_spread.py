from beancount.core import data
from beancount.core.data import Posting
from beancount.core import account_types
from beancount.core.amount import div, Amount
from beancount.core.data import Transaction
from decimal import *
import datetime

__plugins__ = ('expense_spread',)

SPREAD_KEY = 'spread'
SPREAD_ACCOUNT = 'Expenses:Spread-Transfer'

def expense_spread(entries, options_map):
    new_entries = []
    spread_entries = []
    meta = data.new_metadata('<spread_account>', 1)
    new_entries.append(data.Open(meta, datetime.date(2010, 1, 1), SPREAD_ACCOUNT, None, None))

    for entry in entries:
        if isinstance(entry, data.Transaction):
            new_postings = []
            for posting in entry.postings:
                if SPREAD_KEY in posting.meta:
                    spread_entries.extend(spread_posting(entry, posting))
            entry = replace_expenses_accounts(entry, SPREAD_ACCOUNT)
                    
        new_entries.append(entry)
    return new_entries + spread_entries, []

def spread_posting(entry, posting):
    """Generates entries for the posting to be spread across multiple dates

    Args:
      entry: A Entry directive.
      posting: A posting that contains the SPREAD_KEY metadata
    Returns:
      A list of entry directives.
    """
    spread_entries = []
    dates = posting.meta[SPREAD_KEY].split(',')
    total = Decimal(posting.units.number)
    spread_amount = round(total / len(dates), 2)
    sum = 0

    # create an entry in the transfer account for each date
    for i, date_str in enumerate(dates):
        new_postings = []

        # account for any rounding errors in the last posting of the series
        if i == len(dates) - 1:
            spread_amount = total - sum
        
        new_postings.append(Posting(SPREAD_ACCOUNT, Amount(spread_amount * -1, posting.units.currency), None, None, None, None))
        new_postings.append(Posting(posting.account, Amount(spread_amount, posting.units.currency), None, None, None, None))
        sum += spread_amount

        date_obj = datetime.datetime.strptime(date_str.strip() , '%Y-%m-%d')
        new_entry = entry._replace(date = date_obj.date(), postings = new_postings)
        spread_entries.append(new_entry)
        
    return spread_entries

def replace_expenses_accounts(entry, transfer_account):
    """Replace the Expenses account with the trnasfer account

    Args:
      entry: A Transaction directive.
      transfer_account: A string, the account to use for transfer.
    Returns:
      An entry directive.
    """
    new_postings = []
    for posting in entry.postings:
        if SPREAD_KEY in posting.meta:
            posting = posting._replace(account = SPREAD_ACCOUNT)
            del posting.meta[SPREAD_KEY]
        new_postings.append(posting)
    return entry._replace(postings = new_postings)
