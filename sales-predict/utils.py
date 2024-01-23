def regularize_df(df):
  df = df.dropna()
  for col in df.columns: #[:-1]:
    max_value = df[col].max()
    min_value = df[col].min()
    scalar = max_value - min_value
    df[col] = list(map(lambda x: x / scalar, df[col]))
    # scalar = MinMaxScaler(feature_range=(-1, 1))
    # df[col] = scalar.fit(df[col].values.reshape(-1, 1)) # list(map(lambda x: x / scalar, df[col]))
    # df[col] = (df[col] - df[col].mean()) / df[col].std() # 标准 标准化
    # df[col] = stats.zscore(df[col]) # z score 标准化
  df = df.values
  df = df.astype('float32')
  return df