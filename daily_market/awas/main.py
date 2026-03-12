import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import numpy as np
import stock_mapping

# 페이지 설정은 맨 처음 나와야 합니다.
st.set_page_config(layout="wide", page_title="GGeolmu Bird")

# 종목 이름과 종목 코드를 매핑하는 딕셔너리 (예시)
# 실제 서비스에서는 전체 종목 리스트를 API나 DB에서 가져와야 합니다.


STOCK_LIST_ROOT = "/root/Police/postgres_server/market"

mmp_kospi = stock_mapping.mapped(path="{STOCK_LIST_ROOT}/kospi/stock_list.csv")
stock_map_kospi = dict(mmp_kospi.output())

mmp_kosdaq = stock_mapping.mapped(path="{STOCK_LIST_ROOT}/kosdaq/stock_list.csv")
stock_map_kosdaq = dict(mmp_kosdaq.output())

mmp_nasdaq = stock_mapping.mapped(path="{STOCK_LIST_ROOT}/nasdaq/stock_list.csv")
stock_map_nasdaq = dict(mmp_nasdaq.output())

mmp_nyse = stock_mapping.mapped(path="{STOCK_LIST_ROOT}/nyse/stock_list.csv")
stock_map_nyse = dict(mmp_nyse.output())

stock_map_spot = {
    "Gold ETF" : "GLD",
    "Silver ETF" : "SLV",
    "WTI Crude oil" : "CL",
    "Brent oil" : "BZ",
    "Natural gas" : "NG",

    "Copper" : "HG",
    "NI" : "NI",
    "PL" : "PL"
}

stock_map_futures = {
    "Gold" : "GC=F",
    "Silver" : "SI=F",
    "Copper" : "HG=F",
    "NI" : "NI=F",
    
    "WTI Crude oil" : "CL=F",
    "Brent oil" : "BZ=F",
    "Natural gas" : "NG=F",
    "PL=F" : "PL=F"
}

stock_map_money = {
    "달러인덱스" : "DX-Y.NYB",
    "USD/KRW" : "USD/KRW",
    "EUR/KRW" : "EUR/KRW",
    "JPY/KRW" : "JPY/KRW",
    "CHF/KRW" : "CHF/KRW",

    "USD/EUR" : "USD/EUR",
    "USD/CNY" : "USD/CNY",
    "EUR/CNY" : "EUR/CNY",
}

stock_map_coin = {
    "BTC/KRW" : "BTC/KRW",
    "ETH/KRW" : "ETH/KRW",
    "XRP/KRW" : "XRP/KRW",
    "SOL/KRW" : "SOL/KRW",
    "BTC/USD" : "BTC/USD",
    "ETH/USD" : "ETH/USD",
}

def divergence(price, rsi, lookback):
    #Setting
    up_div_price = [0.01, 0.15] # 가격 저점 상승률 하한/상한
    up_div_rsi = [0.01, 0.15] # RSI 저점 상승률 하한/상한
    down_div_price = [0.03, 0.15] # 가격 고점 상승률 하한/상한
    down_div_rsi = [-0.03, -0.15] # RSI 고점 하락률 하한/상한


    def local_peaks(s):  # 로컬 고점
        return (s.shift(1) < s) & (s.shift(-1) < s)
    def local_troughs(s):  # 로컬 저점
        return (s.shift(1) > s) & (s.shift(-1) > s)

    p = price.tail(lookback)
    r = rsi.reindex(p.index)

    trough_idx = p[local_troughs(p)].index
    peak_idx = p[local_peaks(p)].index

    bull_div = pd.Series(0, index=p.index)
    bear_div = pd.Series(0, index=p.index)

    if len(trough_idx) >= 2:
        for a, b in zip(trough_idx[:-1], trough_idx[1:]):
            price_LL_pct = (p[b] - p[a]) / p[a]
            rsi_LL_pct = (r[b] - r[a]) / r[a]
            if ((up_div_price[0] <= price_LL_pct <= up_div_price[1]) and
                (up_div_rsi[0]   <= rsi_LL_pct   <= up_div_rsi[1])):
                bull_div[b] = 1

    if len(peak_idx) >= 2:
        for a, b in zip(peak_idx[:-1], peak_idx[1:]):
            price_HH_pct = (p[b] - p[a]) / p[a]
            rsi_HH_pct = (r[b] - r[a]) / r[a]
            if ((down_div_price[0] <= price_HH_pct <= down_div_price[1]) and
                (down_div_rsi[1]   <= rsi_HH_pct  <= down_div_rsi[0])):  # 주의: 음수 범위
                bear_div[b] = 1

    return bull_div, bear_div

