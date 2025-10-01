################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../ASW/emergencystop/aeb.c 

COMPILED_SRCS += \
ASW/emergencystop/aeb.src 

C_DEPS += \
ASW/emergencystop/aeb.d 

OBJS += \
ASW/emergencystop/aeb.o 


# Each subdirectory must supply rules for building sources it contributes
ASW/emergencystop/aeb.src: ../ASW/emergencystop/aeb.c ASW/emergencystop/subdir.mk
	cctc -cs --dep-file="$(*F).d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/First_project/project_final/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
ASW/emergencystop/aeb.o: ASW/emergencystop/aeb.src ASW/emergencystop/subdir.mk
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"

clean: clean-ASW-2f-emergencystop

clean-ASW-2f-emergencystop:
	-$(RM) ASW/emergencystop/aeb.d ASW/emergencystop/aeb.o ASW/emergencystop/aeb.src

.PHONY: clean-ASW-2f-emergencystop

