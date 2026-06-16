#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "ArenaGameState.generated.h"

/**
 * Holds the score for the orb-collection mini-game.
 * (ue-gameplay-framework: GameState carries shared, replicated-ready match data.)
 */
UCLASS()
class LUMENARENA_API AArenaGameState : public AGameStateBase
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadOnly, Category = "Arena")
	int32 Collected = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Arena")
	int32 Total = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Arena")
	float StartTime = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Arena")
	bool bFinished = false;

	void AddCollected();

	float GetElapsedSeconds() const;
};