def hidden_divergence(price, rsi, lookback):

    up_hide_price = [0.03, 0.15]
    up_hide_rsi = [-0.03, -0.15]
    down_hide_price = [-0.03, -0.15]
    down_hide_rsi = [0.03, 0.15]

    def local_peaks(s):  # 로컬 고점
        return (s.shift(1) < s) & (s.shift(-1) < s)
    def local_troughs(s):  # 로컬 저점
        return (s.shift(1) > s) & (s.shift(-1) > s)

    p = price.tail(lookback)
    r = rsi.reindex(p.index)

    trough_idx = p[local_troughs(p)].index
    peak_idx = p[local_peaks(p)].index

    hidden_bull = pd.Series(0, index=p.index)
    hidden_bear = pd.Series(0, index=p.index)

    if len(trough_idx) >= 2:
        for a, b in zip(trough_idx[:-1], trough_idx[1:]):
            price_LL_pct = (p[b] - p[a]) / p[a]
            rsi_LL_pct = (r[b] - r[a]) / r[a]
            if ((up_hide_price[0] <= price_LL_pct <= up_hide_price[1]) and
                (up_hide_rsi[1]  <= rsi_LL_pct <= up_hide_rsi[0])):  # rsi 하락 → 부호 주의
                hidden_bull[b] = 1

    if len(peak_idx) >= 2:
        for a, b in zip(peak_idx[:-1], peak_idx[1:]):
            price_HH_pct = (p[b] - p[a]) / p[a]
            rsi_HH_pct = (r[b] - r[a]) / r[a]
            if ((down_hide_price[1] <= price_HH_pct <= down_hide_price[0]) and  # 음수 범위
                (down_hide_rsi[0]  <= rsi_HH_pct <= down_hide_rsi[1])):
                hidden_bear[b] = 1

    return hidden_bull, hidden_bear

def divergence_rolling(price, rsi, lookback):
    print("Divergence rolling")
    bull_div_full = pd.Series(index=price.index, dtype=float)
    bear_div_full = pd.Series(index=price.index, dtype=float)
    n = len(price)
    if n < lookback:
        return bull_div_full, bear_div_full
    bull_div_full.iloc[:lookback - 1] = 0.0
    bear_div_full.iloc[:lookback - 1] = 0.0
    for t in range(lookback - 1, n):
        bull_win, bear_win = divergence(price.iloc[:t + 1], rsi, lookback=lookback)
        bull_idx = bull_win.index[bull_win.values == 1]
        bear_idx = bear_win.index[bear_win.values == 1]
        bull_div_full.loc[bull_idx] = 1
        bear_div_full.loc[bear_idx] = 1
    return bull_div_full.fillna(0).astype("int8"), bear_div_full.fillna(0).astype("int8")

def hidden_divergence_rolling(price, rsi, lookback):
    print("Hidden divergence rolling")
    bull_div_full = pd.Series(index=price.index, dtype=float)
    bear_div_full = pd.Series(index=price.index, dtype=float)
    n = len(price)
    if n < lookback:
        return bull_div_full, bear_div_full
    bull_div_full.iloc[:lookback - 1] = 0.0
    bear_div_full.iloc[:lookback - 1] = 0.0
    for t in range(lookback - 1, n):
        bull_win, bear_win = hidden_divergence(price.iloc[:t + 1], rsi, lookback=lookback)
        bull_idx = bull_win.index[bull_win.values == 1]
        bear_idx = bear_win.index[bear_win.values == 1]
        bull_div_full.loc[bull_idx] = 1
        bear_div_full.loc[bear_idx] = 1
    return bull_div_full.fillna(0).astype("int8"), bear_div_full.fillna(0).astype("int8")

def add_dmi(data, window=14, adx_threshold=25, adxr_window=None):
    if adxr_window is None:
        adxr_window = window
    ind = ta.trend.ADXIndicator(
        high=data["High"], low=data["Low"], close=data["Close"],
        window=window, fillna=False,
    )
    try:
        data["PDI"] = ind.adx_pos()
        data["MDI"] = ind.adx_neg()
        data["ADX"] = ind.adx()

        di_p = data["PDI"]
        di_m = data["MDI"]
        denom = (di_p + di_m).replace(0, np.nan)
        data["DX"] = ((di_p - di_m).abs() / denom) * 100
        data["ADXR"] = (data["ADX"] + data["ADX"].shift(adxr_window)) / 2

        data["DMI_Trend"] = np.select(
            [
                (data["ADX"] >= adx_threshold) & (di_p > di_m),
                (data["ADX"] >= adx_threshold) & (di_p < di_m),
            ],
            [1, -1],
            default=0,
        ).astype("int8")

        data["ADXR_Signal"] = np.where(data["ADXR"] >= 25, 1,
                        np.where(data["ADXR"] < 25, 0, 0))

    except IndexError:
        data["PDI"]  = -1000
        data["MDI"] = -1000
        data["ADX"] = -1000
        di_p = data["PDI"]; di_m = data["MDI"]
        denom = (di_p + di_m).replace(0, np.nan)
        data["DX"] = ((di_p - di_m).abs() / denom) * 100
        data["ADXR"] = (data["ADX"] + data["ADX"].shift(adxr_window)) / 2
        data["DMI_Trend"] = 0

    data["DMI_BullCross"] = ((di_p >= di_m) & (di_p.shift(1) < di_m.shift(1))).astype("int8")
    data["DMI_BearCross"] = ((di_p <= di_m) & (di_p.shift(1) > di_m.shift(1))).astype("int8")
    return data

