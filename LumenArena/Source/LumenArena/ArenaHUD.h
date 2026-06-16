#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "ArenaHUD.generated.h"

/**
 * Code-only HUD (no UMG assets required) drawing score, timer and objective.
 * (ue-ui-umg-slate: for a shipping UI you'd swap this for a UUserWidget / Common UI.)
 */
UCLASS()
class LUMENARENA_API AArenaHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;
};
