import argparse
import alone_analysis_kospi
import alone_analysis_kosdaq
import alone_analysis_nasdaq
import alone_analysis_nyse

def main():
    # 1. 인자 파서 설정
    parser = argparse.ArgumentParser(description="시장 분석 시트 생성 프로그램")
    
    # 2. 인자 추가 (기본값을 기존 날짜로 설정하거나 필수 입력으로 변경 가능)
    parser.add_argument('--start', type=str, default="2025-11-01", help="시작 날짜 (YYYY-MM-DD)")
    parser.add_argument('--end', type=str, default="2026-03-11", help="종료 날짜 (YYYY-MM-DD)")
    
    # 3. 인자 파싱
    args = parser.parse_args()
    
    start_date = args.start
    end_date = args.end

    print(f"🚀 분석 시작: {start_date} ~ {end_date}")

    # 4. 각 마켓별 분석 실행
    alone_analysis_kospi.MakeSheet(start=start_date, end=end_date, market_name='KOSPI')
    alone_analysis_kosdaq.MakeSheet(start=start_date, end=end_date, market_name='KOSDAQ')
    alone_analysis_nasdaq.MakeSheet(start=start_date, end=end_date, market_name='NASDAQ')
    alone_analysis_nyse.MakeSheet(start=start_date, end=end_date, market_name='NYSE')

    print("✅ 모든 시트 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()