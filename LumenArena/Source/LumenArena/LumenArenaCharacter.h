#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "LumenArenaCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UInputMappingContext;
class UInputAction;
struct FInputActionValue;

/**
 * Third-person cinematic character. Enhanced Input is created entirely in C++
 * at runtime (no .uasset authoring needed), following the ue-input-system patterns.
 */
UCLASS()
class LUMENARENA_API ALumenArenaCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ALumenArenaCharacter();

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);

	/** Build the mapping context + actions in code (WASD/mouse/space/dash). */
	void BuildInputActions();

	void OnDash();

protected:
	UPROPERTY(VisibleAnywhere, Category = "Camera")
	TObjectPtr<USpringArmComponent> SpringArm;

	UPROPERTY(VisibleAnywhere, Category = "Camera")
	TObjectPtr<UCameraComponent> Camera;

	// Runtime-created Enhanced Input objects.
	UPROPERTY(Transient)
	TObjectPtr<UInputMappingContext> MappingContext;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> MoveAction;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> LookAction;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> JumpAction;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> DashAction;

	UPROPERTY(EditAnywhere, Category = "Movement")
	float DashImpulse = 1500.f;

	float DashCooldown = 0.f;
};
