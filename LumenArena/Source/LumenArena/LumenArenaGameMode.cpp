#include "LumenArenaGameMode.h"

#include "LumenArenaCharacter.h"
#include "ArenaGameState.h"
#include "ArenaHUD.h"
#include "OrbPickup.h"

#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/DirectionalLight.h"
#include "Components/StaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"

ALumenArenaGameMode::ALumenArenaGameMode()
{
	DefaultPawnClass = ALumenArenaCharacter::StaticClass();
	GameStateClass = AArenaGameState::StaticClass();
	HUDClass = AArenaHUD::StaticClass();
}

void ALumenArenaGameMode::BeginPlay()
{
	Super::BeginPlay();
	BuildArena();
}

void ALumenArenaGameMode::BuildArena()
{
	SpawnFloor();
	SpawnLighting();
	SpawnOrbs();
	PlacePlayer();

	if (AArenaGameState* GS = GetGameState<AArenaGameState>())
	{
		GS->StartTime = GetWorld()->GetTimeSeconds();
	}
}

void ALumenArenaGameMode::SpawnFloor()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	AStaticMeshActor* Floor = World->SpawnActor<AStaticMeshActor>(FVector::ZeroVector, FRotator::ZeroRotator);
	if (!Floor)
	{
		return;
	}

	UStaticMeshComponent* Comp = Floor->GetStaticMeshComponent();
	static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(TEXT("/Engine/BasicShapes/Plane.Plane"));
	if (Comp && PlaneMesh.Succeeded())
	{
		// Mobility lives on the component; make it movable so we can scale it at runtime.
		Comp->SetMobility(EComponentMobility::Movable);
		Comp->SetStaticMesh(PlaneMesh.Object);
		// Engine plane is 100x100 uu; scale to a big arena floor.
		Floor->SetActorScale3D(FVector(ArenaRadius / 100.f * 2.2f, ArenaRadius / 100.f * 2.2f, 1.f));

		if (Comp->GetMaterial(0))
		{
			if (UMaterialInstanceDynamic* Mid = Comp->CreateAndSetMaterialInstanceDynamic(0))
			{
				const FLinearColor Dark(0.012f, 0.014f, 0.02f);
				Mid->SetVectorParameterValue(TEXT("Color"), Dark);
				Mid->SetVectorParameterValue(TEXT("BaseColor"), Dark);
			}
		}
	}
}

void ALumenArenaGameMode::SpawnLighting()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	// Moody low key light so the orb point-lights drive the Lumen GI look.
	ADirectionalLight* Key = World->SpawnActor<ADirectionalLight>(FVector(0, 0, 1500.f), FRotator(-48.f, 35.f, 0.f));
	if (Key)
	{
		if (UDirectionalLightComponent* DLC = Cast<UDirectionalLightComponent>(Key->GetLightComponent()))
		{
			DLC->SetMobility(EComponentMobility::Movable);
			DLC->SetIntensity(1.6f);                       // lux — deliberately dim
			DLC->SetLightColor(FLinearColor(0.55f, 0.68f, 1.0f));
			DLC->SetUseTemperature(true);
			DLC->SetTemperature(7200.f);
		}
	}
}

void ALumenArenaGameMode::SpawnOrbs()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const FLinearColor Palette[] = {
		FLinearColor(0.13f, 0.55f, 1.0f),   // blue
		FLinearColor(0.65f, 0.40f, 1.0f),   // violet
		FLinearColor(0.10f, 0.90f, 0.85f),  // cyan
		FLinearColor(1.0f, 0.40f, 0.72f),   // pink
		FLinearColor(1.0f, 0.78f, 0.25f),   // gold
	};
	const int32 PaletteNum = UE_ARRAY_COUNT(Palette);

	int32 Spawned = 0;
	for (int32 i = 0; i < OrbCount; ++i)
	{
		const float T = (float)i / (float)FMath::Max(1, OrbCount);
		const float Angle = T * 2.f * PI + FMath::FRandRange(-0.18f, 0.18f);
		const float R = FMath::FRandRange(ArenaRadius * 0.35f, ArenaRadius * 0.95f);
		const FVector Loc(FMath::Cos(Angle) * R, FMath::Sin(Angle) * R, 120.f + FMath::FRandRange(0.f, 160.f));

		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		AOrbPickup* Orb = World->SpawnActor<AOrbPickup>(Loc, FRotator::ZeroRotator, Params);
		if (Orb)
		{
			Orb->SetOrbColor(Palette[i % PaletteNum]);
			++Spawned;
		}
	}

	if (AArenaGameState* GS = GetGameState<AArenaGameState>())
	{
		GS->Total = Spawned;
		GS->Collected = 0;
		GS->bFinished = false;
	}
}

void ALumenArenaGameMode::PlacePlayer()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	if (APlayerController* PC = World->GetFirstPlayerController())
	{
		if (APawn* Pawn = PC->GetPawn())
		{
			Pawn->TeleportTo(FVector(0.f, 0.f, 140.f), FRotator::ZeroRotator);
		}
	}
}
