#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "LumenArenaGameMode.generated.h"

/**
 * GameMode that procedurally builds the whole playable arena at BeginPlay:
 * floor, cinematic key light, and a ring of glowing collectible orbs.
 * Drop into ANY empty level and press Play.
 * (ue-gameplay-framework + a touch of ue-procedural-generation for layout.)
 */
UCLASS()
class LUMENARENA_API ALumenArenaGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ALumenArenaGameMode();

protected:
	virtual void BeginPlay() override;

	void BuildArena();
	void SpawnFloor();
	void SpawnLighting();
	void SpawnOrbs();
	void PlacePlayer();

	UPROPERTY(EditDefaultsOnly, Category = "Arena")
	int32 OrbCount = 12;

	UPROPERTY(EditDefaultsOnly, Category = "Arena")
	float ArenaRadius = 2200.f;
};
