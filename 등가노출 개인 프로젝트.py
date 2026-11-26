# 등가노출(EV) 계산기 - 컴퓨팅기반문제해결 수업 개념 적용 버전

# 표준 1스톱 기준값(튜플·리스트 자료구조 활용)
SHUTTER_SPEEDS = [
    "1/4000", "1/2000", "1/1000", "1/500", "1/250",
    "1/125", "1/60", "1/30", "1/15", "1/8",
    "1/4", "1/2", "1", "2"
]
APERTURES = [1.4, 2.0, 2.8, 4.0, 5.6, 8.0, 11.0, 16.0, 22.0]
ISOS = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800]


def parse_shutter_to_float(shutter_str):
    """'1/250' 또는 '2' 같은 셔터스피드 문자열을 초(float) 단위로 변환한다."""
    text = shutter_str.strip()
    if "/" in text:
        parts = text.split("/")
        if len(parts) != 2:
            raise ValueError("셔터스피드 형식이 올바르지 않습니다.")
        numerator = float(parts[0])
        denominator = float(parts[1])
        if numerator <= 0 or denominator <= 0:
            raise ValueError("양수만 입력할 수 있습니다.")
        return numerator / denominator
    else:
        seconds = float(text)
        if seconds <= 0:
            raise ValueError("양수만 입력할 수 있습니다.")
        return seconds


def calc_shutter_stops(old_shutter_str, new_shutter_str):
    """
    셔터스피드 변경에 따른 스톱 변화량을 계산한다.
    반환값: (스톱 변화량, 노출 변화 방향 설명)
    - 양수(+): 빛의 양이 늘어남(셔터가 느려짐)
    - 음수(-): 빛의 양이 줄어듦(셔터가 빨라짐)
    """
    old_sec = parse_shutter_to_float(old_shutter_str)
    new_sec = parse_shutter_to_float(new_shutter_str)

    # 노출 시간(초)이 2배가 되면 +1스톱, 1/2배가 되면 -1스톱
    ratio = new_sec / old_sec
    # 2의 거듭제곱 스톱 계산 (로그 없이 반복/곱셈으로 직관적 계산)
    stops = 0.0
    if ratio >= 1.0:
        current = 1.0
        while current * 2.0 <= ratio + 1e-9:
            current *= 2.0
            stops += 1.0
        if ratio > current + 1e-9:
            # 1스톱 미만 비율 근사
            stops += (ratio - current) / current
    else:
        current = 1.0
        while current / 2.0 >= ratio - 1e-9:
            current /= 2.0
            stops -= 1.0
        if ratio < current - 1e-9:
            stops -= (current - ratio) / current

    return round(stops, 1)


def find_closest_value(values, target):
    """리스트에서 target과 가장 가까운 표준 값을 찾는다."""
    best_val = values[0]
    min_diff = abs(values[0] - target)
    for val in values:
        diff = abs(val - target)
        if diff < min_diff:
            min_diff = diff
            best_val = val
    return best_val


def calc_equivalent_aperture(current_f, light_stop_change):
    """
    빛의 양 변화(light_stop_change)를 상쇄할 등가 조리개(f값)를 계산한다.
    셔터로 빛이 +1스톱 늘어나면, 조리개는 -1스톱 줄여야(f값 커져야) 같은 노출이 된다.
    f값 1스톱 변화는 면적 2배(반지름 sqrt(2)배)이므로, f_new = f_old * (2 ** (-delta_stops / 2))
    """
    needed_aperture_stops = -light_stop_change
    raw_f = current_f * (2.0 ** (needed_aperture_stops / 2.0))
    nearest_f = find_closest_value(APERTURES, raw_f)
    return round(raw_f, 1), nearest_f


def calc_equivalent_iso(current_iso, light_stop_change):
    """
    빛의 양 변화(light_stop_change)를 상쇄할 등가 ISO를 계산한다.
    셔터로 빛이 +1스톱 늘어나면, ISO는 -1스톱 줄여야(절반으로) 같은 노출이 된다.
    """
    needed_iso_stops = -light_stop_change
    raw_iso = current_iso * (2.0 ** needed_iso_stops)
    nearest_iso = find_closest_value(ISOS, raw_iso)
    return round(raw_iso, 1), nearest_iso