# 기술적 지표 계산 함수
def calculate_indicators(data):

    # Setting values
    # RSI Divergence
    price_label_rsi = "MA5"
    rsi_label = "RSI6"
    rsi_rollback = 90
    price_label_rsi_hidden = "MA5"
    rsi_label_hidden = "RSI6"
    rsi_hidden_rollback = 180

    # CCI Divergence
    price_label_cci = "MA5"
    cci_label = "CCI6"
    cci_rollback = 90
    price_label_cci_hidden = "MA5"
    cci_label_hidden = "CCI6"
    cci_hidden_rollback = 180

    # Oversell Overbuy
    rsi_overbuy_label = "RSI5"
    rsi_oversell_label = "RSI5"
    cci_overbuy_label = "CCI5"
    cci_oversell_label = "CCI5"

    # 가격차이
    data['Close_diff_first'] = data['Close'].diff()
    data['Close_diff_second'] = data['Close'].diff(2)

    # 가격변화율
    data['Close_rate_first'] = data['Close'].pct_change(fill_method=None)
    data['Close_rate_second'] = data['Close'].pct_change(periods=2, fill_method=None)

    # 거래대금
    data["CurrencyVolume"] = data["Close"] * data["Volume"]

    # OBV 
    data['obv_change'] = np.where(data['Close_diff_first'] > 0,  data['Volume'],  
                np.where(data['Close_diff_first'] < 0, -data['Volume'], 0))
    data['OBV'] = data['obv_change'].cumsum()

    # Moving average
    data["MA2"] = data["Close"].rolling(window=2).mean()
    data["MA3"] = data["Close"].rolling(window=3).mean()
    data["MA4"] = data["Close"].rolling(window=4).mean()
    data["MA5"] = data["Close"].rolling(window=5).mean()
    data["MA6"] = data["Close"].rolling(window=6).mean()
    data["MA7"] = data["Close"].rolling(window=7).mean()
    data["MA8"] = data["Close"].rolling(window=8).mean()
    data["MA9"] = data["Close"].rolling(window=9).mean()
    data["MA10"] = data["Close"].rolling(window=10).mean()
    data["MA14"] = data["Close"].rolling(window=14).mean()
    data["MA30"] = data["Close"].rolling(window=30).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data["MA60"] = data["Close"].rolling(window=60).mean()
    data["MA120"] = data["Close"].rolling(window=120).mean()
    data["MA200"] = data["Close"].rolling(window=200).mean()
    data["MA224"] = data["Close"].rolling(window=224).mean()

    # Bollinger Band
    n, k = 20, 2
    data['MA20'] = data['Close'].rolling(window=n).mean()
    data['STD20'] = data['Close'].rolling(window=n).std()
    data['BB_Upper'] = data['MA20'] + (k * data['STD20'])
    data['BB_Lower'] = data['MA20'] - (k * data['STD20'])

    # RSI
    data["RSI"] = ta.momentum.RSIIndicator(data["Close"], window=14).rsi()
    data["RSI2"] = data['RSI'].rolling(window=2).mean()
    data["RSI3"] = data['RSI'].rolling(window=3).mean()
    data["RSI4"] = data['RSI'].rolling(window=4).mean()
    data["RSI5"] = data['RSI'].rolling(window=5).mean()
    data["RSI6"] = data['RSI'].rolling(window=6).mean()
    data["RSI7"] = data['RSI'].rolling(window=7).mean()
    data["RSI8"] = data['RSI'].rolling(window=8).mean()
    data["RSI9"] = data['RSI'].rolling(window=9).mean()
    data["RSI14"] = data['RSI'].rolling(window=14).mean()

    # RSI rate
    data['RSI_rate_first'] = data['RSI'].pct_change() * 100 # 1 행 전
    data['RSI_rate_second'] = data['RSI'].pct_change(2) * 100 # 2 행 전
    
    # RSI Sell point
    data["RSI_Signal"] = np.where(data[rsi_overbuy_label] >= 70, 1,
                            np.where(data[rsi_oversell_label] <= 30, -1, 0))

    # RSI Divergence rolling
    rsi_bull, rsi_bear = divergence_rolling(
        price=data[price_label_rsi], rsi=data[rsi_label], lookback=rsi_rollback)
    data["RSI_BullDiv"] = rsi_bull
    data["RSI_BearDiv"] = rsi_bear

    rsi_hidden_bull, rsi_hidden_bear = hidden_divergence_rolling(
        price=data[price_label_rsi_hidden], rsi=data[rsi_label_hidden], lookback=rsi_hidden_rollback)
    data["RSI_Hidden_BullDiv"] = rsi_hidden_bull
    data["RSI_Hidden_BearDiv"] = rsi_hidden_bear

    # CCI
    data["CCI"] = ta.trend.CCIIndicator(
        high=data["High"], low=data["Low"], close=data["Close"], window=20
    ).cci()
    data["CCI2"] = data['CCI'].rolling(window=2).mean()
    data["CCI3"] = data['CCI'].rolling(window=3).mean()
    data["CCI4"] = data['CCI'].rolling(window=4).mean()
    data["CCI5"] = data['CCI'].rolling(window=5).mean()
    data["CCI6"] = data['CCI'].rolling(window=6).mean()
    data["CCI7"] = data['CCI'].rolling(window=7).mean()
    data["CCI8"] = data['CCI'].rolling(window=8).mean()
    data["CCI9"] = data['CCI'].rolling(window=9).mean()
    data["CCI14"] = data['CCI'].rolling(window=14).mean()

    # CCI rate
    data['CCI_rate_first'] = data['CCI'].pct_change() * 100 # 1 행 전
    data['CCI_rate_second'] = data['CCI'].pct_change(2) * 100 # 2 행 전
    
    # CCI Oversell Overbuy
    data["CCI_Signal"] = np.where(data[cci_overbuy_label] >= 100, 1,
                            np.where(data[cci_oversell_label] <= -100, -1, 0))
    
    # CCI Divergence rolling
    cci_bull, cci_bear = divergence_rolling(
        price=data[price_label_cci], rsi=data[cci_label], lookback=cci_rollback)
    data["CCI_BullDiv"] = cci_bull
    data["CCI_BearDiv"] = cci_bear

    cci_hidden_bull, cci_hidden_bear = hidden_divergence_rolling(
        price=data[price_label_cci_hidden], rsi=data[cci_label_hidden], lookback=cci_hidden_rollback)
    data["CCI_Hidden_BullDiv"] = cci_hidden_bull
    data["CCI_Hidden_BearDiv"] = cci_hidden_bear

    # MACD
    macd = ta.trend.MACD(close=data["Close"], window_slow=26, window_fast=12, window_sign=9)
    data["MACD"] = macd.macd()
    data["MACD_Base"] = macd.macd_signal()
    data["MACD_Hist"] = macd.macd_diff()
    data["MACD_Positive"] = np.where(data["MACD"] > 0, 1, -1)
    data["MACD_Signal"] = np.where(data["MACD"] > data["MACD_Base"], 1,
                            np.where(data["MACD"] < data["MACD_Base"], -1, 0))

    # DMI
    data = add_dmi(data, window=14, adx_threshold=25)

    # MDD
    data['High_watermark'] = data['Close'].cummax()
    data['Drawdown'] = (data['Close'] - data['High_watermark']) / data['High_watermark']

    data["Sell_Signal"] = np.where(
        (data["MACD_Positive"] == 1) &
        (data["MACD_Signal"] == 1) &
        (data["RSI_Signal"] == 1) &
        (data["CCI_Signal"] == 1),
        1, 0
    )
    return data

