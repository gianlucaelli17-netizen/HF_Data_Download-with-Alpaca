
#this function loads a datset with the S&P500 composition over the years and turns it
#into a dataframe of shape date|tickers 

def load_sp500_components(path):
    df = pd.read_csv(path, sep=",")
    df["tickers_list"] = df["tickers"].str.split(",")
    df = df.explode("tickers_list")
    df["tickers_list"] = df["tickers_list"].str.strip()

    return df[["date", "tickers"]].dropna().reset_index(drop=True)
#Creates daily components list

# Fills in the gaps between dates giving a day by day composition of the index

def build_daily_components(df):
    # 1. Parse date
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)

    # 2. Order by date
    df = df.sort_values("date")

    # 3. Create day by day calendar
    all_days = pd.date_range(
        start=df["date"].min(),
        end=df["date"].max(),
        freq="D"
    )
    calendar = pd.DataFrame({"date": all_days})

    # 4. groups tickers by date
    grouped = df.groupby("date")["tickers"].apply(list).reset_index(name="tickers")

    # 5. Backward filling
    daily_comp = pd.merge_asof(
        calendar,
        grouped.sort_values("date"),
        on="date",
        direction="backward"
    )

    return daily_comp

#download function

def download_hf_data(daily_comp, start_date, end_date, timeframe="1m", block_days=7):
    """
    Download high-frequency Alpaca data for all S&P500 components
    appearing in daily_comp between start_date and end_date.

    Parameters
    ----------
    daily_comp : DataFrame
        Must contain columns: ["date", "tickers"] where tickers is a list.
    start_date : str or Timestamp
    end_date   : str or Timestamp
    timeframe  : str
        e.g. "1m", "5m", "1h"
    block_days : int
        Size of each download block (default 30 days)

    Returns
    -------
    DataFrame
        Concatenated HF data for all blocks.
    """

    # 1. Convert date column
   daily_comp["date"] = pd.to_datetime(daily_comp["date"], format="%m/%d/%Y")

    # 2. Filter global range
    start_global = pd.Timestamp(start_date)
    end_global   = pd.Timestamp(end_date)

    daily_filtered = daily_comp[
        (daily_comp["date"] >= start_global) &
        (daily_comp["date"] < end_global)
    ]

    # 3. Extract sorted list of unique dates
    dates = daily_filtered["date"].sort_values().to_list()

    all_dfs = []
    n = len(dates)

    # 4. Loop over blocks
    for i in range(0, n, block_days):
        start = dates[i]
        end = start + pd.Timedelta(days=block_days)

        # Select block
        block = daily_filtered[
            (daily_filtered["date"] >= start) &
            (daily_filtered["date"] < end)
        ]

        if block.empty:
            print(f"[INFO] No data in block {start.date()} → {end.date()}, skipped.")
            continue

        # Extract tickers for this block
        tickers_block = list(map(str, sorted(set().union(*block["tickers"]))))


        print(f"\n[INFO] Downloading {len(tickers_block)} tickers | {start.date()} → {end.date()}")
        


        # Time the API call
        t0 = time.time()

        df = alpaca.query(
            tickers_block,
            start_date=start,
            end_date=end,
            timeframe=timeframe
        )

        elapsed = time.time() - t0
        print(f"[INFO] → Received {len(df)} rows in {elapsed:.2f} seconds")

        df["block_start"] = start
        all_dfs.append(df)

    # 5. Final concatenation
    full_df = pd.concat(all_dfs, ignore_index=True)

    return full_df

