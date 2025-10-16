################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
"../BSW/Service/battery.c" \
"../BSW/Service/bluetooth.c" \
"../BSW/Service/buzzerport.c" \
"../BSW/Service/config.c" \
"../BSW/Service/dtc.c" \
"../BSW/Service/ledport.c" \
"../BSW/Service/motor.c" \
"../BSW/Service/routine_control.c" \
"../BSW/Service/session.c" \
"../BSW/Service/tof.c" \
"../BSW/Service/uart.c" \
"../BSW/Service/ultrasonic.c" \
"../BSW/Service/util.c" 

COMPILED_SRCS += \
"BSW/Service/battery.src" \
"BSW/Service/bluetooth.src" \
"BSW/Service/buzzerport.src" \
"BSW/Service/config.src" \
"BSW/Service/dtc.src" \
"BSW/Service/ledport.src" \
"BSW/Service/motor.src" \
"BSW/Service/routine_control.src" \
"BSW/Service/session.src" \
"BSW/Service/tof.src" \
"BSW/Service/uart.src" \
"BSW/Service/ultrasonic.src" \
"BSW/Service/util.src" 

C_DEPS += \
"./BSW/Service/battery.d" \
"./BSW/Service/bluetooth.d" \
"./BSW/Service/buzzerport.d" \
"./BSW/Service/config.d" \
"./BSW/Service/dtc.d" \
"./BSW/Service/ledport.d" \
"./BSW/Service/motor.d" \
"./BSW/Service/routine_control.d" \
"./BSW/Service/session.d" \
"./BSW/Service/tof.d" \
"./BSW/Service/uart.d" \
"./BSW/Service/ultrasonic.d" \
"./BSW/Service/util.d" 

OBJS += \
"BSW/Service/battery.o" \
"BSW/Service/bluetooth.o" \
"BSW/Service/buzzerport.o" \
"BSW/Service/config.o" \
"BSW/Service/dtc.o" \
"BSW/Service/ledport.o" \
"BSW/Service/motor.o" \
"BSW/Service/routine_control.o" \
"BSW/Service/session.o" \
"BSW/Service/tof.o" \
"BSW/Service/uart.o" \
"BSW/Service/ultrasonic.o" \
"BSW/Service/util.o" 


# Each subdirectory must supply rules for building sources it contributes
"BSW/Service/battery.src":"../BSW/Service/battery.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/battery.o":"BSW/Service/battery.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/bluetooth.src":"../BSW/Service/bluetooth.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/bluetooth.o":"BSW/Service/bluetooth.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/buzzerport.src":"../BSW/Service/buzzerport.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/buzzerport.o":"BSW/Service/buzzerport.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/config.src":"../BSW/Service/config.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/config.o":"BSW/Service/config.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/dtc.src":"../BSW/Service/dtc.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/dtc.o":"BSW/Service/dtc.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/ledport.src":"../BSW/Service/ledport.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/ledport.o":"BSW/Service/ledport.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/motor.src":"../BSW/Service/motor.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/motor.o":"BSW/Service/motor.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/routine_control.src":"../BSW/Service/routine_control.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/routine_control.o":"BSW/Service/routine_control.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/session.src":"../BSW/Service/session.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/session.o":"BSW/Service/session.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/tof.src":"../BSW/Service/tof.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/tof.o":"BSW/Service/tof.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/uart.src":"../BSW/Service/uart.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/uart.o":"BSW/Service/uart.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/ultrasonic.src":"../BSW/Service/ultrasonic.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/ultrasonic.o":"BSW/Service/ultrasonic.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/Service/util.src":"../BSW/Service/util.c" "BSW/Service/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/Service/util.o":"BSW/Service/util.src" "BSW/Service/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"

clean: clean-BSW-2f-Service

clean-BSW-2f-Service:
	-$(RM) ./BSW/Service/battery.d ./BSW/Service/battery.o ./BSW/Service/battery.src ./BSW/Service/bluetooth.d ./BSW/Service/bluetooth.o ./BSW/Service/bluetooth.src ./BSW/Service/buzzerport.d ./BSW/Service/buzzerport.o ./BSW/Service/buzzerport.src ./BSW/Service/config.d ./BSW/Service/config.o ./BSW/Service/config.src ./BSW/Service/dtc.d ./BSW/Service/dtc.o ./BSW/Service/dtc.src ./BSW/Service/ledport.d ./BSW/Service/ledport.o ./BSW/Service/ledport.src ./BSW/Service/motor.d ./BSW/Service/motor.o ./BSW/Service/motor.src ./BSW/Service/routine_control.d ./BSW/Service/routine_control.o ./BSW/Service/routine_control.src ./BSW/Service/session.d ./BSW/Service/session.o ./BSW/Service/session.src ./BSW/Service/tof.d ./BSW/Service/tof.o ./BSW/Service/tof.src ./BSW/Service/uart.d ./BSW/Service/uart.o ./BSW/Service/uart.src ./BSW/Service/ultrasonic.d ./BSW/Service/ultrasonic.o ./BSW/Service/ultrasonic.src ./BSW/Service/util.d ./BSW/Service/util.o ./BSW/Service/util.src

.PHONY: clean-BSW-2f-Service

