## Description
Beancount [1] plugin to spread an expense across multiple dates.  Useful for reporting.

## Motivation
A single expense that applies for multiple months is common.  Consider the case of a quarterly gym membership fee
where a single expense is incurred and the membership is active for the entire quarter.  For reporting purposes
it would make sense to have this expense split (spread) across each of the 3 months with the monthly expense
being 1/3th of the cost of the membership.  Ideally we could simply post-date the expenses like this:

```
2019-01-01 * "Resolution Gym"
  Assets:Banks:SomeBank           -240 USD
  Expenses:Gym                      80 USD ;; Jan
  Expenses:Gym                      80 USD ;; Feb
  Expenses:Gym                      80 USD ;; Mar
```

This is not supported in Beancount, but there is a proposal being [discussed](https://docs.google.com/document/d/1x0qqWGRHi02ef-FtUW172SHkdJ8quOZD-Xli7r4Nl_k/edit).

## How the plugin works

The plugin identifies the posting to spread by looking for metadata on a posting with a key of ```spread```.  In this example we want to spread the expense over three months:

```
2019-01-01 * "Resolution Gym"
  Assets:Banks:SomeBank           -240 USD
  Expenses:Gym                     240 USD
    spread: "2019-01-01, 2019-02-01, 2019-03-01"
```

The plugin will do the following:

* Create a transfer account named ```Expenses:Spread-Transfer```
* Change the account for the original expense to ```Expenses:Spread-Transfer```
* Generate an entry for each of the dates in for the ```spread``` metadata

The result would be:

```
2019-01-01 * "Resolution Gym"
  Assets:Banks:SomeBank           -240 USD
  Expenses:Spread-Transfer         240 USD

2010-01-01 open Expenses:Spread-Transfer

2019-01-01 * "Resolution Gym"
  Expenses:Spread-Transfer           -80 USD
  Expenses:Gym                        80 USD

2019-02-01 * "Resolution Gym"
  Expenses:Spread-Transfer           -80 USD
  Expenses:Gym                        80 USD

2019-03-01 * "Resolution Gym"
  Expenses:Spread-Transfer           -80 USD
  Expenses:Gym                        80 USD
```

The resulting balance of the transfer account should always be zero.