# 데이터 캐싱
@st.cache_data
def load_data(ticker, start_date, end_date):
    """지정된 기간의 주식 데이터를 가져옵니다. """
    try:
        df = fdr.DataReader(f"{ticker}", start=start_date, end=end_date)
        df = df.interpolate(method="linear")
        return df
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return pd.DataFrame()

# Sidebar
st.sidebar.header("⚙️ 분석 설정")

market_options = {
    "KOSPI": stock_map_kospi,
    "KOSDAQ": stock_map_kosdaq,
    "NYSE": stock_map_nyse,
    "NASDAQ": stock_map_nasdaq,
    "Currency" : stock_map_money,
    "Crypto Currency" : stock_map_coin,
    "Spot" : stock_map_spot,
    "Futures" : stock_map_futures
}

# Market
selected_market_name = st.sidebar.selectbox(
    "시장을 선택하세요:",
    options=list(market_options.keys()),
    index=0 # 기본값 KOSPI
)
selected_stock_map = market_options[selected_market_name]
stock_keys = list(selected_stock_map.keys())

# Name
if not stock_keys:
    st.sidebar.warning(f"선택하신 {selected_market_name} 시장에는 현재 종목 데이터가 없습니다.")
    stock_name = None
    stock_ticker = None
else:
    # 종목 리스트의 첫 번째
    default_index = 0 
    
    stock_name = st.sidebar.selectbox(
        "종목 이름을 선택하세요:",
        options=stock_keys,
        index=default_index
    )

    # 종목 이름으로 종목 코드
    stock_ticker = selected_stock_map.get(stock_name)

# --- (이후 데이터 기간 설정 및 분석 로직 계속) ---
if stock_ticker:
    st.sidebar.write(f"선택된 종목:\n**{stock_name}**\n({stock_ticker})")
else:
    st.sidebar.write("선택된 종목이 없습니다.")

if not stock_ticker:
    st.error(f"'{stock_name}'에 해당하는 종목 코드를 찾을 수 없습니다. (지원되는 종목: {', '.join(stock_map_kospi.keys())})")
    st.stop() # 코드가 더 이상 진행되지 않도록 중단

