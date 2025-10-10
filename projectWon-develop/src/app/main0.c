#include "main0.h"

// 모터 상태를 저장하는 구조체 변수 선언 및 초기화
MotorState motorState = {.baseDuty = 50,      // 기본 주행 속도(Duty 비율), 사용자가 설정한 값 (0~100%)
        .currentDuty = 0,    // 현재 실제 적용 중인 Duty 값 (초기에는 정지)
        .currentDir = '5',   // 현재 주행 방향 (초기에는 정지)
        .prevDir = '5',      // 바로 직전 주행 방향 (초기에는 정지)
        .lastKeyInput = '5'  // 가장 마지막으로 입력된 키 (초기에는 정지)
        };

void main0 (void)
{
    systemInit();

    // 사용자 인증 절차 실행(암호 기반 시동)
    // authenticate();

    float distance_cm;

    while (1)
    {
        // 현재 상태에 따라 차량의 동작을 제어하는 상태 머신 처리
        // 사용자의 키 입력, 센서 값 등에 따라 상태를 변경하고 그에 맞는 행동 수행
        handleStateMachine(&motorState);
        diagnoseTofSensor();
        // ✨ 새로 만든 ultrasonic_getDistanceCm 함수를 호출
        distance_cm = ultrasonic_getDistanceCm(ULT_LEFT);

        if (distance_cm >= 0)
        {
            // 소수점 둘째 자리까지 출력
            myPrintf("Left Ultrasonic Distance: %.2f cm\n", distance_cm);
        }
        else
        {
            myPrintf("Left Ultrasonic Error or Timeout\n");
        }
        delayMs(100);
    }
}
