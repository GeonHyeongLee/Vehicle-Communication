# Vehicle-Communication
차량 통신 프로젝트 담당 : 진단 통신 -> UDS, DoIP, CAN TP

## 1. End-to-End 진단 통신 시스템 구축 완료
PC의 GUI에서 시작된 명령이 이더넷(DoIP)과 CAN 버스를 모두 거쳐 TC375 ECU를 제어하고, 그 응답이 다시 PC 화면에 표시되기까지의 전체 통신 경로(End-to-End Data Flow)를 설계
PC ↔ 라즈베리파이: DoIP 프로토콜을 사용한 이더넷 통신 구현

라즈베리파이: DoIP와 CAN-UDS를 양방향으로 번역하는 게이트웨이 역할 설정

라즈베리파이 ↔ TC375: UDS on CAN (ISO-TP) 통신 구현

## 2. ECU(TC375)의 지능화: UDS 서버 핵심 기능 구현
TC375를 단순한 제어기에서, 외부의 진단 요청에 응답하고 스스로 상태를 보고할 수 있는 ECU로 발전

CAN TP 구현: 7바이트 이하의 데이터는 SF, 7바이트를 초과하는 긴 응답은 다중 프레임(FF/CF/FC)으로 자동 분할하여 전송하는 기능을 구현

### 핵심 UDS 서비스 구현:

SID 0x10 (Session Control) : Session을 Default, Extended 세션으로 나누어 핵심 기능(0x2E, 0x31)은 Extended Session에서만 실행 가능하도록 구현

SID 0x19 (Read DTC): ECU가 스스로 고장을 진단하고 그 결과를 진단기에게 알려주는 핵심적인 자가 진단 기능을 구현

SID 0x22 (Read Data): 실시간 센서 값(ToF, 초음파)과 고정된 ECU 정보(부품 번호, 시리얼 번호 등)를 DID 기반으로 읽어오는 기능을 완성

SID 0x2A (Periodic Read Data) : Tof, 초음파 센서의 값을 0.5초 간격으로 실시간으로 읽어올 수 있도록 구현

SID 0x2E (Write Data): 원격으로 ECU의 기능(AEB On/Off)을 제어하는 기능 플래그(Feature Flag) 쓰기 기능을 구현하여 간단한 형태의 OTA 기반 마련

SID 0x31 (Routine Control) : 모터 강제 구동 기능을 구현하여 모터 진단이 가능하도록 구현


### DTC 자가 진단 시스템 구축:

DTC 관리 모듈(dtc.c, dtc.h)을 설계하고 구현했습니다.

센서의 물리적 연결 해제(통신 타임아웃) 및 측정값 범위 초과와 같은 실제 고장 조건을 정의하고, 이를 감지하여 DTC를 설정하는 로직을 완성했습니다.

## 3. 사용자 친화적 진단 툴(PC) 개발
명령줄 인터페이스를 넘어, 누구나 쉽게 사용할 수 있는 GUI 기반의 PC용 진단 애플리케이션을 개발했습니다.

DoIP 클라이언트 구현: 파이썬 socket을 이용하여 DoIP 패킷을 생성하고 라즈베리파이 게이트웨이와 통신하는 클라이언트 로직을 완성했습니다.

직관적인 GUI: 파이썬 tkinter를 사용하여 각 UDS 기능을 버튼으로 만들고, ECU로부터 받은 응답(센서 값, DTC 목록, 제어 결과 등)을 사용자가 이해하기 쉬운 형태로 화면에 표시하는 인터페이스를 구현했습니다.
