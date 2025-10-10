// 파일명: config.h

#ifndef CONFIG_H_
#define CONFIG_H_

#include <stdbool.h>

// 시스템의 모든 설정값을 모아둘 구조체
typedef struct {
    bool isAebEnabled;
    // 나중에 자율주차 기능 플래그, 최고 속도 제한 등
    // 다른 설정값들을 여기에 계속 추가할 수 있습니다
} SystemConfig;

// '설정값 변수가 있다'고 외부에 알리는 선언 (extern)
// 실제 변수는 .c 파일에 있습니다.
extern SystemConfig g_config;

// 설정값을 초기화하는 함수 선언
void config_init(void);

// 설정값을 주기적으로 관리하는 함수 선언 (DFlash 저장 등)
void config_mainFunction(void);

#endif /* CONFIG_H_ */