def get_shooting_tip(aperture, iso, shutter_str):
    """촬영 세팅에 따른 간단한 현장 팁을 반환한다."""
    tips = []
    if iso >= 3200:
        tips.append("ISO가 높은 편이므로 암부 노이즈 발생 가능성을 확인하세요.")
    elif iso <= 100:
        tips.append("저감도(ISO 100 이하) 세팅으로 디테일과 다이내믹레인지에 유리합니다.")

    if aperture <= 2.8:
        tips.append("개방에 가까운 조리개로 피사계 심도가 얕아집니다. 초점 정확도를 신경 쓰세요.")
    elif aperture >= 11.0:
        tips.append("조리개를 많이 조인 상태이므로 삼각대 사용이나 셔터스피드 확보를 권장합니다.")

    if not tips:
        tips.append("균형 잡힌 기본 노출 세팅입니다. 히스토그램으로 하이라이트 클리핑을 확인하세요.")
    return tips


def save_result_to_txt(lines, filename="ev_result.txt"):
    """계산 결과를 텍스트 파일로 저장한다."""
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def run_ev_calculator():
    print("=== 등가노출(EV) 계산기 ===")
    print("표준 셔터스피드 예시:", ", ".join(SHUTTER_SPEEDS[2:10]))
    print("표준 조리개 예시:", APERTURES)
    print("표준 ISO 예시:", ISOS)

    while True:
        print("\n[메뉴]")
        print("1. 셔터스피드 변경 -> 등가 조리개 / 등가 ISO 계산")
        print("0. 종료")
        choice = input("메뉴를 선택하세요: ").strip()

        if choice == "0":
            print("등가노출 계산기를 종료합니다.")
            break
        elif choice != "1":
            print("0 또는 1만 입력해 주세요.")
            continue

        try:
            old_shutter = input("기존 셔터스피드 (예: 1/60): ").strip()
            new_shutter = input("변경할 셔터스피드 (예: 1/250): ").strip()
            current_f = float(input("현재 조리개 f값 (예: 4.0): ").strip())
            current_iso = int(input("현재 ISO (예: 400): ").strip())

            if current_f <= 0 or current_iso <= 0:
                print("조리개와 ISO는 0보다 큰 값이어야 합니다.")
                continue

            stop_change = calc_shutter_stops(old_shutter, new_shutter)
            raw_f, near_f = calc_equivalent_aperture(current_f, stop_change)
            raw_iso, near_iso = calc_equivalent_iso(current_iso, stop_change)

            result_lines = [
                "--- 등가노출(EV) 계산 결과 ---",
                f"기존 세팅: {old_shutter}s, f/{current_f:.1f}, ISO {current_iso}",
                f"변경 셔터스피드: {new_shutter}s (노출 변화량: {stop_change:+.1f} stop)",
                f"[대안 1 - 조리개 보정] 계산값 f/{raw_f:.1f} -> 가장 가까운 표준 f/{near_f:.1f}",
                f"[대안 2 - ISO 보정] 계산값 ISO {raw_iso:.1f} -> 가장 가까운 표준 ISO {near_iso}"
            ]

            print()
            for line in result_lines:
                print(line)

            print("\n[대안 1 기준 촬영 팁]")
            for tip in get_shooting_tip(near_f, current_iso, new_shutter):
                print("-", tip)

            print("\n[대안 2 기준 촬영 팁]")
            for tip in get_shooting_tip(current_f, near_iso, new_shutter):
                print("-", tip)

            save_ans = input("\n결과를 ev_result.txt로 저장할까요? (y/n): ").strip().lower()
            if save_ans == "y":
                save_result_to_txt(result_lines)
                print("ev_result.txt 파일로 저장되었습니다.")

        except ValueError as e:
            print(f"입력 오류: {e} (숫자 또는 1/250 같은 형식을 정확히 입력해 주세요.)")
        except ZeroDivisionError:
            print("0으로 나눌 수 없습니다. 입력값을 확인해 주세요.")


if __name__ == "__main__":
    run_ev_calculator()