################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
"../app/main0.c" \
"../app/systeminit.c" 

COMPILED_SRCS += \
"app/main0.src" \
"app/systeminit.src" 

C_DEPS += \
"./app/main0.d" \
"./app/systeminit.d" 

OBJS += \
"app/main0.o" \
"app/systeminit.o" 


# Each subdirectory must supply rules for building sources it contributes
"app/main0.src":"../app/main0.c" "app/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"app/main0.o":"app/main0.src" "app/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"
"app/systeminit.src":"../app/systeminit.c" "app/subdir.mk"
	cctc -cs --dep-file="$*.d" --misrac-version=2004 -D__CPU__=tc37x "-fC:/Second_project/second_project/second_project_git/projectWon-develop/src/TriCore Debug (TASKING)/TASKING_C_C___Compiler-Include_paths__-I_.opt" --iso=99 --c++14 --language=+volatile --exceptions --anachronisms --fp-model=3 -O0 --tradeoff=4 --compact-max-size=200 -g -Wc-w544 -Wc-w557 -Ctc37x -Y0 -N0 -Z0 -o "$@" "$<"
"app/systeminit.o":"app/systeminit.src" "app/subdir.mk"
	astc -Og -Os --no-warnings= --error-limit=42 -o  "$@" "$<"

clean: clean-app

clean-app:
	-$(RM) ./app/main0.d ./app/main0.o ./app/main0.src ./app/systeminit.d ./app/systeminit.o ./app/systeminit.src

.PHONY: clean-app

