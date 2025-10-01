################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../ASW/drivecontrol/control.c 

COMPILED_SRCS += \
ASW/drivecontrol/control.src 

C_DEPS += \
ASW/drivecontrol/control.d 

OBJS += \
ASW/drivecontrol/control.o 


# Each subdirectory must supply rules for building sources it contributes
ASW/drivecontrol/control.src: ../ASW/drivecontrol/control.c ASW/drivecontrol/subdir.mk
	cctc -cs --dep-file="$(*F).d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/First_project/project_final/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
ASW/drivecontrol/control.o: ASW/drivecontrol/control.src ASW/drivecontrol/subdir.mk
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"

clean: clean-ASW-2f-drivecontrol

clean-ASW-2f-drivecontrol:
	-$(RM) ASW/drivecontrol/control.d ASW/drivecontrol/control.o ASW/drivecontrol/control.src

.PHONY: clean-ASW-2f-drivecontrol

