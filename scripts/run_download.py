from Download_functions import download_hf_data, build_daily_components, load_sp500_components

daily = build_daily_components(load_sp500_components("sp500.csv"))
full_df = download_hf_data(daily, "2025-01-02", "2025-12-31")

full_df.to_parquet("full_data_2025_01_02_to_2025_12_31.parquet", index=False)
