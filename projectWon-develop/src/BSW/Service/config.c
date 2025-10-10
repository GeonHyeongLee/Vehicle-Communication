// 파일명: config.c

#include "config.h"
// 나중에 DFlash 관련 헤더를 여기에 추가합니다.
//#include "IfxFlash.h"

// .h 파일에서 extern으로 선언했던 변수의 실체
SystemConfig g_config;

// 설정값을 초기화하는 함수 (부팅 시 1회 호출)
void config_init(void)
{
    // 나중에는 여기서 DFlash의 값을 읽어와 g_config를 채웁니다.

    // 지금은 우선 기본값으로 초기화합니다.
    g_config.isAebEnabled = true; // 기본값은 ON
}

// 주기적으로 호출될 관리 함수
void config_mainFunction(void)
{
    // 나중에는 여기에 'g_config에 변경이 생겼으면 DFlash에 저장'하는
    // 로직을 추가하게 됩니다.
}