# 2. 데이터 기간
st.sidebar.markdown("---")
st.sidebar.subheader("🗓️ 데이터 기간 설정")

def set_slider_font_size(label_font_size='23px', value_font_size='23px'):
    """
    st.slider의 라벨과 선택 값의 폰트 크기를 설정하는 CSS를 주입합니다.
    """
    custom_css = f"""
    <style>
    /* 1. 슬라이더 라벨 ("조회 기간을 선택하세요:") 폰트 크기 변경 */
    /* st.slider의 라벨에 해당하는 클래스 (버전에 따라 다를 수 있음) */
    .st-cq, .st-ag {{ 
        font-size: {label_font_size} !important;
        font-weight: bold;
    }}
    
    /* 2. 슬라이더 핸들 위에 표시되는 선택 값 (YYYY-MM-DD) 폰트 크기 변경 */
    .st-bm, .st-am {{
        font-size: {value_font_size} !important;
    }}

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

set_slider_font_size(label_font_size='30px', value_font_size='16px')

# Default data range
end_date = dt.date.today()
default_start_date = end_date - dt.timedelta(days=365 * 2) # 2년치 데이터
# Slider : Data range
date_range = st.sidebar.slider(
    "조회 기간을 선택하세요:",
    min_value=dt.date(2000, 1, 1),
    max_value=end_date,
    value=(default_start_date, end_date),
    format="YYYY-MM-DD"
)
start_date = date_range[0]
end_date = date_range[1]


# 4.ID
ID_label = "GGeolmu bird"
Tier_label = "Silver"
State = "안샀음😠\n This bird is ont of the famous bird in South Korea."
image_path = "/root/Police/daily_market/awas/photo/ggeolmujpjp.jpg"

st.sidebar.image(
    image_path, 
    width=280
)

caption_html = f"""
<div style="text-align: left; font-size: 20px; padding-left: 5px;">
    ID : {ID_label}<br>
    Tier : {Tier_label}<br>
    State : {State}
