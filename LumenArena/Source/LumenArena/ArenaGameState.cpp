#include "ArenaGameState.h"
#include "Engine/World.h"

void AArenaGameState::AddCollected()
{
	Collected = FMath::Min(Collected + 1, Total);
	if (Collected >= Total && Total > 0)
	{
		bFinished = true;
	}
}

float AArenaGameState::GetElapsedSeconds() const
{
	if (!GetWorld())
	{
		return 0.f;
	}
	const float Now = GetWorld()->GetTimeSeconds();
	return FMath::Max(0.f, Now - StartTime);
}
