#include "LumenArenaCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
#include "Engine/LocalPlayer.h"

#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputModifiers.h"

ALumenArenaCharacter::ALumenArenaCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// Capsule
	GetCapsuleComponent()->InitCapsuleSize(42.f, 92.f);

	// Don't rotate the character with the controller; the movement component
	// orients it toward acceleration instead (classic third-person feel).
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Move = GetCharacterMovement();
	Move->bOrientRotationToMovement = true;
	Move->RotationRate = FRotator(0.f, 640.f, 0.f);
	Move->JumpZVelocity = 620.f;
	Move->AirControl = 0.6f;
	Move->MaxWalkSpeed = 620.f;
	Move->BrakingDecelerationWalking = 2000.f;
	Move->GroundFriction = 8.f;

	// Spring arm + camera
	SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
	SpringArm->SetupAttachment(GetRootComponent());
	SpringArm->TargetArmLength = 420.f;
	SpringArm->bUsePawnControlRotation = true;
	SpringArm->bEnableCameraLag = true;
	SpringArm->CameraLagSpeed = 10.f;
	SpringArm->SocketOffset = FVector(0.f, 0.f, 70.f);

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
	Camera->bUsePawnControlRotation = false;
	Camera->FieldOfView = 80.f;
}

void ALumenArenaCharacter::BuildInputActions()
{
	// --- Actions ---
	MoveAction = NewObject<UInputAction>(this, TEXT("IA_Move"));
	MoveAction->ValueType = EInputActionValueType::Axis2D;
	MoveAction->AccumulationBehavior = EInputActionAccumulationBehavior::Cumulative;

	LookAction = NewObject<UInputAction>(this, TEXT("IA_Look"));
	LookAction->ValueType = EInputActionValueType::Axis2D;

	JumpAction = NewObject<UInputAction>(this, TEXT("IA_Jump"));
	JumpAction->ValueType = EInputActionValueType::Boolean;

	DashAction = NewObject<UInputAction>(this, TEXT("IA_Dash"));
	DashAction->ValueType = EInputActionValueType::Boolean;

	// --- Mapping context ---
	MappingContext = NewObject<UInputMappingContext>(this, TEXT("IMC_Default"));

	// Move: WASD composed into a 2D axis (X = right, Y = forward).
	// W -> +Y (swizzle X into Y). S -> -Y. D -> +X. A -> -X.
	{
		FEnhancedActionKeyMapping& MW = MappingContext->MapKey(MoveAction, EKeys::W);
		UInputModifierSwizzleAxis* S = NewObject<UInputModifierSwizzleAxis>(MappingContext);
		S->Order = EInputAxisSwizzle::YXZ;
		MW.Modifiers.Add(S);
	}
	{
		FEnhancedActionKeyMapping& MS = MappingContext->MapKey(MoveAction, EKeys::S);
		UInputModifierSwizzleAxis* S = NewObject<UInputModifierSwizzleAxis>(MappingContext);
		S->Order = EInputAxisSwizzle::YXZ;
		MS.Modifiers.Add(S);
		MS.Modifiers.Add(NewObject<UInputModifierNegate>(MappingContext));
	}
	{
		MappingContext->MapKey(MoveAction, EKeys::D); // +X, no modifier
	}
	{
		FEnhancedActionKeyMapping& MA = MappingContext->MapKey(MoveAction, EKeys::A);
		MA.Modifiers.Add(NewObject<UInputModifierNegate>(MappingContext));
	}

	// Look: mouse delta (2D). Negate Y for standard (up = look up).
	{
		FEnhancedActionKeyMapping& ML = MappingContext->MapKey(LookAction, EKeys::Mouse2D);
		UInputModifierNegate* NegY = NewObject<UInputModifierNegate>(MappingContext);
		NegY->bX = false; NegY->bY = true; NegY->bZ = false;
		ML.Modifiers.Add(NegY);
	}

	// Jump + Dash
	MappingContext->MapKey(JumpAction, EKeys::SpaceBar);
	MappingContext->MapKey(DashAction, EKeys::LeftShift);
}

void ALumenArenaCharacter::BeginPlay()
{
	Super::BeginPlay();

	BuildInputActions();

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Sub =
			ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			Sub->AddMappingContext(MappingContext, 0);
		}
	}
}

void ALumenArenaCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (DashCooldown > 0.f)
	{
		DashCooldown = FMath::Max(0.f, DashCooldown - DeltaSeconds);
	}
}

void ALumenArenaCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!EIC)
	{
		return;
	}

	// Actions may not be built yet if input is set up before BeginPlay; ensure they exist.
	if (!MoveAction)
	{
		BuildInputActions();
	}

	EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ALumenArenaCharacter::Move);
	EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &ALumenArenaCharacter::Look);
	EIC->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
	EIC->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	EIC->BindAction(DashAction, ETriggerEvent::Started, this, &ALumenArenaCharacter::OnDash);
}

void ALumenArenaCharacter::Move(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	if (!Controller || Axis.IsNearlyZero())
	{
		return;
	}

	// Movement relative to camera yaw.
	const FRotator YawRot(0.f, Controller->GetControlRotation().Yaw, 0.f);
	const FVector Forward = FRotationMatrix(YawRot).GetUnitAxis(EAxis::X);
	const FVector Right = FRotationMatrix(YawRot).GetUnitAxis(EAxis::Y);

	AddMovementInput(Forward, Axis.Y);
	AddMovementInput(Right, Axis.X);
}

void ALumenArenaCharacter::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}

void ALumenArenaCharacter::OnDash()
{
	if (DashCooldown > 0.f)
	{
		return;
	}
	DashCooldown = 0.8f;

	FVector Dir = GetLastMovementInputVector();
	if (Dir.IsNearlyZero())
	{
		Dir = GetActorForwardVector();
	}
	Dir.Z = 0.f;
	Dir.Normalize();

	LaunchCharacter(Dir * DashImpulse + FVector(0, 0, 250.f), true, false);
}