</div>
"""
st.sidebar.markdown(caption_html, unsafe_allow_html=True)

# 5. Data loading
data_df = load_data(stock_ticker, start_date, end_date)

if not data_df.empty:
    st.markdown(f"# **{stock_name}** ({stock_ticker}) / 기간: {start_date} ~ {end_date}")
    
    # 기술적 지표 계산
    data_df = calculate_indicators(data=data_df)
    
    # 선택된 기간에 맞게 데이터 필터링
    data_df_filtered = data_df.copy()

    rsi_bull_div_signals = data_df_filtered[data_df_filtered['RSI_BullDiv'] == 1].copy()
    cci_bull_div_signals = data_df_filtered[data_df_filtered['CCI_BullDiv'] == 1].copy()

    rsi_bear_div_signals = data_df_filtered[data_df_filtered['RSI_BearDiv'] == 1].copy()
    cci_bear_div_signals = data_df_filtered[data_df_filtered['CCI_BearDiv'] == 1].copy()

    sell_signals = data_df_filtered[data_df_filtered['Sell_Signal'] == 1].copy()

    rsi_hidden_bull_signals = data_df_filtered[data_df_filtered['RSI_Hidden_BullDiv'] == 1].copy()
    rsi_hidden_bear_signals = data_df_filtered[data_df_filtered['RSI_Hidden_BearDiv'] == 1].copy()

    cci_hidden_bull_signals = data_df_filtered[data_df_filtered['CCI_Hidden_BullDiv'] == 1].copy()
    cci_hidden_bear_signals = data_df_filtered[data_df_filtered['CCI_Hidden_BearDiv'] == 1].copy()
    
    # (1, 1) Line Chart
    fig_price = go.Figure(data=[
        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['Close'], 
            mode='lines', 
            name='Close', 
            line=dict(color='forestgreen', width=5)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['MA5'], 
            mode='lines', 
            name='MA5', 
            line=dict(color='silver', width=5)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['MA60'], 
            mode='lines', 
            name='MA60', 
            line=dict(color='darkgrey', width=5)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['MA120'], 
            mode='lines', 
            name='MA120', 
            line=dict(color='dimgray', width=5)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['MA224'], 
            mode='lines', 
            name='MA224', 
            line=dict(color='maroon', width=5)  
        ),

        # Bollinger band
        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['BB_Upper'], 
            mode='lines', 
            name='BB Upper', 
            line=dict(color='indianred', width=3)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['BB_Lower'], 
            mode='lines', 
            name='BB Lower', 
            line=dict(color='royalblue', width=3)  
        ),

        # Sell signals
        go.Scatter(
            x=sell_signals.index, 
            y=sell_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Sell', 
            marker=dict(color='blue', size=20, symbol='triangle-down'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Sell signal<extra></extra>'
                    ),

        # RSI Signals
        go.Scatter(
            x=rsi_bull_div_signals.index, 
            y=rsi_bull_div_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Bull(R)', 
            marker=dict(color='red', size=20, symbol='triangle-up'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Bull signal<extra></extra>'
                    ),
        
        go.Scatter(
            x=rsi_bear_div_signals.index, 
            y=rsi_bear_div_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Bear(R)', 
            marker=dict(color='slateblue', size=20, symbol='triangle-down'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Bear signal<extra></extra>'
                    ),

        go.Scatter(
            x=rsi_hidden_bull_signals.index, 
            y=rsi_hidden_bull_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Keep Bull(R)', 
            marker=dict(color='orange', size=20, symbol='triangle-up'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Hidden bull<extra></extra>'
                    ),
        
        go.Scatter(
            x=rsi_hidden_bear_signals.index, 
            y=rsi_hidden_bear_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Keep Bear(R)', 
            marker=dict(color='royalblue', size=20, symbol='triangle-down'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Hidden bear<extra></extra>'
                    ),

        # CCI
        go.Scatter(
            x=cci_bull_div_signals.index, 
            y=cci_bull_div_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Bull(C)', 
            marker=dict(color='chocolate', size=20, symbol='triangle-up'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Bull signal<extra></extra>'
                    ),

        go.Scatter(
            x=cci_bear_div_signals.index, 
            y=cci_bear_div_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Bear(C)', 
            marker=dict(color='darkgreen', size=20, symbol='triangle-down'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f}<br>' +
                    '<b>Signal:</b> Bear signal<extra></extra>'
                    ),
        
        go.Scatter(
            x=cci_hidden_bull_signals.index, 
            y=cci_hidden_bull_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Keep Bull(C)', 
            marker=dict(color='tomato', size=20, symbol='triangle-up'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f} KRW<br>' +
                    '<b>Signal:</b> Hidden bull<extra></extra>'
                    ),
    
        go.Scatter(
            x=cci_hidden_bear_signals.index, 
            y=cci_hidden_bear_signals['Close'], # 종가 그래프 위에 표시
            mode='markers', 
            name='Keep Bear(C)', 
            marker=dict(color='deepskyblue', size=20, symbol='triangle-down'),
            hovertemplate = 
                    '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                    '<b>Close:</b> %{y:,.0f} KRW<br>' +
                    '<b>Signal:</b> Hidden bear<extra></extra>'
                    ),
    ])

    fig_price.update_layout(
        yaxis_title="Price",
        height=500,
        xaxis_rangeslider_visible=False,
        
        # 여백
        margin=dict(
                l=20,  # Left margin (좌측 Y축 제목/레이블 공간)
                r=20,  # Right margin
                t=10,  # Top margin (상단 제목 공간)
                b=10  # Bottom margin (하단 X축 제목, RangeSlider, 그리고 범례 공간)
            ),

        # 폰트 크기 설정
        font=dict(
            family="Arial, sans-serif",  # 폰트 종류 설정
            size=20,                     # 기본 폰트 크기 설정
            color="black"
        ),

        # 축 제목 폰트 크기 설정
        xaxis=dict(title=dict(font=dict(size=22)),
        tickfont=dict(size=20)
        ),
        yaxis=dict(title=dict(font=dict(size=22)),
        tickfont=dict(size=20)
        ),

        legend=dict(
        font=dict(size=15),
        # 오른쪽 상단에 배치 (x=1, y=1)
        x=0,
        y=1.1,
        orientation="h",
        # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
        xanchor='left',
        yanchor='top')

        # 제목 폰트 크기 설정 (만약 fig_price에 차트 제목을 추가했다면 사용)
        # title=dict(font=dict(size=20)) 
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # (2, 1) Volume
    fig_price = go.Figure(data=[
    go.Bar(
            x=data_df_filtered.index, 
            y=data_df_filtered['Volume'], 
            name='Volume', 
            marker_color='grey', 
            opacity=0.8,
        ),
    ])

    fig_price.update_layout(
        yaxis_title="Volume",
        height=200,
        xaxis_rangeslider_visible=False,
        
        # 여백
        margin=dict(
                l=20,  # Left margin (좌측 Y축 제목/레이블 공간)
                r=20,  # Right margin
                t=10,  # Top margin (상단 제목 공간)
                b=10  # Bottom margin (하단 X축 제목, RangeSlider, 그리고 범례 공간)
            ),

        # 폰트 크기 설정
        font=dict(
            family="Arial, sans-serif",  # 폰트 종류 설정
            size=20,                     # 기본 폰트 크기 설정
            color="black"
        ),

        # 축 제목 폰트 크기 설정
        xaxis=dict(title=dict(font=dict(size=22)),
        tickfont=dict(size=20)
        ),
        yaxis=dict(title=dict(font=dict(size=22)),
        tickfont=dict(size=20)
        ),

        legend=dict(
        font=dict(size=15),
        # 오른쪽 상단에 배치 (x=1, y=1)
        x=0,
        y=1.1,
        orientation="h",
        # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
        xanchor='left',
        yanchor='top')

        # 제목 폰트 크기 설정 (만약 fig_price에 차트 제목을 추가했다면 사용)
        # title=dict(font=dict(size=20)) 
    )
    st.plotly_chart(fig_price, use_container_width=True)


    # (3, 1) Binary indicator
    fig_price = go.Figure(data=[
        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['CCI_Signal'], 
            mode='lines', 
            name='CCI(Ternary)', 
            line=dict(color='orange', width=3)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['RSI_Signal'], 
            mode='lines', 
            name='RSI(Ternary)', 
            line=dict(color='purple', width=3)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['MACD_Signal'], 
            mode='lines', 
            name='MACD(Ternary)', 
            line=dict(color='red', width=3)  
        ),

        go.Scatter(
            x=data_df_filtered.index, 
            y=data_df_filtered['ADXR_Signal'], 
            mode='lines', 
            name='ADXR(Binary)', 
            line=dict(color='green', width=3)  
        ),

        ])
    

    fig_price.update_layout(
        yaxis_title="Signals",
        height=300,
        xaxis_rangeslider_visible=False,
        
        # 여백
        margin=dict(
                l=20,  # Left margin (좌측 Y축 제목/레이블 공간)
                r=20,  # Right margin
                t=10,  # Top margin (상단 제목 공간)
                b=10  # Bottom margin (하단 X축 제목, RangeSlider, 그리고 범례 공간)
            ),


        # 폰트 크기 설정
        font=dict(
            family="Arial, sans-serif",  # 폰트 종류 설정
            size=20,                     # 기본 폰트 크기 설정
            color="black"
        ),
        # 축 제목 폰트 크기 설정
        xaxis=dict(title=dict(font=dict(size=20)),
        tickfont=dict(size=17)
        ),
        yaxis=dict(title=dict(font=dict(size=20)),
        tickfont=dict(size=17)
        ),

        legend=dict(
        font=dict(size=18),
        # 오른쪽 상단에 배치 (x=1, y=1)
        x=0,
        y=1.4,
        orientation="h",
        # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
        xanchor='left',
        yanchor='top')

        # 제목 폰트 크기 설정 (만약 fig_price에 차트 제목을 추가했다면 사용)
        # title=dict(font=dict(size=20)) 
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # 3. 기술적 지표 시각화 (RSI, CCI, MACD, ADX/DMI)
    st.markdown("---")

    # (RSI, CCI, MACD, ADX/DMI)
    # col1, col2, col3, col4 = st.columns(4)
    col1, col2 = st.columns(2)
    
    # --- 1열: CCI ---
    with col1:
        st.markdown("#### CCI (Commodity Channel Index)")
        fig_cci = go.Figure(data=[
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['CCI'], mode='lines', name='CCI', line=dict(color='orange')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['CCI3'], mode='lines', name='CCI3', line=dict(color='red')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['CCI6'], mode='lines', name='CCI6', line=dict(color='green')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['CCI9'], mode='lines', name='CCI9', line=dict(color='blue'))
        ])
        fig_cci.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="+100", annotation_position="top left")
        fig_cci.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="0", annotation_position="top left")
        fig_cci.add_hline(y=-100, line_dash="dash", line_color="green", annotation_text="-100", annotation_position="bottom left")
        fig_cci.update_layout(height=300, 
        
        margin=dict(t=10, b=10),

        xaxis=dict(
            tickfont=dict(size=16) 
        ),
        
        yaxis=dict(
            tickfont=dict(size=16)
        ),

        legend=dict(
            font=dict(size=18),
            # 오른쪽 상단에 배치 (x=1, y=1)
            x=0,
            y=1.1,
            orientation="h",
            # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
            xanchor='left',
            yanchor='top')
        )
        st.plotly_chart(fig_cci, use_container_width=True)


    # --- 2열: RSI ---
    with col2:
        st.markdown("#### RSI (Relative Strength Index)")
        fig_rsi = go.Figure(data=[
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['RSI'], mode='lines', name='RSI', line=dict(color='purple')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['RSI3'], mode='lines', name='RSI3', line=dict(color='red')), 
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['RSI6'], mode='lines', name='RSI6', line=dict(color='green')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['RSI9'], mode='lines', name='RSI9', line=dict(color='blue'))
        ])
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="과매수(70)", annotation_position="top left")
        fig_rsi.add_hline(y=50, line_dash="dash", line_color="white", annotation_text="50", annotation_position="top left")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="과매도(30)", annotation_position="bottom left")
        fig_rsi.update_layout(height=300, 
                              margin=dict(t=10, b=10),
            legend=dict(
            font=dict(size=18),
            # 오른쪽 상단에 배치 (x=1, y=1)
            x=0,
            y=1.1,
            orientation="h",
            # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
            xanchor='left',
            yanchor='top')
        
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    # --- MACD ---
    with col3:
        st.markdown("#### MACD (Moving Average Convergence Divergence)")
        fig_macd = go.Figure(data=[
            go.Bar(x=data_df_filtered.index, y=data_df_filtered['MACD_Hist'], name='MACD Hist', marker_color='grey'),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['MACD'], mode='lines', name='MACD Line', line=dict(color='red')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['MACD_Signal'], mode='lines', name='Signal Line', line=dict(color='blue'))
        ])
        fig_macd.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="0", annotation_position="top left")
        fig_macd.update_layout(height=300, 
        margin=dict(t=3, b=3),

        xaxis=dict(
            tickfont=dict(size=16) 
        ),
        
        yaxis=dict(
            tickfont=dict(size=16)
        ),
        
        legend=dict(
            font=dict(size=18),
            # 오른쪽 상단에 배치 (x=1, y=1)
            x=0,
            y=1,
            orientation="h",
            # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
            xanchor='left',
            yanchor='top')
        )
        st.plotly_chart(fig_macd, use_container_width=True)

    # --- 4열: DMI (+DI, -DI) / ADX ---
    with col4:
        st.markdown("#### DMI (+DI, -DI) / ADX")
        fig_dmi_adx = go.Figure(data=[
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['PDI'], mode='lines', name='+DI', line=dict(color='red')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['MDI'], mode='lines', name='-DI', line=dict(color='green')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['ADX'], mode='lines', name='ADX', line=dict(color='gray', dash='dot')),
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['ADXR'], mode='lines', name='ADXR', line=dict(color='gray'))
        ])
        fig_dmi_adx.add_hline(y=20, line_dash="dash", line_color="white", annotation_text="20", annotation_position="top left")
        fig_dmi_adx.update_layout(height=300, 
        margin=dict(t=3, b=3),

        xaxis=dict(
            tickfont=dict(size=16) 
        ),
        
        yaxis=dict(
            tickfont=dict(size=16)
        ),
        
        legend=dict(
            font=dict(size=18),
            # 오른쪽 상단에 배치 (x=1, y=1)
            x=0,
            y=1,
            orientation="h",
            # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
            xanchor='left',
            yanchor='top')
        )
        st.plotly_chart(fig_dmi_adx, use_container_width=True)
    

    # 3. 기술적 지표 시각화 (MDD, OBV)
    st.markdown("---")

    # MDD, OBV
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("#### MDD (Max Draw Down)")
        fig_mdd = go.Figure(data=[
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['Drawdown'], mode='lines', name='MDD', line=dict(color='red'))
        ])
        fig_cci.update_layout(height=300, 
        
        margin=dict(t=3, b=3),

        xaxis=dict(
            tickfont=dict(size=16) 
        ),
        
        yaxis=dict(
            tickfont=dict(size=16),
            range=[-1.1, 0]
        ),

        # legend=dict(
        #     font=dict(size=18),
        #     # 오른쪽 상단에 배치 (x=1, y=1)
        #     x=0,
        #     y=1,
        #     orientation="h",
        #     # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
        #     xanchor='left',
        #     yanchor='top')
        )
        st.plotly_chart(fig_mdd, use_container_width=True)
    
    with col6:
        st.markdown("#### OBV (On-Balance Volume)")
        fig_obv = go.Figure(data=[
            go.Scatter(x=data_df_filtered.index, y=data_df_filtered['OBV'], mode='lines', name='OBV', line=dict(color='gray'))
        ])

        fig_obv.update_layout(height=300, 
        
        margin=dict(t=3, b=3),

        xaxis=dict(
            tickfont=dict(size=16) 
        ),
        
        yaxis=dict(
            tickfont=dict(size=16)
        ),

        # legend=dict(
        #     font=dict(size=18),
        #     # 오른쪽 상단에 배치 (x=1, y=1)
        #     x=0,
        #     y=1,
        #     orientation="h",
        #     # 범례 상자의 오른쪽 상단 모서리를 (1, 1) 좌표에 고정
        #     xanchor='left',
        #     yanchor='top')
        )
        st.plotly_chart(fig_obv, use_container_width=True)

    # --- 데이터 확인 (선택 사항) ---
    # st.markdown("---")
    # BullF
    # st.subheader("Bull Signals")
    # if st.checkbox('CCI'):
    #     st.dataframe(cci_bull_div_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # if st.checkbox('RSI'):
    #     st.dataframe(rsi_bull_div_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # if st.checkbox('CCI Hidden'):
    #     st.dataframe(cci_hidden_bull_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # if st.checkbox('RSI Hidden'):
    #     st.dataframe(rsi_hidden_bull_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # Bear signals
    # st.markdown("---")
    # st.subheader("Bear Signals")

    # if st.checkbox('CCI'):
    #     st.dataframe(cci_bear_div_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # if st.checkbox('RSI'):
    #     st.dataframe(rsi_bear_div_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # if st.checkbox('CCI Hidden'):
    #     st.dataframe(cci_hidden_bear_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

    # if st.checkbox('RSI Hidden'):
    #     st.dataframe(rsi_hidden_bear_signals.tail(10),
    #     width=1900, # 예시로 1500px 너비를 지정
    #     height=1000   # 높이는 90개 행을 보기에 적절한 값으로 설정 (선택 사항)
    #     )

else:
    st.warning("주식 데이터를 불러오지 못했습니다. 종목 코드 또는 기간을 확인해 주세요.")
    