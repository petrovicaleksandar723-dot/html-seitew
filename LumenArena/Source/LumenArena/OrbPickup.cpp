#include "OrbPickup.h"
#include "ArenaGameState.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "TimerManager.h"

AOrbPickup::AOrbPickup()
{
	PrimaryActorTick.bCanEverTick = true;

	Trigger = CreateDefaultSubobject<USphereComponent>(TEXT("Trigger"));
	SetRootComponent(Trigger);
	Trigger->InitSphereRadius(110.f);
	Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Trigger->SetGenerateOverlapEvents(true);

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(Trigger);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Mesh->SetRelativeScale3D(FVector(0.9f));

	// Engine basic sphere — always available, no content import needed.
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMesh.Succeeded())
	{
		Mesh->SetStaticMesh(SphereMesh.Object);
	}

	Glow = CreateDefaultSubobject<UPointLightComponent>(TEXT("Glow"));
	Glow->SetupAttachment(Trigger);
	Glow->SetIntensityUnits(ELightUnits::Candelas);
	Glow->SetIntensity(2200.f);
	Glow->SetAttenuationRadius(900.f);
	Glow->SetSourceRadius(30.f);
	Glow->SetCastShadows(false);
	Glow->SetLightColor(OrbColor);
}

void AOrbPickup::SetOrbColor(const FLinearColor& InColor)
{
	OrbColor = InColor;
	if (Glow)
	{
		Glow->SetLightColor(OrbColor);
	}
	if (DynMat)
	{
		DynMat->SetVectorParameterValue(TEXT("Color"), OrbColor);
		DynMat->SetVectorParameterValue(TEXT("BaseColor"), OrbColor);
	}
}

void AOrbPickup::BeginPlay()
{
	Super::BeginPlay();

	BaseZ = GetActorLocation().Z;
	Phase = FMath::FRandRange(0.f, 6.28318f);

	// Dynamic material so each orb can be tinted (params no-op safely if absent).
	if (Mesh && Mesh->GetMaterial(0))
	{
		DynMat = Mesh->CreateAndSetMaterialInstanceDynamic(0);
		if (DynMat)
		{
			DynMat->SetVectorParameterValue(TEXT("Color"), OrbColor);
			DynMat->SetVectorParameterValue(TEXT("BaseColor"), OrbColor);
		}
	}

	Trigger->OnComponentBeginOverlap.AddDynamic(this, &AOrbPickup::OnOverlapBegin);
}

void AOrbPickup::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Spin + bob for life.
	AddActorLocalRotation(FRotator(0.f, SpinSpeed * DeltaSeconds, 0.f));
	Phase += BobSpeed * DeltaSeconds;
	FVector Loc = GetActorLocation();
	Loc.Z = BaseZ + FMath::Sin(Phase) * BobHeight;
	SetActorLocation(Loc);

	// Subtle light pulse.
	if (Glow)
	{
		Glow->SetIntensity(2000.f + FMath::Sin(Phase * 2.f) * 600.f);
	}
}

void AOrbPickup::OnOverlapBegin(UPrimitiveComponent* /*OverlappedComp*/, AActor* OtherActor,
	UPrimitiveComponent* /*OtherComp*/, int32 /*OtherBodyIndex*/, bool /*bFromSweep*/, const FHitResult& /*Sweep*/)
{
	if (bCollected || !OtherActor || !OtherActor->IsA(APawn::StaticClass()))
	{
		return;
	}
	bCollected = true;

	if (AArenaGameState* GS = GetWorld() ? GetWorld()->GetGameState<AArenaGameState>() : nullptr)
	{
		GS->AddCollected();
	}

	// Quick collect flourish: bright flash, then destroy next frame.
	if (Glow)
	{
		Glow->SetIntensity(9000.f);
	}
	Trigger->SetGenerateOverlapEvents(false);

	FTimerHandle Handle;
	GetWorldTimerManager().SetTimer(Handle, [this]() { Destroy(); }, 0.12f, false);
}
