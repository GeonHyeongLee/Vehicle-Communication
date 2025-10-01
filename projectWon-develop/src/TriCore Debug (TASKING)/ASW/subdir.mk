################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../ASW/buzzer.c \
../ASW/fsm.c \
../ASW/led.c 

COMPILED_SRCS += \
ASW/buzzer.src \
ASW/fsm.src \
ASW/led.src 

C_DEPS += \
ASW/buzzer.d \
ASW/fsm.d \
ASW/led.d 

OBJS += \
ASW/buzzer.o \
ASW/fsm.o \
ASW/led.o 


# Each subdirectory must supply rules for building sources it contributes
ASW/buzzer.src: ../ASW/buzzer.c ASW/subdir.mk
	cctc -cs --dep-file="$(*F).d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/First_project/project_final/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
ASW/buzzer.o: ASW/buzzer.src ASW/subdir.mk
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
ASW/fsm.src: ../ASW/fsm.c ASW/subdir.mk
	cctc -cs --dep-file="$(*F).d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/First_project/project_final/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
ASW/fsm.o: ASW/fsm.src ASW/subdir.mk
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
ASW/led.src: ../ASW/led.c ASW/subdir.mk
	cctc -cs --dep-file="$(*F).d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/First_project/project_final/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
ASW/led.o: ASW/led.src ASW/subdir.mk
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"

clean: clean-ASW

clean-ASW:
	-$(RM) ASW/buzzer.d ASW/buzzer.o ASW/buzzer.src ASW/fsm.d ASW/fsm.o ASW/fsm.src ASW/led.d ASW/led.o ASW/led.src

.PHONY: clean-ASW

