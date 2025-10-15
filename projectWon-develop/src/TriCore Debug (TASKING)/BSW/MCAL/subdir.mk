################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
"../BSW/MCAL/asclin0.c" \
"../BSW/MCAL/asclin1.c" \
"../BSW/MCAL/can.c" \
"../BSW/MCAL/eru.c" \
"../BSW/MCAL/gpt12.c" \
"../BSW/MCAL/gtm_atom_pwm.c" \
"../BSW/MCAL/port.c" \
"../BSW/MCAL/stm.c" 

COMPILED_SRCS += \
"BSW/MCAL/asclin0.src" \
"BSW/MCAL/asclin1.src" \
"BSW/MCAL/can.src" \
"BSW/MCAL/eru.src" \
"BSW/MCAL/gpt12.src" \
"BSW/MCAL/gtm_atom_pwm.src" \
"BSW/MCAL/port.src" \
"BSW/MCAL/stm.src" 

C_DEPS += \
"./BSW/MCAL/asclin0.d" \
"./BSW/MCAL/asclin1.d" \
"./BSW/MCAL/can.d" \
"./BSW/MCAL/eru.d" \
"./BSW/MCAL/gpt12.d" \
"./BSW/MCAL/gtm_atom_pwm.d" \
"./BSW/MCAL/port.d" \
"./BSW/MCAL/stm.d" 

OBJS += \
"BSW/MCAL/asclin0.o" \
"BSW/MCAL/asclin1.o" \
"BSW/MCAL/can.o" \
"BSW/MCAL/eru.o" \
"BSW/MCAL/gpt12.o" \
"BSW/MCAL/gtm_atom_pwm.o" \
"BSW/MCAL/port.o" \
"BSW/MCAL/stm.o" 


# Each subdirectory must supply rules for building sources it contributes
"BSW/MCAL/asclin0.src":"../BSW/MCAL/asclin0.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/asclin0.o":"BSW/MCAL/asclin0.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/asclin1.src":"../BSW/MCAL/asclin1.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/asclin1.o":"BSW/MCAL/asclin1.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/can.src":"../BSW/MCAL/can.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/can.o":"BSW/MCAL/can.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/eru.src":"../BSW/MCAL/eru.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/eru.o":"BSW/MCAL/eru.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/gpt12.src":"../BSW/MCAL/gpt12.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/gpt12.o":"BSW/MCAL/gpt12.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/gtm_atom_pwm.src":"../BSW/MCAL/gtm_atom_pwm.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/gtm_atom_pwm.o":"BSW/MCAL/gtm_atom_pwm.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/port.src":"../BSW/MCAL/port.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/port.o":"BSW/MCAL/port.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"BSW/MCAL/stm.src":"../BSW/MCAL/stm.c" "BSW/MCAL/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"BSW/MCAL/stm.o":"BSW/MCAL/stm.src" "BSW/MCAL/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"

clean: clean-BSW-2f-MCAL

clean-BSW-2f-MCAL:
	-$(RM) ./BSW/MCAL/asclin0.d ./BSW/MCAL/asclin0.o ./BSW/MCAL/asclin0.src ./BSW/MCAL/asclin1.d ./BSW/MCAL/asclin1.o ./BSW/MCAL/asclin1.src ./BSW/MCAL/can.d ./BSW/MCAL/can.o ./BSW/MCAL/can.src ./BSW/MCAL/eru.d ./BSW/MCAL/eru.o ./BSW/MCAL/eru.src ./BSW/MCAL/gpt12.d ./BSW/MCAL/gpt12.o ./BSW/MCAL/gpt12.src ./BSW/MCAL/gtm_atom_pwm.d ./BSW/MCAL/gtm_atom_pwm.o ./BSW/MCAL/gtm_atom_pwm.src ./BSW/MCAL/port.d ./BSW/MCAL/port.o ./BSW/MCAL/port.src ./BSW/MCAL/stm.d ./BSW/MCAL/stm.o ./BSW/MCAL/stm.src

.PHONY: clean-BSW-2f-MCAL

